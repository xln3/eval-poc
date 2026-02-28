"""异步评测执行器 — 支持任务级并行 + JSON 持久化 + 任务重试"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from ..config import RUN_EVAL_SCRIPT, PROJECT_ROOT, DATA_DIR, JOBS_JSON
from ..models.schemas import (
    EvalJob, EvalJobCreate, EvalStatus, EvalTaskProgress, TaskStatus,
)
from .catalog_service import get_all_benchmarks, get_task_display_name
from .model_store import get_model, get_model_by_model_id

logger = logging.getLogger(__name__)

# ---- Task retry & timeout configuration ----
MAX_TASK_RETRIES = int(os.environ.get("EVAL_MAX_TASK_RETRIES", "5"))
# Per-task timeout in seconds (default 30 minutes)
TASK_TIMEOUT_SECONDS = int(os.environ.get("EVAL_TASK_TIMEOUT", "1800"))


def _classify_error(error_msg: str) -> str:
    """Classify error message into a human-readable failure reason."""
    lower = error_msg.lower()

    # Auth failures
    if any(kw in lower for kw in ["401", "unauthorized", "authentication", "auth fail",
                                   "invalid api key", "invalid_api_key", "api key"]):
        return "AUTH_FAILURE"
    if any(kw in lower for kw in ["403", "forbidden", "access denied", "permission denied"]):
        return "ACCESS_DENIED"

    # Rate limiting
    if any(kw in lower for kw in ["429", "rate limit", "rate_limit", "too many requests",
                                   "quota exceeded", "quota_exceeded"]):
        return "RATE_LIMITED"

    # Model / endpoint not found
    if any(kw in lower for kw in ["404", "model not found", "model_not_found",
                                   "not found", "no such model"]):
        return "MODEL_NOT_FOUND"

    # Connection errors
    if any(kw in lower for kw in ["connection refused", "connectionrefused",
                                   "connect timeout", "connection reset",
                                   "name resolution", "dns", "ssl",
                                   "connectionerror", "connection error"]):
        return "CONNECTION_ERROR"

    # Timeout
    if any(kw in lower for kw in ["timeout", "timed out", "deadline exceeded"]):
        return "TIMEOUT"

    # Out of memory / resource
    if any(kw in lower for kw in ["out of memory", "oom", "resource exhausted",
                                   "insufficient", "cuda out of memory"]):
        return "RESOURCE_EXHAUSTED"

    # Content filter / safety
    if any(kw in lower for kw in ["content filter", "content_filter", "safety filter",
                                   "blocked by", "content policy"]):
        return "CONTENT_FILTERED"

    return "UNKNOWN_ERROR"


_ERROR_LABELS = {
    "AUTH_FAILURE": "模型认证失败 (API Key 无效或过期)",
    "ACCESS_DENIED": "访问被拒绝 (权限不足)",
    "RATE_LIMITED": "API 速率限制 (请求过于频繁)",
    "MODEL_NOT_FOUND": "模型未找到 (模型 ID 或 endpoint 错误)",
    "CONNECTION_ERROR": "网络连接失败 (无法连接到模型 API)",
    "TIMEOUT": "任务执行超时",
    "RESOURCE_EXHAUSTED": "资源不足 (内存/GPU 耗尽)",
    "CONTENT_FILTERED": "内容安全过滤 (模型拒绝响应)",
    "UNKNOWN_ERROR": "未知错误",
}


# ---- Job persistence (following model_store.py pattern) ----

def _load_jobs() -> Dict[str, EvalJob]:
    """Load persisted jobs from JSON on startup."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not JOBS_JSON.exists():
        return {}
    try:
        with open(JOBS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        jobs = {}
        for item in data:
            job = EvalJob(**item)
            # Mark stale RUNNING/PENDING jobs as FAILED (crashed before completion)
            if job.status in (EvalStatus.PENDING, EvalStatus.RUNNING):
                job.status = EvalStatus.FAILED
                job.error = "Service restarted while job was running"
                if not job.completed_at:
                    job.completed_at = datetime.now(timezone.utc).isoformat()
            jobs[job.id] = job
        logger.info("Loaded %d persisted jobs from %s", len(jobs), JOBS_JSON)
        return jobs
    except Exception as e:
        logger.warning("Failed to load jobs from %s: %s", JOBS_JSON, e)
        return {}


def _save_jobs():
    """Persist current jobs dict to JSON file."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = [job.model_dump() for job in _jobs.values()]
        with open(JOBS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.warning("Failed to save jobs to %s: %s", JOBS_JSON, e)


_jobs: Dict[str, EvalJob] = _load_jobs()

# 默认并行任务数（可通过环境变量覆盖）
DEFAULT_MAX_PARALLEL_TASKS = int(os.environ.get("EVAL_MAX_PARALLEL_TASKS", "32"))
# 默认 inspect_ai 并发连接数
DEFAULT_MAX_CONNECTIONS = int(os.environ.get("EVAL_MAX_CONNECTIONS", "256"))

# Track asyncio tasks and subprocesses for cancellation
_async_tasks: Dict[str, asyncio.Task] = {}
_processes: Dict[str, List[asyncio.subprocess.Process]] = {}


def get_all_jobs() -> List[EvalJob]:
    """获取所有评测任务"""
    return list(_jobs.values())


def get_job(job_id: str) -> Optional[EvalJob]:
    """获取指定评测任务"""
    return _jobs.get(job_id)


async def create_job(req: EvalJobCreate) -> EvalJob:
    """创建评测任务"""
    # Lookup model config: prefer explicit model_config_id, fall back to model_id
    model = None
    if req.model_config_id:
        model = get_model(req.model_config_id)
    if not model:
        model = get_model(req.model_id) or get_model_by_model_id(req.model_id)
    model_name = model.name if model else req.model_id
    model_id_str = model.model_id if model else req.model_id

    # 解析 benchmark -> 具体 task 列表
    all_benchmarks = get_all_benchmarks()
    benchmark_map = {b.name: b for b in all_benchmarks}

    tasks: List[EvalTaskProgress] = []
    for bench_name in req.benchmarks:
        bench = benchmark_map.get(bench_name)
        if not bench:
            continue
        for t in bench.tasks:
            tasks.append(EvalTaskProgress(
                task_name=t.name,
                benchmark=bench_name,
                status=TaskStatus.PENDING,
            ))

    job = EvalJob(
        id=uuid.uuid4().hex[:12],
        model_id=model_id_str,
        model_name=model_name,
        model_config_id=model.id if model else None,
        status=EvalStatus.PENDING,
        benchmarks=req.benchmarks,
        tasks=tasks,
        progress=0.0,
        created_at=datetime.now(timezone.utc).isoformat(),
        limit=req.limit,
        agent_id=req.agent_id,
        agent_name=req.agent_name,
    )
    _jobs[job.id] = job
    _save_jobs()

    # 启动异步执行
    task = asyncio.create_task(_run_job(job, req.max_parallel_tasks, req.max_connections))
    _async_tasks[job.id] = task
    _processes[job.id] = []
    return job


async def _run_job(
    job: EvalJob,
    max_parallel_tasks: Optional[int] = None,
    max_connections: Optional[int] = None,
):
    """异步执行评测任务 — 并行调度"""
    job.status = EvalStatus.RUNNING
    _save_jobs()
    total = len(job.tasks)
    concurrency = max_parallel_tasks or DEFAULT_MAX_PARALLEL_TASKS
    connections = max_connections or DEFAULT_MAX_CONNECTIONS
    sem = asyncio.Semaphore(concurrency)
    completed_count = 0

    async def _run_with_sem(task: EvalTaskProgress):
        nonlocal completed_count
        async with sem:
            task.status = TaskStatus.RUNNING
            last_error = None
            for attempt in range(1, MAX_TASK_RETRIES + 1):
                try:
                    task.retry_count = attempt - 1
                    await asyncio.wait_for(
                        _run_single_task(job, task, connections),
                        timeout=TASK_TIMEOUT_SECONDS,
                    )
                    task.status = TaskStatus.COMPLETED
                    last_error = None
                    break
                except asyncio.TimeoutError:
                    last_error = (
                        f"任务 {task.task_name} 执行超时 "
                        f"(超过 {TASK_TIMEOUT_SECONDS}s, 第 {attempt}/{MAX_TASK_RETRIES} 次)"
                    )
                    logger.warning(last_error)
                except asyncio.CancelledError:
                    # Job was cancelled — don't retry
                    last_error = "Cancelled"
                    break
                except Exception as e:
                    last_error = str(e)
                    logger.warning(
                        "Task %s attempt %d/%d failed: %s",
                        task.task_name, attempt, MAX_TASK_RETRIES, last_error,
                    )

                # Don't retry certain fatal errors
                if last_error:
                    error_type = _classify_error(last_error)
                    if error_type in ("AUTH_FAILURE", "ACCESS_DENIED", "MODEL_NOT_FOUND"):
                        logger.info(
                            "Task %s: non-retryable error (%s), skipping remaining retries",
                            task.task_name, error_type,
                        )
                        break

                # Brief backoff before retry (2s, 4s, 8s, 16s)
                if attempt < MAX_TASK_RETRIES:
                    await asyncio.sleep(min(2 ** attempt, 16))

            if last_error:
                task.status = TaskStatus.FAILED
                task.retry_count = min(attempt, MAX_TASK_RETRIES) - 1
                error_type = _classify_error(last_error)
                label = _ERROR_LABELS.get(error_type, "未知错误")
                task.error = f"[{label}] {last_error} (重试 {task.retry_count} 次后失败)"

            completed_count += 1
            job.progress = (completed_count / total) * 100 if total > 0 else 100
            _save_jobs()

    # Run all tasks with bounded concurrency
    await asyncio.gather(*[_run_with_sem(t) for t in job.tasks])

    # 检查最终状态
    failed = [t for t in job.tasks if t.status == TaskStatus.FAILED]
    if failed:
        if len(failed) == total:
            job.status = EvalStatus.FAILED
            job.error = f"所有 {total} 个任务执行失败"
        else:
            job.status = EvalStatus.COMPLETED
            job.error = f"{len(failed)} 个任务执行失败"
    else:
        job.status = EvalStatus.COMPLETED

    job.current_task = None
    job.progress = 100.0
    job.completed_at = datetime.now(timezone.utc).isoformat()
    _save_jobs()

    # Clean up handles
    _async_tasks.pop(job.id, None)
    _processes.pop(job.id, None)


async def _run_single_task(job: EvalJob, task: EvalTaskProgress, max_connections: int = 16):
    """执行单个评测任务（含子进程超时清理）"""
    # 构建命令: ./run-eval.py <benchmark>:<task> --model <model>
    task_spec = f"{task.benchmark}:{task.task_name}" if task.benchmark != task.task_name else task.task_name

    cmd = [
        str(RUN_EVAL_SCRIPT),
        task_spec,
        "--model", job.model_id,
    ]

    if job.limit:
        cmd.extend(["--limit", str(job.limit)])

    # 透传 api_base / api_key 作为 CLI 参数（避免被 .env 覆盖）
    model_cfg = None
    if job.model_config_id:
        model_cfg = get_model(job.model_config_id)
    if not model_cfg:
        model_cfg = get_model_by_model_id(job.model_id)
    if model_cfg:
        if model_cfg.api_base:
            cmd.extend(["--api-base", model_cfg.api_base])
        if model_cfg.api_key:
            cmd.extend(["--api-key", model_cfg.api_key])

    # 传递 inspect_ai 并发参数作为 extra args
    cmd.extend(["--max-connections", str(max_connections)])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(PROJECT_ROOT),
    )

    # Track process for cancellation
    if job.id in _processes:
        _processes[job.id].append(process)

    try:
        stdout, stderr = await process.communicate()
    except asyncio.CancelledError:
        # Timeout or cancellation — kill the subprocess
        _kill_process(process)
        raise

    # Remove from tracking after completion
    if job.id in _processes:
        try:
            _processes[job.id].remove(process)
        except ValueError:
            pass

    if process.returncode != 0:
        stderr_text = stderr.decode("utf-8", errors="replace").strip()
        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        # Prefer stderr; fall back to stdout if stderr is empty (inspect_ai sometimes prints errors to stdout)
        error_msg = (stderr_text or stdout_text)[-500:]
        raise RuntimeError(f"任务 {task.task_name} 执行失败 (exit {process.returncode}): {error_msg}")


def _kill_process(process: asyncio.subprocess.Process):
    """Terminate then kill a subprocess, ignoring already-exited processes."""
    try:
        process.terminate()
    except ProcessLookupError:
        return
    # Schedule force-kill after a short grace period
    try:
        process.kill()
    except ProcessLookupError:
        pass


async def cancel_job(job_id: str) -> bool:
    """Cancel a running or pending evaluation job."""
    job = _jobs.get(job_id)
    if not job:
        return False
    if job.status not in (EvalStatus.PENDING, EvalStatus.RUNNING):
        return False

    # 1. Cancel the asyncio task
    task = _async_tasks.pop(job_id, None)
    if task and not task.done():
        task.cancel()

    # 2. Terminate all tracked subprocesses
    procs = _processes.pop(job_id, [])
    for proc in procs:
        try:
            proc.terminate()
        except ProcessLookupError:
            pass
    # Give processes a moment to terminate, then force-kill
    if procs:
        await asyncio.sleep(1)
        for proc in procs:
            try:
                proc.kill()
            except ProcessLookupError:
                pass

    # 3. Update job status
    job.status = EvalStatus.CANCELLED
    job.completed_at = datetime.now(timezone.utc).isoformat()
    job.error = "Cancelled by user"
    job.current_task = None
    # Mark pending/running tasks as cancelled
    for t in job.tasks:
        if t.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            t.status = TaskStatus.FAILED
            t.error = "Cancelled"
    _save_jobs()

    logger.info("Cancelled job %s", job_id)
    return True
