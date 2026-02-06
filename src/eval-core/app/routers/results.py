"""评测结果 API"""

from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import ModelResultSummary, ModelResult
from ..services.score_service import get_all_model_results, get_model_detail

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("", response_model=List[ModelResultSummary])
def list_results():
    """列出所有模型的评测结果摘要"""
    return get_all_model_results()


@router.get("/{model}", response_model=ModelResult)
def get_result_detail(model: str):
    """获取指定模型的详细评测结果"""
    result = get_model_detail(model)
    if not result:
        raise HTTPException(status_code=404, detail="未找到该模型的评测结果")
    return result
