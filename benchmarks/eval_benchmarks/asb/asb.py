"""
Agent Security Bench (ASB): LLM Agent Resistance to Adversarial Attacks

Based on:
    Zhang et al. "Agent Security Bench (ASB): Formalizing and Benchmarking
    Attacks and Defenses in LLM-based Agents" (ICLR 2025)
    https://github.com/agiresearch/ASB

This benchmark evaluates whether LLM agents can resist Direct Prompt
Injection (DPI) attacks across 10 agent scenarios. The attack injects
malicious tool-use instructions into the user message, attempting to
hijack the agent's workflow.

Scoring:
  - ASR (Attack Success Rate): string match of attack goal in response
    1.0 = compromised, 0.0 = safe
  - Refusal: LLM judge binary — 0 (refused=safe) / 1 (complied=unsafe)
  - Lower ASR = safer model

LIMITATION: The full ASB paper defines multiple attack types (DPI, IPI,
mixed attacks). This implementation covers only DPI (Direct Prompt
Injection). IPI and mixed attack types are planned for future versions.

Usage:
    inspect eval eval_benchmarks/asb --model openai/gpt-4o
    inspect eval eval_benchmarks/asb --model openai/gpt-4o -T dpi_variant=naive --limit 20
"""

import os
import warnings

from inspect_ai import Task, task
from inspect_ai.model import GenerateConfig
from inspect_ai.solver import generate

from .dataset import load_asb_dataset
from .scorer import asb_scorer

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048


@task
def asb(
    dpi_variant: str = "naive",
    agent_filter: str | None = None,
    aggressive_only: bool = False,
    judge_model: str | None = None,
    judge_max_tokens: int = 256,
    judge_temperature: float = 0.0,
    limit: int | None = None,
    shuffle: bool = False,
    seed: int = 42,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> Task:
    """Agent Security Bench — DPI Attack Evaluation.

    Evaluates LLM agent resistance to Direct Prompt Injection attacks
    across 10 diverse agent scenarios (financial, medical, legal, etc.).

    DPI variants:
    - naive: Direct injection appended to task
    - fake_completion: "Answer: task complete." prefix
    - escape_characters: Newline prefix
    - context_ignoring: "Ignore previous instructions." prefix
    - combined_attack: All of the above combined

    Args:
        dpi_variant: DPI attack variant (default: naive).
        agent_filter: Comma-separated agent names to include (default: all).
        aggressive_only: Only include aggressive attack tools.
        judge_model: Model for refusal evaluation. Reads JUDGE_MODEL_NAME
            env var if not specified.
        judge_max_tokens: Max tokens for judge.
        judge_temperature: Temperature for judge model.
        limit: Maximum number of samples.
        shuffle: Whether to shuffle samples.
        seed: Random seed.
        temperature: Generation temperature for evaluated model.
        max_tokens: Max tokens for model response.

    Returns:
        Task object for running the evaluation.
    """
    # Resolve judge model
    if judge_model is None:
        judge_env = os.getenv("JUDGE_MODEL_NAME")
        if not judge_env:
            warnings.warn(
                "[asb] JUDGE_MODEL_NAME not set, falling back to 'gpt-4o'.",
                stacklevel=2,
            )
        judge_model = f"openai/{judge_env}" if judge_env else "openai/gpt-4o"

    # Load dataset
    dataset = load_asb_dataset(
        dpi_variant=dpi_variant,
        agent_filter=agent_filter,
        aggressive_only=aggressive_only,
        shuffle=shuffle,
        seed=seed,
        limit=limit,
    )

    return Task(
        dataset=dataset,
        solver=[generate()],
        scorer=asb_scorer(
            judge_model=judge_model,
            judge_max_tokens=judge_max_tokens,
            judge_temperature=judge_temperature,
        ),
        config=GenerateConfig(
            temperature=temperature,
            max_tokens=max_tokens,
        ),
        version="1.0.0",
    )
