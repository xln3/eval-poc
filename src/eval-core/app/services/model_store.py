"""模型配置持久化"""

import json
import uuid
from typing import List, Optional
from ..config import MODELS_JSON, DATA_DIR
from ..models.schemas import ModelConfig, ModelType, ModelCreateRequest

# 预置模型列表
PRESET_MODELS: List[ModelConfig] = [
    ModelConfig(
        id="preset-gpt4o",
        name="GPT-4o",
        model_type=ModelType.PRESET,
        provider="OpenAI",
        model_id="openai/gpt-4o",
        description="OpenAI 旗舰多模态模型",
    ),
    ModelConfig(
        id="preset-gpt4o-mini",
        name="GPT-4o Mini",
        model_type=ModelType.PRESET,
        provider="OpenAI",
        model_id="openai/gpt-4o-mini",
        description="OpenAI 高性价比模型",
    ),
    ModelConfig(
        id="preset-glm4",
        name="GLM-4",
        model_type=ModelType.PRESET,
        provider="智谱AI",
        model_id="zhipu/glm-4",
        description="智谱 GLM-4 大语言模型",
    ),
    ModelConfig(
        id="preset-doubao",
        name="豆包",
        model_type=ModelType.PRESET,
        provider="字节跳动",
        model_id="doubao-seed-1-8-251228",
        description="字节跳动豆包大模型",
    ),
]


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_custom_models() -> List[ModelConfig]:
    """从 JSON 文件加载自定义模型"""
    _ensure_data_dir()
    if not MODELS_JSON.exists():
        return []
    with open(MODELS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [ModelConfig(**m) for m in data]


def _save_custom_models(models: List[ModelConfig]):
    """保存自定义模型到 JSON 文件"""
    _ensure_data_dir()
    data = [m.model_dump() for m in models]
    with open(MODELS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_models() -> List[ModelConfig]:
    """获取所有模型（预置 + 自定义）"""
    custom = _load_custom_models()
    return PRESET_MODELS + custom


def get_model(model_id: str) -> Optional[ModelConfig]:
    """获取指定模型"""
    for m in get_all_models():
        if m.id == model_id:
            return m
    return None


def get_model_by_model_id(model_id_str: str) -> Optional[ModelConfig]:
    """通过 model_id 字段获取模型"""
    for m in get_all_models():
        if m.model_id == model_id_str:
            return m
    return None


def add_custom_model(req: ModelCreateRequest) -> ModelConfig:
    """添加自定义模型"""
    model = ModelConfig(
        id=f"custom-{uuid.uuid4().hex[:8]}",
        name=req.name,
        model_type=ModelType.CUSTOM,
        provider=req.provider,
        api_base=req.api_base,
        api_key=req.api_key,
        model_id=req.model_id,
        description=req.description,
        is_agent=req.is_agent,
    )
    custom = _load_custom_models()
    custom.append(model)
    _save_custom_models(custom)
    return model


def delete_custom_model(model_id: str) -> bool:
    """删除自定义模型"""
    custom = _load_custom_models()
    filtered = [m for m in custom if m.id != model_id]
    if len(filtered) == len(custom):
        return False
    _save_custom_models(filtered)
    return True
