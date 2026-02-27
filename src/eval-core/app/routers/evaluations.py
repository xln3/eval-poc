"""评测执行 API"""

from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import EvalJob, EvalJobCreate
from ..services.eval_runner import create_job, get_job, get_all_jobs, cancel_job

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


@router.get("", response_model=List[EvalJob])
def list_evaluations():
    """列出所有评测任务"""
    return get_all_jobs()


@router.get("/{job_id}", response_model=EvalJob)
def get_evaluation(job_id: str):
    """查看评测进度"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="评测任务不存在")
    return job


@router.post("", response_model=EvalJob)
async def start_evaluation(req: EvalJobCreate):
    """启动评测（异步）"""
    if not req.benchmarks:
        raise HTTPException(status_code=400, detail="请选择至少一个评测任务")
    job = await create_job(req)
    return job


@router.delete("/{job_id}")
async def cancel_evaluation(job_id: str):
    """取消评测任务"""
    success = await cancel_job(job_id)
    if not success:
        job = get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="评测任务不存在")
        raise HTTPException(status_code=400, detail=f"无法取消状态为 {job.status} 的任务")
    return {"status": "cancelled", "job_id": job_id}
