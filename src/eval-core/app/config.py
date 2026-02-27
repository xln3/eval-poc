"""路径配置"""

import os
from pathlib import Path

# 项目根目录 (eval-poc/)
# In Docker, PROJECT_ROOT resolves incorrectly (flat directory structure),
# so allow override via environment variable.
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", "")).resolve() \
    if os.environ.get("PROJECT_ROOT") \
    else Path(__file__).resolve().parent.parent.parent.parent

# 关键路径 — all overridable via env vars for Docker deployment
CATALOG_PATH = Path(os.environ["CATALOG_PATH"]) if os.environ.get("CATALOG_PATH") \
    else PROJECT_ROOT / "benchmarks" / "catalog.yaml"
RESULTS_DIR = Path(os.environ["RESULTS_DIR"]) if os.environ.get("RESULTS_DIR") \
    else PROJECT_ROOT / "results"
RUN_EVAL_SCRIPT = PROJECT_ROOT / "run-eval.py"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_JSON = DATA_DIR / "models.json"
REPORTS_DIR = Path(os.environ["REPORTS_DIR"]) if os.environ.get("REPORTS_DIR") \
    else PROJECT_ROOT / "reports"
