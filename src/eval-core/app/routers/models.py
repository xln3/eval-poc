"""模型管理 API"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..models.schemas import ModelConfig, ModelCreateRequest
from ..services.model_store import get_all_models, add_custom_model, delete_custom_model, update_custom_model

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=List[ModelConfig])
def list_models():
    """列出所有模型（预置 + 自定义）"""
    return get_all_models()


@router.post("", response_model=ModelConfig)
def create_model(req: ModelCreateRequest):
    """添加自定义模型"""
    return add_custom_model(req)


@router.put("/{model_id}", response_model=ModelConfig)
def update_model(model_id: str, updates: Dict[str, Any]):
    """Update a custom model."""
    result = update_custom_model(model_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="模型不存在或为预置模型")
    return result


@router.delete("/{model_id}")
def remove_model(model_id: str):
    """删除自定义模型"""
    if not delete_custom_model(model_id):
        raise HTTPException(status_code=404, detail="模型不存在或为预置模型")
    return {"message": "删除成功"}
