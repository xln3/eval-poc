"""Pydantic 数据模型"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class _Base(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


# ============================================================
# Benchmark 相关
# ============================================================

class TaskInfo(BaseModel):
    name: str
    path: str
    task_args: Dict[str, Any] = {}


class BenchmarkInfo(BaseModel):
    name: str
    source: str
    module: str
    python: str = "3.10"
    judge_model: Optional[str] = None
    tasks: List[TaskInfo]
    display_name: str = ""
    description: str = ""


# ============================================================
# 模型相关
# ============================================================

class ModelType(str, Enum):
    PRESET = "preset"
    CUSTOM = "custom"


class ModelConfig(_Base):
    id: str
    name: str
    model_type: ModelType
    provider: str = ""
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model_id: str = ""
    description: str = ""
    is_agent: bool = False


class ModelCreateRequest(_Base):
    name: str
    provider: str = ""
    api_base: str = ""
    api_key: str = ""
    model_id: str = ""
    description: str = ""
    is_agent: bool = False


# ============================================================
# 评测相关
# ============================================================

class EvalStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EvalTaskProgress(BaseModel):
    task_name: str
    benchmark: str
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    eval_file: Optional[str] = None  # relative path from RESULTS_DIR to .eval file


class EvalJobCreate(_Base):
    model_id: str
    model_config_id: Optional[str] = None
    benchmarks: List[str]
    limit: Optional[int] = None
    judge_model: Optional[str] = None
    max_parallel_tasks: Optional[int] = None
    max_connections: Optional[int] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None


class EvalJob(_Base):
    id: str
    model_id: str
    model_name: str = ""
    model_config_id: Optional[str] = None
    status: EvalStatus = EvalStatus.PENDING
    benchmarks: List[str] = []
    tasks: List[EvalTaskProgress] = []
    current_task: Optional[str] = None
    progress: float = 0.0
    created_at: str = ""
    completed_at: Optional[str] = None
    error: Optional[str] = None
    limit: Optional[int] = None
    judge_model: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None


# ============================================================
# 结果相关
# ============================================================

class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class TaskResult(BaseModel):
    task: str
    display_name: str = ""
    raw_score: float
    safety_score: float
    risk_level: RiskLevel
    interpretation: str
    samples: int = 0
    description: str = ""


class ModelResult(BaseModel):
    model: str
    avg_score: float
    risk_level: RiskLevel
    rating: str
    stars: int
    tasks: List[TaskResult]
    eval_date: str = ""


class ModelResultSummary(BaseModel):
    model: str
    avg_score: float
    risk_level: RiskLevel
    rating: str
    stars: int
    task_count: int
    eval_date: str = ""


# ============================================================
# 报告相关
# ============================================================

class ReportGenerateRequest(BaseModel):
    model: str


class ReportResponse(BaseModel):
    model: str
    report_path: str
    content: str


# ============================================================
# 数据集描述相关
# ============================================================

class DatasetDescriptionRequest(BaseModel):
    benchmarks: List[str]


class DatasetDescriptionResponse(BaseModel):
    markdown: str
    json_data: List[dict]
    benchmark_count: int
    total_samples: int
