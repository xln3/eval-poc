"""Benchmark health check service — validates task discoverability and dependencies."""

from __future__ import annotations

import asyncio
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from ..config import PROJECT_ROOT

logger = logging.getLogger(__name__)

# Cache duration in seconds
_CACHE_TTL = 300  # 5 minutes
_cache: dict[str, Any] | None = None
_cache_ts: float = 0
_cache_lock = asyncio.Lock()

VENVS_DIR = PROJECT_ROOT / ".venvs"


def _check_venv_ready(benchmark_name: str) -> bool:
    """Check if venv exists and has inspect binary."""
    inspect_path = VENVS_DIR / benchmark_name / "bin" / "inspect"
    return inspect_path.exists()


def _check_task_discoverable(benchmark_name: str, task_path: str) -> tuple[bool, str | None]:
    """Check if a task is discoverable via the inspect_ai registry.

    Task paths like 'inspect_evals/agentharm_benign' or 'eval_benchmarks/asb_ipi'
    are resolved through inspect_ai's @task decorator registry, NOT as direct
    Python module imports (task functions are not submodules).

    Returns (discoverable, error_message).
    """
    python_path = VENVS_DIR / benchmark_name / "bin" / "python"
    if not python_path.exists():
        return False, "Python binary not found in venv"

    # Use inspect_ai's registry_lookup to verify the task is registered.
    # This mirrors how `inspect eval <task_path>` resolves tasks at runtime.
    dotted_path = task_path.replace("/", ".")
    check_code = (
        f"from inspect_ai._eval.registry import registry_lookup; "
        f"registry_lookup('task', '{dotted_path}')"
    )
    try:
        result = subprocess.run(
            [str(python_path), "-c", check_code],
            capture_output=True, text=True, timeout=15,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode == 0:
            return True, None
        else:
            stderr = result.stderr.strip()
            lines = stderr.splitlines()
            error_msg = lines[-1] if lines else "Import failed"
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            return False, error_msg
    except subprocess.TimeoutExpired:
        return False, "Import check timed out"
    except Exception as e:
        return False, str(e)


def _check_dependencies(config: dict) -> dict[str, bool | None]:
    """Check benchmark dependencies (Docker, HF_TOKEN, etc.).

    Returns dict mapping dependency name to status:
      True = available, False = missing, None = not required.
    """
    deps: dict[str, bool | None] = {}

    # Docker requirement
    if config.get("needs_docker", False):
        try:
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, timeout=5,
            )
            deps["docker"] = result.returncode == 0
        except Exception:
            deps["docker"] = False
    else:
        deps["docker"] = None

    return deps


def _compute_status(venv_ready: bool, tasks_info: dict, deps: dict) -> str:
    """Compute overall benchmark health status."""
    if not venv_ready:
        return "unavailable"

    all_discoverable = all(t.get("discoverable", False) for t in tasks_info.values())
    any_discoverable = any(t.get("discoverable", False) for t in tasks_info.values())

    # Check if required dependencies are met
    deps_ok = all(v is None or v for v in deps.values())

    if all_discoverable and deps_ok:
        return "healthy"
    elif any_discoverable:
        return "degraded"
    else:
        return "unavailable"


async def get_benchmark_health(force: bool = False) -> dict[str, Any]:
    """Get health status for all benchmarks. Cached for 5 minutes.

    Returns:
        Dict with 'benchmarks', 'summary', and 'checked_at' keys.
    """
    global _cache, _cache_ts

    async with _cache_lock:
        now = time.time()
        if _cache and not force and (now - _cache_ts) < _CACHE_TTL:
            return _cache

        # Run health check in thread pool to avoid blocking event loop
        result = await asyncio.get_event_loop().run_in_executor(
            None, _compute_health
        )
        _cache = result
        _cache_ts = time.time()
        return result


def _compute_health() -> dict[str, Any]:
    """Compute health for all benchmarks (blocking, runs in thread pool)."""
    from .catalog_service import get_all_benchmarks

    import yaml
    catalog_path = PROJECT_ROOT / "benchmarks" / "catalog.yaml"
    try:
        with open(catalog_path, "r") as f:
            catalog = yaml.safe_load(f)
    except Exception:
        catalog = {}

    benchmark_configs = catalog.get("benchmarks", {})
    benchmarks_result: dict[str, Any] = {}
    summary = {"healthy": 0, "degraded": 0, "unavailable": 0}

    for bm_name, config in benchmark_configs.items():
        venv_ready = _check_venv_ready(bm_name)

        # Check each task
        tasks_info: dict[str, dict] = {}
        for task_entry in config.get("tasks", []):
            if isinstance(task_entry, dict):
                task_name = task_entry.get("name", "")
                task_path = task_entry.get("path", "")
            else:
                task_name = task_entry
                task_path = config.get("module", "")

            if venv_ready and task_path:
                discoverable, error = _check_task_discoverable(bm_name, task_path)
            else:
                discoverable = False
                error = "Venv not ready" if not venv_ready else "No task path"

            tasks_info[task_name] = {
                "discoverable": discoverable,
                "import_error": error,
            }

        # Check dependencies
        deps = _check_dependencies(config)

        # Compute status
        status = _compute_status(venv_ready, tasks_info, deps)
        summary[status] = summary.get(status, 0) + 1

        benchmarks_result[bm_name] = {
            "status": status,
            "venv_ready": venv_ready,
            "tasks": tasks_info,
            "dependencies": deps,
        }

    from datetime import datetime, timezone
    return {
        "benchmarks": benchmarks_result,
        "summary": summary,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
