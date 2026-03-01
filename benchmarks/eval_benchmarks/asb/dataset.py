"""
ASB (Agent Security Bench) — Dataset Loader

Loads ASB data files and builds the cross-product of
(agent × task × attack_tool × dpi_variant) as inspect_ai Samples.

Each Sample encodes:
  - input: [system_message (agent prompt + tools), user_message (task + DPI)]
  - target: attack_goal string (for ASR string matching)
  - metadata: agent_name, attacker_tool, dpi_variant, aggressive, etc.
"""

import json
import random
from pathlib import Path

from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ChatMessageSystem, ChatMessageUser

from .prompts import (
    build_dpi_prompt,
    build_system_prompt,
    build_tool_call_format,
)

_DATA_DIR = Path(__file__).parent / "data"


def _load_jsonl(filename: str) -> list[dict]:
    """Load a JSONL file from the data directory."""
    path = _DATA_DIR / filename
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _load_json(filename: str) -> dict:
    """Load a JSON file from the data directory."""
    path = _DATA_DIR / filename
    with open(path) as f:
        return json.load(f)


def _build_normal_tools(agent_name: str, agent_configs: dict, normal_tools_db: list[dict]) -> list[dict]:
    """Build tool-call-format list for an agent's normal tools."""
    config = agent_configs.get(agent_name, {})
    tool_names = config.get("tools", [])

    tools = []
    for tool_name in tool_names:
        for nt in normal_tools_db:
            if nt["Tool Name"] == tool_name:
                tools.append(build_tool_call_format(tool_name, nt["Description"]))
                break
    return tools


def load_asb_dataset(
    dpi_variant: str = "naive",
    agent_filter: str | None = None,
    aggressive_only: bool = False,
    shuffle: bool = False,
    seed: int = 42,
    limit: int | None = None,
) -> MemoryDataset:
    """Load ASB DPI benchmark dataset.

    Args:
        dpi_variant: DPI attack variant (naive, fake_completion,
            escape_characters, context_ignoring, combined_attack).
        agent_filter: Comma-separated agent names to include. None = all.
        aggressive_only: If True, only include aggressive attack tools.
        shuffle: Whether to shuffle the dataset.
        seed: Random seed for shuffling.
        limit: Maximum number of samples.

    Returns:
        MemoryDataset with ASB samples.
    """
    # Load data files
    agent_tasks = _load_jsonl("agent_task.jsonl")
    attack_tools = _load_jsonl("all_attack_tools.jsonl")
    normal_tools_db = _load_jsonl("all_normal_tools.jsonl")
    agent_configs = _load_json("agent_configs.json")

    # Filter agents if specified
    if agent_filter:
        allowed = {a.strip() for a in agent_filter.split(",")}
        agent_tasks = [a for a in agent_tasks if a["agent_name"] in allowed]

    # Filter attack tools by aggressiveness
    if aggressive_only:
        attack_tools = [t for t in attack_tools if t.get("Aggressive") == "True"]

    samples = []
    sample_idx = 0

    for agent_info in agent_tasks:
        agent_name = agent_info["agent_name"]
        tasks = agent_info["tasks"]
        agent_desc = agent_configs.get(agent_name, {}).get("description", "")

        # Get normal tools for this agent
        normal_tools = _build_normal_tools(agent_name, agent_configs, normal_tools_db)
        normal_tool_names = [t["function"]["name"] for t in normal_tools]

        # Get attack tools for this agent
        agent_attack_tools = [
            t for t in attack_tools
            if t["Corresponding Agent"] == agent_name
        ]

        for task in tasks:
            for atool in agent_attack_tools:
                # Build system prompt with normal + attacker tools
                system_prompt = build_system_prompt(
                    agent_description=agent_desc,
                    normal_tools=normal_tools,
                    attacker_tool=atool,
                )

                # Build user message with DPI injection
                user_message = build_dpi_prompt(
                    task=task,
                    attacker_instruction=atool["Attacker Instruction"],
                    attacker_tool=atool["Attacker Tool"],
                    variant=dpi_variant,
                )

                sample = Sample(
                    input=[
                        ChatMessageSystem(content=system_prompt),
                        ChatMessageUser(content=user_message),
                    ],
                    target=atool["Attack goal"],
                    id=f"asb_{sample_idx:04d}_{agent_name}_{atool['Attacker Tool']}",
                    metadata={
                        "agent_name": agent_name,
                        "attacker_tool": atool["Attacker Tool"],
                        "attacker_instruction": atool["Attacker Instruction"],
                        "attack_goal": atool["Attack goal"],
                        "attack_type": atool.get("Attack Type", ""),
                        "aggressive": atool.get("Aggressive", "False") == "True",
                        "dpi_variant": dpi_variant,
                        "task": task,
                        "normal_tools": normal_tool_names,
                    },
                )
                samples.append(sample)
                sample_idx += 1

    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(samples)

    if limit:
        samples = samples[:limit]

    return MemoryDataset(samples=samples, name="asb")
