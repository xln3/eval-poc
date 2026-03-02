"""评测结果 API"""

import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from ..config import RESULTS_DIR
from ..models.schemas import ModelResultSummary, ModelResult
from ..services.score_service import get_all_model_results, get_model_detail, get_job_detail
from ..services.result_reader import get_model_results, get_results_for_job
from ..services.eval_runner import get_job

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("", response_model=List[ModelResultSummary])
def list_results():
    """列出所有模型的评测结果摘要"""
    return get_all_model_results()


@router.get("/by-job/{job_id}")
def get_result_by_job(job_id: str):
    """获取特定 evaluation job 的结果（run-scoped）"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="未找到该评测任务")
    result = get_job_detail(job)
    if not result:
        raise HTTPException(status_code=404, detail="该评测任务暂无结果数据")
    return result


@router.get("/by-job/{job_id}/tasks/{task}/samples")
def get_job_task_samples(
    job_id: str,
    task: str,
    risk_level: Optional[str] = Query(None),
):
    """获取特定 job 的某个 task 的样本数据"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="未找到该评测任务")

    # Prefer precise file-path matching (bug #53), fall back to time-window
    model_short = job.model_id.split("/")[-1].strip()
    task_progress = next((t for t in job.tasks if t.task_name == task), None)
    eval_file = None
    if task_progress and task_progress.eval_file:
        from ..config import RESULTS_DIR
        candidate = RESULTS_DIR / task_progress.eval_file
        if candidate.exists():
            eval_file = str(candidate)
    if not eval_file:
        eval_file = _find_eval_file_for_job(model_short, task, job.created_at, job.completed_at)
    if not eval_file:
        raise HTTPException(status_code=404, detail="未找到 .eval 文件")

    samples = _extract_samples(eval_file)
    if risk_level:
        samples = [s for s in samples if s.get("risk_level", "").upper() == risk_level.upper()]

    return {
        "model": model_short,
        "task": task,
        "job_id": job_id,
        "total_samples": len(samples),
        "samples": samples,
    }


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


def _task_matches_filename(task: str, filename_stem: str) -> bool:
    """Check if a task name matches an eval filename stem.

    Filename pattern: {ISO-timestamp}_{task-hyphenated}_{hash}
    The three parts are separated by underscores. Timestamps use hyphens
    (no underscores), and hashes are alphanumeric (no underscores).
    Task names in code use underscores; in filenames they use hyphens.
    """
    parts = filename_stem.split("_")
    if len(parts) >= 3:
        # Extract the task portion (middle part between timestamp and hash)
        file_task = "_".join(parts[1:-1])
        norm_task = task.replace("_", "-")
        norm_file_task = file_task.replace("_", "-")
        return norm_task == norm_file_task
    # Unexpected format: fall back to substring match
    norm_task = task.replace("_", "-")
    norm_stem = filename_stem.replace("_", "-")
    return norm_task in norm_stem


def _parse_to_utc(s: str):
    """Parse ISO datetime string, converting to UTC naive datetime.

    .eval files use UTC timestamps (e.g. '2026-02-28T09:21:23+00:00').
    Job timestamps use local time without tz info (e.g. '2026-02-28T17:20:42').
    Converting both to UTC ensures correct comparison.
    """
    from datetime import datetime as dt, timezone
    parsed = dt.fromisoformat(s.replace("Z", "+00:00"))
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        local_tz = dt.now(timezone.utc).astimezone().tzinfo
        return parsed.replace(tzinfo=local_tz).astimezone(timezone.utc).replace(tzinfo=None)


def _find_eval_file_for_job(model: str, task: str, start_time: str, end_time: Optional[str]) -> Optional[str]:
    """Locate the .eval file for a model/task within a job's time window."""
    import zipfile
    from datetime import datetime as dt, timedelta

    try:
        t_start = _parse_to_utc(start_time)
    except Exception:
        t_start = dt.min
    try:
        t_end = _parse_to_utc(end_time) if end_time else dt.max
    except Exception:
        t_end = dt.max

    if not RESULTS_DIR.exists():
        return None

    best_file = None
    best_time = None

    for model_dir in RESULTS_DIR.iterdir():
        if not model_dir.is_dir():
            continue
        if model not in model_dir.name and model_dir.name not in model:
            continue
        for bench_dir in model_dir.iterdir():
            if not bench_dir.is_dir():
                continue
            logs_dir = bench_dir / "logs"
            if not logs_dir.exists():
                continue
            for eval_file in logs_dir.glob("*.eval"):
                if not _task_matches_filename(task, eval_file.stem):
                    continue
                # Check timestamp from header using zipfile (not subprocess)
                try:
                    with zipfile.ZipFile(str(eval_file), "r") as zf:
                        if "header.json" not in zf.namelist():
                            continue
                        header = json.loads(zf.read("header.json"))
                    ts = header.get("eval", {}).get("created", "")
                    t_eval = _parse_to_utc(ts)
                    in_window = (t_start == dt.min or t_eval >= (t_start - timedelta(seconds=60))) and \
                               (t_end == dt.max or t_eval <= (t_end + timedelta(seconds=60)))
                    if in_window:
                        if best_time is None or t_eval > best_time:
                            best_file = str(eval_file)
                            best_time = t_eval
                except Exception:
                    continue

    return best_file


def _find_eval_file(model: str, task: str) -> Optional[str]:
    """Locate the most recent .eval file for a model/task combination."""
    if not RESULTS_DIR.exists():
        return None

    best_file = None
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
                if _task_matches_filename(task, eval_file.stem):
                    # Filenames start with ISO timestamps; pick the latest
                    if best_file is None or eval_file.name > best_file.name:
                        best_file = eval_file
    return str(best_file) if best_file else None


def _extract_samples(eval_file_path: str) -> list:
    """Extract per-sample data from .eval zip file.

    inspect_ai .eval files are zips containing:
      - samples/<id>_epoch_<n>.json  — individual sample files (full data)
      - summaries.json               — sample list with scores but no output
      - header.json                   — aggregate metrics only
    """
    import zipfile

    samples = []
    try:
        with zipfile.ZipFile(eval_file_path, "r") as zf:
            names = zf.namelist()

            # Strategy 1: Read individual sample files from samples/ dir
            sample_files = sorted(
                [n for n in names if n.startswith("samples/") and n.endswith(".json")]
            )
            if sample_files:
                # Build a score lookup from summaries.json (scores may be
                # missing from individual sample files in some benchmarks)
                score_lookup = {}
                if "summaries.json" in names:
                    try:
                        summaries = json.loads(zf.read("summaries.json"))
                        for s in (summaries if isinstance(summaries, list) else []):
                            sid = s.get("id")
                            if sid is not None:
                                score_lookup[str(sid)] = s.get("scores", {})
                    except Exception:
                        pass

                for i, fname in enumerate(sample_files):
                    try:
                        raw = json.loads(zf.read(fname))
                        # Merge scores from summaries if sample's own scores empty
                        if not raw.get("scores") and str(raw.get("id", "")) in score_lookup:
                            raw["scores"] = score_lookup[str(raw["id"])]
                        samples.append(_normalize_sample(i, raw))
                    except Exception:
                        continue
                return samples

            # Strategy 2: Fall back to summaries.json (has scores but no output)
            if "summaries.json" in names:
                try:
                    summaries = json.loads(zf.read("summaries.json"))
                    for i, s in enumerate(summaries if isinstance(summaries, list) else []):
                        samples.append(_normalize_sample(i, s))
                    if samples:
                        return samples
                except Exception:
                    pass

            # Strategy 3: Fall back to header.json aggregate
            if "header.json" in names:
                try:
                    header = json.loads(zf.read("header.json"))
                    completed = header.get("results", {}).get("completed_samples", 0)
                    scores = header.get("results", {}).get("scores", [])
                    metrics = {}
                    for scorer in scores:
                        metrics.update(scorer.get("metrics", {}))
                    return [{
                        "sample_id": "summary",
                        "score": next(
                            (v["value"] for v in metrics.values()
                             if isinstance(v, dict) and "value" in v),
                            0,
                        ),
                        "total_samples": completed,
                        "input": "",
                        "output": "",
                        "risk_level": "UNKNOWN",
                        "note": "Per-sample data not available; showing aggregate summary",
                    }]
                except Exception:
                    pass

    except Exception:
        pass

    return samples


def _normalize_sample(idx: int, raw: dict) -> dict:
    """Normalize a raw sample dict to a consistent format.

    Handles inspect_ai sample format where:
      - scores: dict of scorer_name → {value, answer, ...}
      - output: {model, choices: [{message: {content: ...}}], completion, ...}
      - input: str | list of message dicts
    """
    # --- Extract score ---
    scores_dict = raw.get("scores", {})
    score = None
    if isinstance(scores_dict, dict) and scores_dict:
        # Take the first scorer's value
        first_scorer = next(iter(scores_dict.values()), {})
        if isinstance(first_scorer, dict):
            score = first_scorer.get("value")
    # Legacy format fallback
    if score is None:
        score = raw.get("score", 0)
    if isinstance(score, dict):
        score = score.get("value", 0)
    # Normalize string scores to numeric
    if isinstance(score, str):
        score_map = {"C": 1.0, "I": 0.0, "safe": 1.0, "unsafe": 0.0}
        score = score_map.get(score, 0)

    # --- Extract input ---
    input_text = raw.get("input", "")
    if isinstance(input_text, list):
        # Messages format
        parts = []
        for m in input_text:
            if isinstance(m, dict):
                content = m.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        c.get("text", "") for c in content
                        if isinstance(c, dict) and c.get("type") == "text"
                    )
                parts.append(content)
        input_text = "\n".join(parts)

    # --- Extract output ---
    output_raw = raw.get("output", raw.get("target", ""))
    output_text = ""
    if isinstance(output_raw, dict):
        # inspect_ai format: {model, choices: [{message: {content}}], completion}
        completion = output_raw.get("completion", "")
        if completion:
            output_text = completion
        else:
            choices = output_raw.get("choices", [])
            if choices and isinstance(choices[0], dict):
                msg = choices[0].get("message", {})
                content = msg.get("content", "")
                if isinstance(content, list):
                    # Multi-part content (text + reasoning)
                    text_parts = []
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            text_parts.append(c.get("text", ""))
                    output_text = "\n".join(text_parts)
                elif isinstance(content, str):
                    output_text = content
    elif isinstance(output_raw, str):
        output_text = output_raw

    # Fallback: extract last assistant message from messages array
    if not output_text:
        messages = raw.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, list):
                    text_parts = []
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            text_parts.append(c.get("text", ""))
                    output_text = "\n".join(text_parts)
                elif isinstance(content, str):
                    output_text = content
                break

    # --- Determine risk level from score ---
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
        "score": score if isinstance(score, (int, float)) else 0,
        "input": str(input_text)[:2000],
        "output": str(output_text)[:2000],
        "risk_level": risk,
        "metadata": raw.get("metadata", {}),
    }
