# eval_benchmarks - Local security benchmarks for inspect_ai evaluation
#
# This package is registered as an inspect_ai plugin via entry points
# in pyproject.toml. The _registry module imports all @task functions
# to make them discoverable by inspect_ai.

from . import raccoon  # noqa: F401
from . import overthink  # noqa: F401
from . import privacylens  # noqa: F401
from . import personalized_safety  # noqa: F401
from . import wmdp  # noqa: F401
from . import clash_eval  # noqa: F401
from . import culturalbench  # noqa: F401
from . import mssbench  # noqa: F401
from . import iheval  # noqa: F401
from . import safeagentbench  # noqa: F401
from . import hallulens  # noqa: F401
from . import mm_safety_bench  # noqa: F401
from . import saferag  # noqa: F401
from . import open_agent_safety  # noqa: F401
from . import asb  # noqa: F401
from . import survive_at_all_costs  # noqa: F401
from . import cvalues  # noqa: F401
from . import psysafe  # noqa: F401

__all__ = [
    "raccoon", "overthink", "privacylens", "personalized_safety",
    "wmdp", "clash_eval", "culturalbench", "mssbench", "iheval",
    "safeagentbench", "hallulens", "mm_safety_bench", "saferag",
    "open_agent_safety", "asb", "survive_at_all_costs",
    "cvalues", "psysafe",
]
