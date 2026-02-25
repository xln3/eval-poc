# benchmarks/eval_benchmarks/mssbench/mssbench.py
"""
This file defines the inspect_ai Task for the MSSBench benchmark.
It includes the dataset loader and a custom solver to handle the paired
safe/unsafe evaluation logic.

To run this benchmark, you must set the environment variable:
export MSSBENCH_DATA_ROOT=/path/to/your/mssbench_dataset

The dataset directory should contain 'combined.json' and the image folders ('chat', 'embodied').
"""
import json
import logging
import os

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ChatMessageUser, ContentImage, ContentText, Model, get_model
from inspect_ai.solver import Solver, TaskState, solver

from .prompts import (
    PROMPT_CHAT_IC, PROMPT_CHAT_IC_CAP, PROMPT_CHAT_IF, PROMPT_CHAT_QC,
    PROMPT_EMBODIED_IC, PROMPT_EMBODIED_IC_CAP, PROMPT_EMBODIED_IF,
    PROMPT_EMBODIED_QC,
)
from .scorer import mss_scorer

def _get_data_root() -> str:
    data_root = os.getenv("MSSBENCH_DATA_ROOT")
    if not data_root:
        raise ValueError(
            "The MSSBENCH_DATA_ROOT environment variable is not set. "
            "Please set it to the root directory of the MSSBench dataset, "
            "which contains 'combined.json' and image folders."
        )
    return data_root

# A mapping from setting to the corresponding prompt constants
PROMPT_MAP = {
    "chat": {
        "if": PROMPT_CHAT_IF, "qc": PROMPT_CHAT_QC,
        "ic": PROMPT_CHAT_IC, "ic_cap": PROMPT_CHAT_IC_CAP
    },
    "embodied": {
        "if": PROMPT_EMBODIED_IF, "qc": PROMPT_EMBODIED_QC,
        "ic": PROMPT_EMBODIED_IC, "ic_cap": PROMPT_EMBODIED_IC_CAP
    },
}

def _build_input(image_path: str, prompt_text: str) -> list:
    return [
        ChatMessageUser(
            content=[
                ContentImage(image=image_path),
                ContentText(text=prompt_text),
            ]
        ),
    ]


# MODIFIED: Removed @generator_dataset decorator and changed function implementation
def mss_dataset(
    scenario: str, setting: str, data_file: str, data_root: str
) -> MemoryDataset:
    """
    Dataset loader for MSSBench.

    It reads the combined.json file and returns a MemoryDataset object.
    Each Sample corresponds to one safe/unsafe pair evaluation.
    """
    samples = [] # MODIFIED: Create a list to hold samples

    with open(data_file, "r") as f:
        data = json.load(f)

    items = data.get(scenario, [])
    base_prompt = PROMPT_MAP[scenario][setting]

    expected_counts = {"chat": 1200, "embodied": 760}
    expected = expected_counts.get(scenario)
    if expected is not None and len(items) != expected:
        logging.getLogger(__name__).warning(
            "Expected %s samples for %s, got %s",
            expected,
            scenario,
            len(items),
        )

    for i, d in enumerate(items):
        meta = {"scenario": scenario, "setting": setting}
        
        if scenario == "chat":
            # For 'if' and 'qc' settings, each query is a separate sample
            if setting in ["if", "qc"]:
                for j, query in enumerate(d.get("queries", [])):
                    safe_img_path = os.path.join(
                        data_root, "chat", d["safe_image_path"]
                    )
                    unsafe_img_path = os.path.join(
                        data_root, "chat", d["unsafe_image_path"]
                    )
                    safe_input = _build_input(safe_img_path, base_prompt + query)
                    unsafe_input = _build_input(unsafe_img_path, base_prompt + query)
                    samples.append(Sample(
                        id=f"{scenario}_{setting}_{i}_q_{j}",
                        input=safe_input,
                        metadata={**meta, **d, "query": query, "unsafe_input": unsafe_input},
                    ))
            # For 'ic' settings, the intent is used
            else:
                intent = d.get("intent", "")
                safe_img_path = os.path.join(
                    data_root, "chat", d["safe_image_path"]
                )
                unsafe_img_path = os.path.join(
                    data_root, "chat", d["unsafe_image_path"]
                )
                safe_text = base_prompt + intent
                unsafe_text = base_prompt + intent
                if setting == "ic_cap":
                    unsafe_text += f"\nThe caption is: {d['unsafe_image']}"
                safe_input = _build_input(safe_img_path, safe_text)
                unsafe_input = _build_input(unsafe_img_path, unsafe_text)
                samples.append(Sample(
                    id=f"{scenario}_{setting}_{i}",
                    input=safe_input,
                    metadata={**meta, **d, "unsafe_input": unsafe_input},
                ))
        elif scenario == "embodied":
            # For 'if' and 'qc' settings
            if setting in ["if", "qc"]:
                 for j, (safe_instr, unsafe_instr) in enumerate(zip(d.get("safe_instructions", []), d.get("unsafe_instructions", []))):
                    safe_img_path = os.path.join(data_root, "embodied", d["safe"])
                    unsafe_img_path = os.path.join(data_root, "embodied", d["unsafe"])
                    safe_text = base_prompt + (safe_instr or unsafe_instr)
                    unsafe_text = base_prompt + unsafe_instr
                    safe_input = _build_input(safe_img_path, safe_text)
                    unsafe_input = _build_input(unsafe_img_path, unsafe_text)
                    samples.append(Sample(
                        id=f"{scenario}_{setting}_{i}_instr_{j}",
                        input=safe_input,
                        metadata={
                            **meta, **d,
                            "safe_instruction": safe_instr,
                            "unsafe_instruction": unsafe_instr,
                            "unsafe_input": unsafe_input,
                        },
                    ))
            # For 'ic' settings
            else:
                 safe_img_path = os.path.join(data_root, "embodied", d["safe"])
                 unsafe_img_path = os.path.join(data_root, "embodied", d["unsafe"])
                 safe_instr = d.get("safe_instruction", "")
                 unsafe_instr = d.get("unsafe_instruction", "")
                 safe_text = base_prompt + safe_instr
                 unsafe_text = base_prompt + unsafe_instr
                 if setting == "ic_cap":
                    safe_text += f"\nThe caption is: {d['observation_safe']}"
                    unsafe_text += f"\nThe caption is: {d['observation_unsafe']}"
                 safe_input = _build_input(safe_img_path, safe_text)
                 unsafe_input = _build_input(unsafe_img_path, unsafe_text)
                 samples.append(Sample(
                    id=f"{scenario}_{setting}_{i}",
                    input=safe_input,
                    metadata={**meta, **d, "unsafe_input": unsafe_input},
                ))

    return MemoryDataset(samples) # MODIFIED: Return the final MemoryDataset


@solver
def mss_solver() -> Solver:
    async def solve(state: TaskState, generate) -> TaskState:
        """
        Custom solver for MSSBench.

        For each sample, this solver calls the target model twice:
        1. For the 'safe' scenario (safe image + safe instruction).
        2. For the 'unsafe' scenario (unsafe image + unsafe instruction).

        It stores both outputs in the task state's metadata for the scorer.
        """
        # Get metadata from the sample (TaskState stores it in metadata)
        unsafe_input = state.metadata.get("unsafe_input")
        if not unsafe_input:
            raise ValueError("Missing unsafe_input in sample metadata")

        # Call the model for both scenarios (bypass task generate to run two prompts)
        model = get_model()
        safe_response = await model.generate(state.input)
        unsafe_response = await model.generate(unsafe_input)

        # Store outputs in metadata for the scorer to access
        state.metadata["outputs"] = {
            "safe": safe_response.completion,
            "unsafe": unsafe_response.completion,
        }
        
        # The final output can be a placeholder or one of the responses
        state.output = safe_response
        return state
    
    return solve

def _create_mss_task(
    scenario: str,
    setting: str = "if",
    judge_model: str | Model | None = None,
) -> Task:
    """A factory function to create MSSBench tasks."""
    data_root = _get_data_root()
    data_file = os.path.join(data_root, "combined.json")
    if not os.path.exists(data_file):
        raise FileNotFoundError(
            f"Data file not found: {data_file}. "
            f"Ensure MSSBENCH_DATA_ROOT is set correctly and 'combined.json' exists."
        )

    return Task(
        dataset=mss_dataset(
            scenario=scenario,
            setting=setting,
            data_file=data_file,
            data_root=data_root,
        ),
        solver=mss_solver(),
        scorer=mss_scorer(judge_model=judge_model),
        # Metrics can be defined here, e.g., to average the score
    )
# Define and register the tasks for chat and embodied scenarios
@task(name="mssbench_chat")
def mssbench_chat(
    setting: str = "if",
    judge_model: str | Model | None = None,
) -> Task:
    """MSSBench task for the 'Chat' scenario."""
    return _create_mss_task("chat", setting, judge_model=judge_model)

@task(name="mssbench_embodied")
def mssbench_embodied(
    setting: str = "if",
    judge_model: str | Model | None = None,
) -> Task:
    """MSSBench task for the 'Embodied' scenario."""
    return _create_mss_task("embodied", setting, judge_model=judge_model)