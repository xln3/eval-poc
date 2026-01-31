# Local benchmarks package

# Import local benchmarks so they can be discovered by inspect_ai
from . import raccoon  # noqa: F401
from . import overthink  # noqa: F401

__all__ = ["raccoon", "overthink"]
