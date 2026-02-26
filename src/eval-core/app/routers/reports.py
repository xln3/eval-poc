"""报告生成 API"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import (
    ReportGenerateRequest,
    ReportResponse,
    DatasetDescriptionRequest,
    DatasetDescriptionResponse,
)
from ..services.report_service import generate_report
from ..services.dataset_service import generate_dataset_description

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate", response_model=ReportResponse)
def create_report(req: ReportGenerateRequest):
    """生成评测报告"""
    result = generate_report(req.model)
    if not result:
        raise HTTPException(status_code=404, detail="未找到该模型的评测结果")
    return result


@router.post("/dataset-description", response_model=DatasetDescriptionResponse)
async def create_dataset_description(request: DatasetDescriptionRequest):
    """生成测试数据集说明报告和混合样本数据集"""
    if not request.benchmarks:
        raise HTTPException(status_code=400, detail="请至少选择一个 benchmark")
    result = await generate_dataset_description(request.benchmarks)
    return DatasetDescriptionResponse(**result)
