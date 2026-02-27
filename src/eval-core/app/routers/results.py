"""评测结果 API"""

import json
import subprocess
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from ..config import RESULTS_DIR
from ..models.schemas import ModelResultSummary, ModelResult
from ..services.score_service import get_all_model_results, get_model_detail
from ..services.result_reader import get_model_results

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


@router.get("/{model}/tasks/{task}/samples")
def get_task_samples(
    model: str,
    task: str,
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
):
    """获取指定模型/任务的每个样本结果（从 .eval ZIP 中解析）"""
    # Find the matching .eval file
    model_results = get_model_results(model)
    eval_result = next((r for r in model_results if r.task == task), None)
    if not eval_result:
        raise HTTPException(status_code=404, detail=f"未找到 {model}/{task} 的评测结果")

    # Resolve full file path
    eval_file = _find_eval_file(model, task)
    if not eval_file:
        raise HTTPException(status_code=404, detail="未找到 .eval 文件")

    samples = _extract_samples(eval_file)

    # Filter by risk_level if requested
    if risk_level:
        samples = [s for s in samples if s.get("risk_level", "").upper() == risk_level.upper()]

    return {
        "model": model,
        "task": task,
        "total_samples": len(samples),
        "samples": samples,
    }


def _find_eval_file(model: str, task: str) -> Optional[str]:
    """Locate the .eval file for a model/task combination."""
    if not RESULTS_DIR.exists():
        return None

    for model_dir in RESULTS_DIR.iterdir():
        if not model_dir.is_dir():
            continue
        # Fuzzy match model name
        if model not in model_dir.name and model_dir.name not in model:
            continue
        for bench_dir in model_dir.iterdir():
            if not bench_dir.is_dir():
                continue
            logs_dir = bench_dir / "logs"
            if not logs_dir.exists():
                continue
            for eval_file in logs_dir.glob("*.eval"):
                if task in eval_file.stem:
                    return str(eval_file)
    return None


def _extract_samples(eval_file_path: str) -> list:
    """Extract per-sample data from .eval zip file."""
    samples = []
    try:
        # Try to extract samples.json first (some eval files have it)
        proc = subprocess.run(
            ["unzip", "-p", eval_file_path, "samples.json"],
            capture_output=True, text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            raw_samples = json.loads(proc.stdout)
            for i, sample in enumerate(raw_samples if isinstance(raw_samples, list) else []):
                samples.append(_normalize_sample(i, sample))
            return samples

        # Fallback: extract header.json for summary info
        proc = subprocess.run(
            ["unzip", "-p", eval_file_path, "header.json"],
            capture_output=True, text=True,
        )
        if proc.returncode == 0:
            header = json.loads(proc.stdout)
            completed = header.get("results", {}).get("completed_samples", 0)
            scores = header.get("results", {}).get("scores", [])
            metrics = {}
            for scorer in scores:
                metrics.update(scorer.get("metrics", {}))

            # Return summary-level info when per-sample data unavailable
            return [{
                "sample_id": "summary",
                "score": next((v["value"] for v in metrics.values() if isinstance(v, dict) and "value" in v), 0),
                "total_samples": completed,
                "input": "",
                "output": "",
                "risk_level": "UNKNOWN",
                "note": "Per-sample data not available; showing aggregate summary",
            }]

    except Exception:
        pass

    return samples


def _normalize_sample(idx: int, raw: dict) -> dict:
    """Normalize a raw sample dict to a consistent format."""
    # inspect_ai sample format varies, handle common shapes
    score = raw.get("score", raw.get("scores", {}).get("value", 0))
    if isinstance(score, dict):
        score = score.get("value", 0)

    input_text = raw.get("input", "")
    if isinstance(input_text, list):
        # Messages format
        input_text = "\n".join(
            m.get("content", "") for m in input_text if isinstance(m, dict)
        )

    output_text = raw.get("output", raw.get("target", ""))
    if isinstance(output_text, dict):
        output_text = output_text.get("completion", str(output_text))

    # Determine risk level from score
    if isinstance(score, (int, float)):
        if score <= 0.3:
            risk = "CRITICAL"
        elif score <= 0.5:
            risk = "HIGH"
        elif score <= 0.6:
            risk = "MEDIUM"
        elif score <= 0.8:
            risk = "LOW"
        else:
            risk = "MINIMAL"
    else:
        risk = "UNKNOWN"

    return {
        "sample_id": str(raw.get("id", idx)),
        "score": score,
        "input": str(input_text)[:2000],  # Truncate long inputs
        "output": str(output_text)[:2000],
        "risk_level": risk,
        "metadata": raw.get("metadata", {}),
    }
