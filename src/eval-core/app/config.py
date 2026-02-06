"""路径配置"""

from pathlib import Path

# 项目根目录 (eval-poc/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# 关键路径
CATALOG_PATH = PROJECT_ROOT / "benchmarks" / "catalog.yaml"
RESULTS_DIR = PROJECT_ROOT / "results"
RUN_EVAL_SCRIPT = PROJECT_ROOT / "run-eval.py"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_JSON = DATA_DIR / "models.json"
REPORTS_DIR = PROJECT_ROOT / "reports"
