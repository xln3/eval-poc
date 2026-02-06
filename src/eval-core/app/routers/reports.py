"""报告生成 API"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import ReportGenerateRequest, ReportResponse
from ..services.report_service import generate_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate", response_model=ReportResponse)
def create_report(req: ReportGenerateRequest):
    """生成评测报告"""
    result = generate_report(req.model)
    if not result:
        raise HTTPException(status_code=404, detail="未找到该模型的评测结果")
    return result
