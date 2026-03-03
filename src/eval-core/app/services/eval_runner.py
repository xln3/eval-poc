"""异步评测执行器 — 支持任务级并行 + JSON 持久化 + 任务重试"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import uuid
import zipfile
from datetime import datetime, timezone
from typing import Dict, List, Optional
from ..config import RUN_EVAL_SCRIPT, PROJECT_ROOT, DATA_DIR, JOBS_JSON, RESULTS_DIR
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

    # Timeout (includes Chinese "超时" from timeout error messages)
    if any(kw in lower for kw in ["timeout", "timed out", "deadline exceeded", "超时"]):
        return "TIMEOUT"

    # Out of memory / resource
    if any(kw in lower for kw in ["out of memory", "oom", "resource exhausted",
                                   "insufficient", "cuda out of memory"]):
        return "RESOURCE_EXHAUSTED"

    # Content filter / safety
    if any(kw in lower for kw in ["content filter", "content_filter", "safety filter",
                                   "blocked by", "content policy"]):
        return "CONTENT_FILTERED"

    # Data / file missing (e.g. FileNotFoundError from incomplete dataset downloads)
    if any(kw in lower for kw in ["filenotfounderror", "no such file", "missing data",
                                   "file not found", "not found: /"]):
        return "DATA_MISSING"

    return "UNKNOWN_ERROR"


_NON_RETRYABLE = {"AUTH_FAILURE", "ACCESS_DENIED", "MODEL_NOT_FOUND", "DATA_MISSING"}


def _find_latest_eval_file(model_id: str, task_name: str) -> Optional[str]:
    """Find the most recent .eval file for a model/task combination.

    Returns a relative path from RESULTS_DIR, or None if not found.
    Used after task completion to record which .eval file was produced (bug #53).
    """
    if not RESULTS_DIR.exists():
        return None
    model_short = model_id.split("/")[-1].strip()
    best_file = None
    for model_dir in RESULTS_DIR.iterdir():
        if not model_dir.is_dir():
            continue
        dir_name = model_dir.name.strip()
        if model_short not in dir_name and dir_name not in model_short:
            continue
        for bench_dir in model_dir.iterdir():
            if not bench_dir.is_dir():
                continue
            logs_dir = bench_dir / "logs"
            if not logs_dir.exists():
                continue
            for eval_file in logs_dir.glob("*.eval"):
                # Task names use underscores; filenames use hyphens
                parts = eval_file.stem.split("_")
                if len(parts) >= 3:
                    file_task = "_".join(parts[1:-1])
                    if task_name.replace("_", "-") != file_task.replace("_", "-"):
                        continue
                else:
                    if task_name.replace("_", "-") not in eval_file.stem.replace("_", "-"):
                        continue
                # Filenames start with ISO timestamps; pick the latest
                if best_file is None or eval_file.name > best_file.name:
                    best_file = eval_file
    if best_file is None:
        return None
    try:
        return str(best_file.relative_to(RESULTS_DIR))
    except ValueError:
        return str(best_file)


# ---- Job persistence (following model_store.py pattern) ----

def _load_jobs() -> Dict[str, EvalJob]:
    """Load persisted jobs from JSON on startup."""
    JOBS_JSON.parent.mkdir(parents=True, exist_ok=True)
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
                # Also mark stale tasks within the job (bug #47)
                for t in job.tasks:
                    if t.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                        t.status = TaskStatus.FAILED
                        t.error = "Service restarted while task was running"
            jobs[job.id] = job
        logger.info("Loaded %d persisted jobs from %s", len(jobs), JOBS_JSON)
        return jobs
    except Exception as e:
        logger.warning("Failed to load jobs from %s: %s", JOBS_JSON, e)
        return {}


def _save_jobs():
    """Persist current jobs dict to JSON file."""
    try:
        JOBS_JSON.parent.mkdir(parents=True, exist_ok=True)
        data = [job.model_dump() for job in _jobs.values()]
        with open(JOBS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.warning("Failed to save jobs to %s: %s", JOBS_JSON, e)


def _cleanup_orphaned_containers_on_startup():
    """Stop and remove orphaned inspect-* Docker containers left from previous runs.

    When the eval-backend restarts, containers spawned by inspect_ai's Docker
    sandbox remain running. These 'inspect-*' named containers are safe to
    remove since no jobs are active right after startup.
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "-q", "--filter", "name=inspect-"],
            capture_output=True, text=True, timeout=10,
        )
        container_ids = result.stdout.strip().split()
        container_ids = [c for c in container_ids if c]  # filter empty strings
        if not container_ids:
            return
        logger.info("Cleaning up %d orphaned inspect-* containers on startup", len(container_ids))
        subprocess.run(
            ["docker", "stop", "--time", "5"] + container_ids,
            capture_output=True, timeout=60,
        )
        subprocess.run(
            ["docker", "rm", "-f"] + container_ids,
            capture_output=True, timeout=30,
        )
        logger.info("Successfully cleaned up orphaned containers")
    except Exception as e:
        logger.warning("Failed to clean up orphaned containers on startup: %s", e)


_jobs: Dict[str, EvalJob] = _load_jobs()

# Clean up orphaned Docker containers from previous runs on startup
_cleanup_orphaned_containers_on_startup()

# 默认并行任务数（可通过环境变量覆盖）
# 注意: 32 并发 × 256 连接 = 8192 潜在并发请求，会导致代理/API 连接耗尽，
# 造成所有任务 SSL 超时、无一完成。实测 8 并发 × 32 连接足够稳定。
DEFAULT_MAX_PARALLEL_TASKS = int(os.environ.get("EVAL_MAX_PARALLEL_TASKS", "8"))
# 默认 inspect_ai 并发连接数（每个 task 的最大 API 并发请求数）
DEFAULT_MAX_CONNECTIONS = int(os.environ.get("EVAL_MAX_CONNECTIONS", "32"))

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
                    # Record which .eval file this task produced (bug #53)
                    task.eval_file = _find_latest_eval_file(job.model_id, task.task_name)
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
                    if error_type in _NON_RETRYABLE:
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
                task.error_type = _classify_error(last_error)
                task.error = last_error

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

    # Clean up stale Docker networks to prevent address pool exhaustion (Bug #91)
    _cleanup_docker_networks()

    # Clean up handles
    _async_tasks.pop(job.id, None)
    _processes.pop(job.id, None)


def _check_eval_file_status(model_id: str, task_name: str):
    """Check the latest .eval file for a task; raise if status is 'error'.

    inspect_ai may exit 0 but record status=error in the .eval header
    when sample-level errors occur. This catches those false-positive completions.
    """
    model_short = model_id.split("/")[-1].strip()
    # Search all model dirs that match
    if not RESULTS_DIR.exists():
        return
    candidates = []
    for model_dir in RESULTS_DIR.iterdir():
        if not model_dir.is_dir():
            continue
        dir_name = model_dir.name.strip()
        if model_short not in dir_name and dir_name not in model_short:
            continue
        for bench_dir in model_dir.iterdir():
            if not bench_dir.is_dir():
                continue
            logs_dir = bench_dir / "logs"
            if not logs_dir.exists():
                continue
            for eval_file in logs_dir.glob("*.eval"):
                candidates.append(eval_file)
    if not candidates:
        return

    # Find the most recent .eval file matching this task
    # Sort by mtime descending to get the latest
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for eval_path in candidates:
        try:
            with zipfile.ZipFile(str(eval_path), "r") as zf:
                with zf.open("header.json") as f:
                    header = json.loads(f.read())
            file_task = header.get("eval", {}).get("task", "").split("/")[-1]
            if file_task != task_name:
                continue
            status = header.get("status", "")
            if status == "error":
                error_info = header.get("error", {})
                error_msg = error_info.get("message", "unknown error") if isinstance(error_info, dict) else str(error_info)
                raise RuntimeError(
                    f"任务 {task_name} 进程退出成功但 .eval 状态为 error: {error_msg}"
                )
            return  # found the matching file and it's not error — OK
        except (zipfile.BadZipFile, json.JSONDecodeError, KeyError):
            continue


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
        start_new_session=True,  # create new process group for clean tree killing
    )

    # Track process for cancellation
    if job.id in _processes:
        _processes[job.id].append(process)

    try:
        stdout, stderr = await process.communicate()
    except asyncio.CancelledError:
        # Timeout or cancellation — kill the entire process tree
        await _kill_process(process)
        raise
    finally:
        # Always remove from tracking and ensure process is dead
        if job.id in _processes:
            try:
                _processes[job.id].remove(process)
            except ValueError:
                pass
        # Safety net: if process is still alive after communicate(), kill it
        if process.returncode is None:
            await _kill_process(process)

    if process.returncode != 0:
        stderr_text = stderr.decode("utf-8", errors="replace").strip()
        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        # Prefer stderr; fall back to stdout if stderr is empty (inspect_ai sometimes prints errors to stdout)
        raw = stderr_text or stdout_text
        # Keep both the beginning (where the real error usually is) and the end (context),
        # so that long Docker help text doesn't bury the actual error message.
        if len(raw) > 800:
            error_msg = raw[:400] + "\n...[truncated]...\n" + raw[-400:]
        else:
            error_msg = raw
        raise RuntimeError(f"任务 {task.task_name} 执行失败 (exit {process.returncode}): {error_msg}")

    # Bug #48 fix: inspect may exit 0 but write status=error in .eval file.
    # Check the latest .eval file for this task to catch sample-level errors.
    _check_eval_file_status(job.model_id, task.task_name)


async def _kill_process(process: asyncio.subprocess.Process):
    """Kill subprocess and its entire process tree via process group.

    Because subprocesses are created with start_new_session=True,
    each subprocess is a process group leader. Killing the group
    ensures all children (inspect, vendor scripts, etc.) are terminated.

    Sends SIGTERM first with a grace period so inspect_ai can clean up
    Docker containers, then force-kills with SIGKILL.
    """
    pid = process.pid
    if pid is None:
        return
    # Try graceful SIGTERM first — gives inspect_ai time to stop Docker containers
    try:
        os.killpg(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        pass
    # Grace period: let inspect_ai handle SIGTERM and clean up containers
    await asyncio.sleep(3)
    # Force-kill the group if still alive
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        pass
    # Fallback: kill the process directly if group kill failed
    try:
        process.kill()
    except ProcessLookupError:
        pass


def _cleanup_docker_containers(benchmarks: List[str]):
    """Stop and remove Docker containers orphaned by cancelled eval tasks.

    inspect_ai containers follow the naming pattern: inspect-<benchmark>-<id>-<role>-<n>
    """
    for bench in benchmarks:
        # Normalize: catalog keys use underscore, Docker compose names use underscore too
        # but the container filter matches as substring
        try:
            result = subprocess.run(
                ["docker", "ps", "-q", "--filter", f"name=inspect-{bench}"],
                capture_output=True, text=True, timeout=10,
            )
            container_ids = result.stdout.strip().split()
            if container_ids:
                logger.info("Stopping %d orphaned Docker containers for benchmark %s",
                            len(container_ids), bench)
                subprocess.run(
                    ["docker", "stop", "--time", "5"] + container_ids,
                    capture_output=True, timeout=30,
                )
                subprocess.run(
                    ["docker", "rm", "-f"] + container_ids,
                    capture_output=True, timeout=30,
                )
        except Exception as e:
            logger.warning("Failed to clean up Docker containers for %s: %s", bench, e)


def _cleanup_docker_networks():
    """Remove stale inspect-* Docker networks to prevent address pool exhaustion (Bug #91).

    inspect_ai creates a new bridge network per compose run but does not always
    remove it on exit, especially after timeouts or cancellations.  Over time
    the default Docker address pool fills up and *all* Docker-dependent benchmarks
    fail with "all predefined address pools have been fully subnetted".
    """
    try:
        ls = subprocess.run(
            ["docker", "network", "ls", "--format", "{{.Name}}",
             "--filter", "name=inspect-"],
            capture_output=True, text=True, timeout=10,
        )
        if ls.returncode != 0:
            return
        networks = [n.strip() for n in ls.stdout.splitlines() if n.strip()]
        if not networks:
            return
        removed = 0
        for net in networks:
            rm = subprocess.run(
                ["docker", "network", "rm", net],
                capture_output=True, text=True, timeout=10,
            )
            if rm.returncode == 0:
                removed += 1
        if removed:
            logger.info("Docker network cleanup: removed %d stale inspect-* network(s)", removed)
    except Exception as e:
        logger.debug("Docker network cleanup skipped: %s", e)


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

    # 2. Terminate all tracked subprocesses (SIGTERM + grace period + SIGKILL)
    procs = _processes.pop(job_id, [])
    if procs:
        await asyncio.gather(*[_kill_process(proc) for proc in procs])

    # 3. Clean up any Docker containers spawned by Docker-requiring benchmarks
    docker_benchmarks = list({t.benchmark for t in job.tasks})
    if docker_benchmarks:
        await asyncio.get_running_loop().run_in_executor(
            None, _cleanup_docker_containers, docker_benchmarks,
        )

    # 4. Clean up stale Docker networks (Bug #91)
    await asyncio.get_running_loop().run_in_executor(
        None, _cleanup_docker_networks,
    )

    # 5. Update job status
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
