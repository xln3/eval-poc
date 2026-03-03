# ruff: noqa: F401
# Import all @task functions to register them with inspect_ai's registry.
# When this module is loaded via the entry point, all tasks become discoverable.

from eval_benchmarks.raccoon import raccoon
from eval_benchmarks.overthink import overthink
from eval_benchmarks.privacylens import privacylens_probing, privacylens_probing_vignette, privacylens_action
from eval_benchmarks.personalized_safety import personalized_safety, personalized_safety_context_free, personalized_safety_context_rich, personalized_safety_youth, personalized_safety_elderly, personalized_safety_healthcare
from eval_benchmarks.wmdp import wmdp_cyber, wmdp_bio, wmdp_chem
from eval_benchmarks.clash_eval import clash_eval
from eval_benchmarks.culturalbench import culturalbench_easy, culturalbench_hard
from eval_benchmarks.mssbench import mssbench_chat, mssbench_embodied
from eval_benchmarks.iheval import iheval
from eval_benchmarks.safeagentbench import safeagentbench, safeagentbench_react, safeagentbench_visual
from eval_benchmarks.hallulens import (
    hallulens_task1_precise_wikiqa,
    hallulens_task2_longwiki,
    hallulens_task3_nonsense_mixed_entities,
    hallulens_task3_round_robin_nonsense_name,
)
from eval_benchmarks.mm_safety_bench import mm_safety_bench_illegal_activity
from eval_benchmarks.saferag import saferag, saferag_sn, saferag_icc, saferag_sa, saferag_wdos
from eval_benchmarks.survive_at_all_costs import survive_at_all_costs
from eval_benchmarks.open_agent_safety import open_agent_safety
from eval_benchmarks.cvalues import cvalues
from eval_benchmarks.asb import asb, asb_ipi
from eval_benchmarks.psysafe import psysafe
from eval_benchmarks.survivalbench import survivalbench
