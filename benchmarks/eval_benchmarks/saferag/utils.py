from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
import os
import sys
import threading

_CWD_LOCK = threading.Lock()


@lru_cache(maxsize=1)
def resolve_saferag_root() -> Path:
    env_root = os.environ.get("SAFERAG_ROOT")
    if env_root:
        root = Path(env_root).expanduser().resolve()
    else:
        root = Path(__file__).resolve().parents[4] / "SafeRAG"
        root = root.resolve()

    if not root.exists():
        raise FileNotFoundError(
            "SafeRAG root not found. Set SAFERAG_ROOT or place SafeRAG next to safety-benchmarks."
        )
    return root


def ensure_saferag_on_path() -> None:
    root = resolve_saferag_root()
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


@contextmanager
def saferag_cwd():
    root = resolve_saferag_root()
    with _CWD_LOCK:
        previous = os.getcwd()
        os.chdir(root)
        try:
            yield
        finally:
            os.chdir(previous)


def run_with_saferag_cwd(func, *args, **kwargs):
    with saferag_cwd():
        return func(*args, **kwargs)
