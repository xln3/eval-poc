"""评测任务 API"""

from fastapi import APIRouter
from typing import List
from ..models.schemas import BenchmarkInfo
from ..services.catalog_service import get_all_benchmarks, TASK_META

router = APIRouter(prefix="/api/benchmarks", tags=["benchmarks"])


@router.get("", response_model=List[BenchmarkInfo])
def list_benchmarks():
    """列出所有已注册的评测任务"""
    return get_all_benchmarks()


@router.get("/task-meta")
def get_task_metadata():
    """获取所有任务的中文元数据"""
    return TASK_META
