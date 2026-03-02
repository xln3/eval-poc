"""读取 .eval 结果文件"""

import os
import json
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional
from ..config import RESULTS_DIR


@dataclass
class EvalFileResult:
    """单个 .eval 文件的结果"""
    task: str
    model: str
    raw_accuracy: float
    samples: int
    timestamp: str
    file_path: str


def scan_results() -> Dict[str, List[EvalFileResult]]:
    """扫描 results/ 目录，返回按模型分组的结果"""
    results_by_model: Dict[str, List[EvalFileResult]] = {}

    if not RESULTS_DIR.exists():
        return results_by_model

    # 遍历 results/<model>/<benchmark>/logs/*.eval
    for model_dir in RESULTS_DIR.iterdir():
        if not model_dir.is_dir():
            continue

        for bench_dir in model_dir.iterdir():
            if not bench_dir.is_dir():
                continue

            logs_dir = bench_dir / "logs"
            if not logs_dir.exists():
                continue

            for eval_file in logs_dir.glob("*.eval"):
                result = _parse_eval_file(str(eval_file))
                if result is None:
                    continue

                model = result.model
                if model not in results_by_model:
                    results_by_model[model] = []

                # 去重: 保留样本数最多的
                existing = next(
                    (r for r in results_by_model[model] if r.task == result.task),
                    None,
                )
                if existing:
                    if result.samples > existing.samples:
                        results_by_model[model].remove(existing)
                        results_by_model[model].append(result)
                else:
                    results_by_model[model].append(result)

    return results_by_model


def get_model_results(model_name: str) -> List[EvalFileResult]:
    """获取指定模型的所有结果"""
    all_results = scan_results()
    # 模糊匹配模型名
    for model, results in all_results.items():
        if model == model_name or model_name in model or model in model_name:
            return results
    return []


def get_results_for_job(model_id: str, task_names: List[str],
                        start_time: str, end_time: Optional[str] = None) -> List[EvalFileResult]:
    """获取特定 job 时间窗口内的结果（run-scoped results）"""
    from datetime import datetime as dt, timezone

    def _parse_to_utc(s: str) -> dt:
        """Parse ISO datetime string, converting to UTC naive datetime.

        .eval files use UTC timestamps (e.g. '2026-02-28T09:21:23+00:00').
        Job timestamps use local time without tz info (e.g. '2026-02-28T17:20:42').
        Converting both to UTC ensures correct comparison.
        """
        parsed = dt.fromisoformat(s.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            # Has timezone info (e.g. .eval files) — convert to UTC
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            # No timezone info — assume local time, convert to UTC
            local_tz = dt.now(timezone.utc).astimezone().tzinfo
            return parsed.replace(tzinfo=local_tz).astimezone(timezone.utc).replace(tzinfo=None)

    # Parse time bounds
    try:
        t_start = _parse_to_utc(start_time)
    except Exception:
        t_start = dt.min
    try:
        t_end = _parse_to_utc(end_time) if end_time else dt.max
    except Exception:
        t_end = dt.max

    # Normalize model_id: strip provider prefix for matching
    model_short = model_id.split("/")[-1].strip()
    task_set = set(task_names)

    results: List[EvalFileResult] = []
    if not RESULTS_DIR.exists():
        return results

    for model_dir in RESULTS_DIR.iterdir():
        if not model_dir.is_dir():
            continue
        # Match model directory
        dir_name = model_dir.name.strip()
        if model_short not in dir_name and dir_name not in model_short:
            continue

        for bench_dir in model_dir.iterdir():
            if not bench_dir.is_dir():
                continue
            logs_dir = bench_dir / "logs"
            if not logs_dir.exists():
                continue

            for eval_file in logs_dir.glob("*.eval"):
                result = _parse_eval_file(str(eval_file))
                if result is None:
                    continue
                # Filter by task list
                if result.task not in task_set:
                    continue
                # Filter by time window
                try:
                    t_eval = _parse_to_utc(result.timestamp)
                except Exception:
                    continue
                # Allow 60s buffer before start (clock skew)
                # Guard against overflow when sentinel values are used
                from datetime import timedelta
                if t_start != dt.min and t_eval < (t_start - timedelta(seconds=60)):
                    continue
                if t_end != dt.max and t_eval > (t_end + timedelta(seconds=60)):
                    continue

                # Dedup: keep the one with most samples
                existing = next((r for r in results if r.task == result.task), None)
                if existing:
                    if result.samples > existing.samples:
                        results.remove(existing)
                        results.append(result)
                else:
                    results.append(result)

    return results


def get_results_by_eval_files(eval_files: Dict[str, str]) -> List[EvalFileResult]:
    """Get results by directly reading specific .eval files (bug #53).

    Args:
        eval_files: mapping of task_name -> relative path from RESULTS_DIR

    Returns:
        List of parsed results, one per file. Skips files that don't exist or
        fail to parse.
    """
    results: List[EvalFileResult] = []
    for task_name, rel_path in eval_files.items():
        full_path = RESULTS_DIR / rel_path
        if not full_path.exists():
            continue
        result = _parse_eval_file(str(full_path))
        if result is not None:
            results.append(result)
    return results


# 各 benchmark 对应的首选 metric 名称
# 按优先级排列，取第一个匹配的
_METRIC_PRIORITY = {
    "raccoon": ["leakage_rate"],
    "overthink": ["reasoning_overhead", "mean"],
    "cyse2_interpreter_abuse": ["accuracy"],
    "cyse2_prompt_injection": ["accuracy"],
    "cyse2_vulnerability_exploit": ["accuracy"],
    "privacylens_probing": ["accuracy"],
    "privacylens_action": ["leakage"],
    "browse_comp": ["browse_comp_accuracy", "accuracy"],
    "personalized_safety": ["normalized_avg_score"],
    "personalized_safety_context_free": ["normalized_avg_score"],
    "personalized_safety_context_rich": ["normalized_avg_score"],
    "strong_reject": ["strong_reject_metric"],
    "truthfulqa": ["accuracy"],
    "bbq": ["accuracy"],
    "coconot": ["total", "accuracy"],
    "sycophancy": ["inspect_evals/truthfulness", "truthfulness"],
    "ifeval": ["final_acc", "accuracy"],
    "stereoset": ["stereotype_score"],
    "simpleqa": ["correct"],
    "agentharm": ["avg_refusals"],
    "agentharm_benign": ["avg_score"],
    "makemesay": ["win_rate"],
    "bold": ["toxicity"],
    "sec_qa": ["accuracy"],
    "sec_qa_v1": ["accuracy"],
    "sec_qa_v2": ["accuracy"],
    "personality_BFI": ["Extraversion", "Agreeableness", "Conscientiousness"],
    "personality_TRAIT": ["Openness", "Conscientiousness"],
    "iheval": ["mean"],
    "iheval_rule_multi_aligned": ["mean"],
    "chembench": ["all", "accuracy"],
    "clash_eval": ["adherence_rate"],
    "healthbench": ["bootstrap_score", "mean"],
    "healthbench_hard": ["bootstrap_score", "mean"],
    "bfcl": ["accuracy"],
    "wmdp_bio": ["accuracy"],
    "wmdp_chem": ["accuracy"],
    "wmdp_cyber": ["accuracy"],
    "fortress_adversarial": ["ARS__risk_domain__overall"],
    "fortress_benign": ["ORS__risk_domain__overall"],
    "make_me_pay": ["mean"],
    "abstention_bench": ["f1"],
    "mgsm": ["accuracy"],
    "culturalbench_easy": ["accuracy"],
    "culturalbench_hard": ["accuracy"],
    "b3": ["accuracy", "mean"],
    "cve_bench": ["accuracy"],
    "hallulens_task1_precise_wikiqa": ["accuracy"],
    "sosbench": ["mean"],
    "ahb": ["dimension_normalized_avg"],
    "uccb": ["accuracy"],
    "sciknoweval": ["accuracy", "mean"],
    "sevenllm_mcq_zh": ["accuracy"],
    "sevenllm_mcq_en": ["accuracy"],
    "sevenllm_qa_zh": ["rouge_l", "mean"],
    "sevenllm_qa_en": ["rouge_l", "mean"],
    "gdm_approved_directories": ["accuracy", "mean"],
    "gdm_calculator_improvement": ["accuracy", "mean"],
    "gdm_context_length_mod_instrumental_only": ["accuracy", "mean"],
    "gdm_context_length_mod_irreversibility_only": ["accuracy", "mean"],
    "gdm_database_tool": ["accuracy", "mean"],
    "gdm_latency_calculator": ["accuracy", "mean"],
    "gdm_max_messages_calculator": ["accuracy", "mean"],
    "gdm_max_tokens": ["accuracy", "mean"],
    "gdm_oversight_frequency": ["accuracy", "mean"],
    "gdm_read_logs": ["accuracy", "mean"],
    "gdm_turn_off_filters": ["accuracy", "mean"],
    "gdm_oversight_pattern": ["accuracy", "mean"],
    "gdm_classifier_evasion": ["accuracy", "mean"],
    "gdm_cover_your_tracks": ["accuracy", "mean"],
    "gdm_strategic_rule_breaking": ["accuracy", "mean"],
    "mind2web": ["accuracy"],
    "mind2web_sc": ["accuracy"],
    "assistant_bench_closed_book": ["assistant_bench_accuracy", "accuracy"],
    "assistant_bench_closed_book_zero_shot": ["assistant_bench_accuracy", "accuracy"],
    "assistant_bench_web_browser": ["assistant_bench_accuracy", "accuracy"],
    "gaia": ["accuracy"],
    "mm_safety_bench_illegal_activity": ["attack_rate"],
    "cyse3_visual_prompt_injection": ["accuracy"],
    "mathvista": ["accuracy"],
    "mmmu_multiple_choice": ["accuracy"],
    "mmmu_open": ["accuracy"],
    "mmiu": ["accuracy"],
    "docvqa": ["accuracy"],
    "mssbench_chat_if": ["accuracy"],
    "mssbench_chat_qc": ["accuracy"],
    "mssbench_chat_ic": ["accuracy"],
    "mssbench_chat_ic_cap": ["accuracy"],
    "mssbench_embodied_if": ["accuracy"],
    "mssbench_embodied_qc": ["accuracy"],
    "mssbench_embodied_ic": ["accuracy"],
    "mssbench_embodied_ic_cap": ["accuracy"],
    "xstest": ["refusal_rate"],
    "cybench": ["accuracy"],
    "threecb": ["accuracy"],
    # SafeAgentBench: rejection_rate = proportion of unsafe tasks where model refused
    "safeagentbench": ["rejection_rate"],
    "safeagentbench_react": ["rejection_rate"],
    "safeagentbench_visual": ["rejection_rate"],
}

# 通用 fallback 顺序
_FALLBACK_METRICS = ["accuracy", "mean", "leakage_rate", "reasoning_overhead"]


def _extract_metric_value(metrics: dict, task: str) -> Optional[float]:
    """从 metrics 字典中提取主要指标值"""
    # 1. 按 task 特定优先级查找
    priority = _METRIC_PRIORITY.get(task, [])
    for key in priority:
        entry = metrics.get(key)
        if entry and "value" in entry:
            return entry["value"]
        # 尝试带 namespace 前缀的 key (eval_benchmarks/xxx)
        for mk, mv in metrics.items():
            if mk.endswith("/" + key) and isinstance(mv, dict) and "value" in mv:
                return mv["value"]

    # 2. 通用 fallback
    for key in _FALLBACK_METRICS:
        entry = metrics.get(key)
        if entry and isinstance(entry, dict) and "value" in entry:
            return entry["value"]
        for mk, mv in metrics.items():
            if mk.endswith("/" + key) and isinstance(mv, dict) and "value" in mv:
                return mv["value"]

    # 3. 最后兜底：取第一个 metric 的 value
    for mk, mv in metrics.items():
        if isinstance(mv, dict) and "value" in mv:
            return mv["value"]

    return None


def _parse_eval_file(path: str) -> Optional[EvalFileResult]:
    """解析 .eval 文件（zip 格式，包含 header.json）"""
    try:
        proc = subprocess.run(
            ["unzip", "-p", path, "header.json"],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return None

        data = json.loads(proc.stdout)
        if data.get("status") != "success":
            return None

        model = data["eval"]["model"].split("/")[-1]
        if "mockllm" in model.lower():
            return None

        task = data["eval"]["task"].split("/")[-1]
        results = data.get("results", {})
        scores = results.get("scores", [])

        if not scores:
            return None

        # 合并所有 scorer 的 metrics（后面的覆盖前面的）
        metrics = {}
        for scorer in scores:
            metrics.update(scorer.get("metrics", {}))
        acc = _extract_metric_value(metrics, task)
        if acc is None:
            return None

        samples = results.get("completed_samples", 0)
        timestamp = data["eval"].get("created", "")

        return EvalFileResult(
            task=task,
            model=model,
            raw_accuracy=acc,
            samples=samples,
            timestamp=timestamp,
            file_path=os.path.basename(path),
        )
    except Exception:
        return None
