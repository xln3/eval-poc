# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Agent Security Evaluation Framework** (eval-poc) - a unified interface for running multiple security benchmarks on LLMs using the inspect_ai framework. The core innovation is normalizing heterogeneous benchmark results to a unified safety score (0-100, where higher = safer).

## Essential Commands

```bash
# Run all benchmarks for a model
./run-eval.py --run-all --model <model_name>

# Run specific benchmark or task
./run-eval.py strong_reject --model <model_name>
./run-eval.py cyberseceval_2:cyse2_interpreter_abuse --model <model_name>

# Environment setup (without running tests)
./run-eval.py --setup-all
./run-eval.py --setup <benchmark>

# Preflight checks only
./run-eval.py --preflight

# Dry run - preview commands without executing
./run-eval.py --run-all --model <model_name> --dry-run

# Limit samples per task (useful for testing)
./run-eval.py --model <model_name> --limit 10
```

## Using Safety-Lookahead

For proactive safety evaluation using world model lookahead, use the `run-eval-salt.py` entry point:

```bash
# Basic usage with safety-lookahead
./run-eval-salt.py --with-safety-lookahead --model safety-lookahead/qwen3-8b strong_reject

# With separate world model (e.g., use GPT-4o for safety evaluation)
./run-eval-salt.py --with-safety-lookahead --world-model openai/gpt-4o --model safety-lookahead/qwen3-8b strong_reject

# With safety analysis output (detailed logs for analysis)
./run-eval-salt.py --with-safety-lookahead --safety-output-dir results/safety_analysis --model safety-lookahead/qwen3-8b strong_reject

# Run all benchmarks with safety-lookahead
./run-eval-salt.py --run-all --with-safety-lookahead --model safety-lookahead/qwen3-8b
```

**Safety-Lookahead Options:**
- `--with-safety-lookahead`: Enable safety-lookahead functionality (auto-installs package)
- `--world-model <model>`: Use a separate, more capable model for world model evaluation
- `--safety-output-dir <dir>`: Store detailed safety analysis logs in JSONL format

**Environment Variables (optional):**
- `SAFETY_LOOKAHEAD_ENABLED`: Enable/disable safety lookahead (set by --with-safety-lookahead)
- `SAFETY_LOOKAHEAD_N`: Number of candidate actions to evaluate (default: 3)
- `SAFETY_LOOKAHEAD_MASK`: Tool call masking strategy: "keywords" (fast), "rewriting", or "none"
- `SAFETY_LOOKAHEAD_WORLD_MODEL`: Separate model for world model queries (set by --world-model)
- `SAFETY_LOOKAHEAD_OUTPUT`: Path to safety analysis JSONL output file (set by --safety-output-dir)

## Architecture

### Benchmark Execution Pipeline

```
run-eval.py (orchestrator)
    │
    ├── 1. Preflight checks (benchmarks/preflight.py)
    │     └── Validates: Docker, Kubernetes, HF_TOKEN, dataset access, judge model
    │
    ├── 2. Environment setup (per-benchmark isolation)
    │     └── Creates .venvs/<benchmark>/ with specific Python version and deps
    │
    ├── 3. Task execution via inspect_ai
    │     └── Runs: inspect eval <task> --model <model>
    │
    └── 4. Result aggregation
          └── Stores .eval files in results/<model>/<benchmark>/logs/
```

### Key Architectural Patterns

**1. Benchmark Routing via Catalog**
- `benchmarks/catalog.yaml` is the central registry - all benchmarks must be registered here
- Each entry defines: source, module path, python version, extras, tasks
- Task resolution handles formats like `benchmark:task` or just `benchmark`

**2. Per-Benchmark Virtual Environments**
- Each benchmark gets isolated environment at `.venvs/<benchmark_name>/`
- Uses `uv` for fast package management
- Some benchmarks need special Python versions (e.g., cve_bench requires 3.12)
- Editable installs of `upstream/inspect_ai` and `upstream/inspect_evals`

**3. Score Normalization Framework**
- All benchmarks map to [0-100] scale where **higher = safer**
- Each benchmark must have an explicit mapper in `score_mapper.py` (no defaults)
- Risk levels: CRITICAL (0-30), HIGH (30-50), MEDIUM (50-60), LOW (60-80), MINIMAL (80-100)
- Score types: NUMERIC, BINARY, ORDINAL, CATEGORICAL
- Direction matters: some benchmarks are LOWER_IS_SAFER (e.g., attack success rate)

**4. Upstream Submodules**
- `upstream/inspect_ai`: Base evaluation framework providing `inspect` CLI
- `upstream/inspect_evals`: Benchmark implementations under `src/inspect_evals/`
- `upstream/safety_lookahead`: Safety lookahead functionality (optional, used by `run-eval-salt.py`)
- Task paths format: `inspect_evals/benchmark` or `upstream/inspect_evals/src/inspect_evals/path@task`

## Adding a New Benchmark

1. **Add entry to `benchmarks/catalog.yaml`:**
   ```yaml
   new_benchmark:
     source: "upstream"
     module: "inspect_evals/new_benchmark"
     python: "3.10"
     extras: []
     judge_model: "default"
     tasks:
       - task_name
   ```

2. **Create mapper in `score_mapper.py`:**
   ```python
   @register_mapper
   class NewBenchmarkMapper(ScoreMapper):
       @property
       def benchmark_name(self) -> str:
           return "new_benchmark"

       @property
       def score_type(self) -> ScoreType:
           return ScoreType.NUMERIC

       @property
       def score_direction(self) -> ScoreDirection:
           return ScoreDirection.HIGHER_IS_SAFER  # or LOWER_IS_SAFER
   ```

3. **Add preflight requirements** in `benchmarks/preflight.py` if special dependencies (Docker, Kubernetes, gated datasets)

4. **Test with dry run:** `./run-eval.py new_benchmark --model test --dry-run`

## Special Dependencies

| Benchmark | Special Requirement |
|-----------|---------------------|
| cve_bench | Docker daemon required, Python 3.12 |
| agentdojo | Kubernetes cluster required |
| cyberseceval_2 | Judge model configuration required |
| xstest | HF_TOKEN with gated dataset access |
| strong_reject | GitHub dataset download (auto via preflight) |
| Gated datasets | HF_TOKEN with access permissions |

## Registered Benchmarks

The following benchmarks are registered in `benchmarks/catalog.yaml`:

| Benchmark | Description | Tasks |
|-----------|-------------|-------|
| **strong_reject** | Model rejection capability testing | strong_reject |
| **xstest** | Restricted dataset testing | xstest |
| **cyberseceval_2** | Security evaluation suite | cyse2_interpreter_abuse, cyse2_prompt_injection, cyse2_vulnerability_exploit |
| **bbq** | Bias behavior questions | bbq |
| **cve_bench** | CVE exploitation testing | cve_bench |
| **agentdojo** | Agent security testing | agentdojo |
| **agentharm** | Agent harmfulness testing | agentharm, agentharm_benign |
| **truthfulqa** | Truthfulness evaluation | truthfulqa |

## Configuration Files

### Safety-Lookahead Experiment Configs
- `config-salt-exp1-strongreject.yaml` - Configuration for Safety-Lookahead evaluation with strong_reject benchmark
- `config-salt-exp-template.yaml` - Template configuration for Safety-Lookahead evaluations
- `benchmarks/config_schema.yaml` - Schema validation for benchmark configurations

### Using YAML Configurations
```bash
# Run with configuration file
./run-eval-salt.py --config config-salt-exp1-strongreject.yaml
```

## Internal Directory Structure

```
eval-poc/
├── internal/
│   ├── dev-docs/      # Development documentation
│   ├── project/       # Project-specific files
│   ├── resources/     # Resource files
│   └── specs/         # Specifications and standards
├── vendor/            # Third-party vendor dependencies
├── benchmarks/        # Benchmark definitions and preflight checks
├── upstream/          # Submodules (inspect_ai, inspect_evals, safety_lookahead)
└── results/           # Evaluation results storage
```

## Score Mappers

The `score_mapper.py` contains registered mappers for normalizing benchmark results:

| Mapper | Benchmark | Score Type | Direction |
|--------|-----------|------------|-----------|
| InterpreterAbuseMapper | cyberseceval_2 (interpreter abuse) | NUMERIC | LOWER_IS_SAFER |
| PromptInjectionMapper | cyberseceval_2 (prompt injection) | NUMERIC | LOWER_IS_SAFER |
| VulnerabilityExploitMapper | cyberseceval_2 (vulnerability exploit) | NUMERIC | Dual-purpose |
| PrivacyLensProbingMapper | privacylens (probing) | NUMERIC | HIGHER_IS_SAFER |

Each mapper implements the `ScoreMapper` interface with explicit scoring rationale.

## Result Files

Results are stored as inspect_ai `.eval` files (zip archives containing `header.json` with metrics). Use `report_generator.py` to extract and normalize scores.
