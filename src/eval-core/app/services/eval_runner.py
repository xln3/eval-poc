"""异步评测执行器 — 支持任务级并行"""

import asyncio
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from ..config import RUN_EVAL_SCRIPT, PROJECT_ROOT
from ..models.schemas import (
    EvalJob, EvalJobCreate, EvalStatus, EvalTaskProgress, TaskStatus,
)
from .catalog_service import get_all_benchmarks, get_task_display_name
from .model_store import get_model

# 内存 Job 存储
_jobs: Dict[str, EvalJob] = {}

# 默认并行任务数（可通过环境变量覆盖）
DEFAULT_MAX_PARALLEL_TASKS = int(os.environ.get("EVAL_MAX_PARALLEL_TASKS", "4"))
# 默认 inspect_ai 并发连接数
DEFAULT_MAX_CONNECTIONS = int(os.environ.get("EVAL_MAX_CONNECTIONS", "16"))


def get_all_jobs() -> List[EvalJob]:
    """获取所有评测任务"""
    return list(_jobs.values())


def get_job(job_id: str) -> Optional[EvalJob]:
    """获取指定评测任务"""
    return _jobs.get(job_id)


async def create_job(req: EvalJobCreate) -> EvalJob:
    """创建评测任务"""
    model = get_model(req.model_id)
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
        created_at=datetime.now().isoformat(),
        limit=req.limit,
        agent_id=req.agent_id,
        agent_name=req.agent_name,
    )
    _jobs[job.id] = job

    # 启动异步执行
    asyncio.create_task(_run_job(job, req.max_parallel_tasks, req.max_connections))
    return job


async def _run_job(
    job: EvalJob,
    max_parallel_tasks: Optional[int] = None,
    max_connections: Optional[int] = None,
):
    """异步执行评测任务 — 并行调度"""
    job.status = EvalStatus.RUNNING
    total = len(job.tasks)
    concurrency = max_parallel_tasks or DEFAULT_MAX_PARALLEL_TASKS
    connections = max_connections or DEFAULT_MAX_CONNECTIONS
    sem = asyncio.Semaphore(concurrency)
    completed_count = 0

    async def _run_with_sem(task: EvalTaskProgress):
        nonlocal completed_count
        async with sem:
            task.status = TaskStatus.RUNNING
            try:
                await _run_single_task(job, task, connections)
                task.status = TaskStatus.COMPLETED
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
            finally:
                completed_count += 1
                job.progress = (completed_count / total) * 100 if total > 0 else 100

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
    job.completed_at = datetime.now().isoformat()


async def _run_single_task(job: EvalJob, task: EvalTaskProgress, max_connections: int = 16):
    """执行单个评测任务"""
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
    if job.model_config_id:
        model_cfg = get_model(job.model_config_id)
        if model_cfg and model_cfg.api_base:
            cmd.extend(["--api-base", model_cfg.api_base])
        if model_cfg and model_cfg.api_key:
            cmd.extend(["--api-key", model_cfg.api_key])

    # 传递 inspect_ai 并发参数作为 extra args
    cmd.extend(["--max-connections", str(max_connections)])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(PROJECT_ROOT),
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"任务 {task.task_name} 执行失败 (exit {process.returncode}): {error_msg}")
