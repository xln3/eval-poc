"""评测任务 API"""

from fastapi import APIRouter, Query
from typing import List
from ..models.schemas import BenchmarkInfo
from ..services.catalog_service import get_all_benchmarks, TASK_META, BENCHMARK_META

router = APIRouter(prefix="/api/benchmarks", tags=["benchmarks"])


@router.get("", response_model=List[BenchmarkInfo])
def list_benchmarks():
    """列出所有已注册的评测任务"""
    return get_all_benchmarks()


@router.get("/task-meta")
def get_task_metadata():
    """获取所有任务的中文元数据"""
    return TASK_META


@router.get("/benchmark-meta")
def get_benchmark_metadata():
    """获取所有 benchmark 的元数据（含中英文）"""
    return BENCHMARK_META


@router.get("/health")
async def get_health(force: bool = Query(False, description="Force refresh")):
    """Get health status for all benchmarks (cached 5 min)."""
    from ..services.health_service import get_benchmark_health
    return await get_benchmark_health(force=force)
