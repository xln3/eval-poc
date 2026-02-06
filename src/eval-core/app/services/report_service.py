"""调用 report_generator.py 生成报告"""

import sys
from typing import Optional
from ..config import PROJECT_ROOT, RESULTS_DIR, REPORTS_DIR
from ..models.schemas import ReportResponse
from .result_reader import scan_results, EvalFileResult

# 将项目根目录加入 sys.path
_root = str(PROJECT_ROOT)
if _root not in sys.path:
    sys.path.insert(0, _root)

from report_generator import generate_model_report, EvalResult as ReportEvalResult


def generate_report(model_name: str) -> Optional[ReportResponse]:
    """为指定模型生成安全评测报告"""
    all_results = scan_results()

    # 模糊匹配模型名
    model_results = None
    matched_model = None
    for model, results in all_results.items():
        if model == model_name or model_name in model or model in model_name:
            model_results = results
            matched_model = model
            break

    if not model_results or not matched_model:
        return None

    # 将 EvalFileResult 转换为 report_generator 的 EvalResult
    report_results = []
    for r in model_results:
        report_results.append(ReportEvalResult(
            task=r.task,
            model=r.model,
            raw_accuracy=r.raw_accuracy,
            samples=r.samples,
            timestamp=r.timestamp,
            file_path=r.file_path,
        ))

    # 生成报告
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = generate_model_report(
        matched_model,
        report_results,
        str(REPORTS_DIR),
    )

    # 读取报告内容
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()

    return ReportResponse(
        model=matched_model,
        report_path=output_path,
        content=content,
    )
