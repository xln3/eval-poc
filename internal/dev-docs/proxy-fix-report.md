# Benchmark 代理修复报告

## 问题背景

本服务器位于阿里云北京 ECS，外部网络（HuggingFace、PyPI、Docker Hub、OpenAI blob 存储等）需通过本地代理 `http://127.0.0.1:7890`（mihomo）才能访问。

之前有 **15 个 benchmark 执行失败**，其中 **7 个的根本原因是代理环境变量未正确传递给子进程**。

## 根因分析

### 1. `run-eval.py` 子进程缺少代理环境变量

`run-eval.py` 通过 `subprocess.run()` 启动 `inspect eval` 子进程。子进程的环境变量通过 `env = os.environ.copy()` 从父进程继承。

**问题**：当用户 shell 中未设置 `http_proxy`/`https_proxy`/`HTTP_PROXY`/`HTTPS_PROXY` 时，子进程也无法通过代理访问外网。而 benchmark 执行过程中需要：
- 从 HuggingFace 下载数据集（`datasets` 库、`load_json_dataset`）
- 从 OpenAI blob 存储下载 TSV 文件（mgsm）
- 从 PyPI 下载模型权重（detoxify/BERT）

**受影响 benchmark**：
| Benchmark | 失败原因 | 需要访问的外部资源 |
|-----------|---------|-------------------|
| cyse2_prompt_injection | HF 下载超时 | `facebook/cyberseceval2` (HuggingFace) |
| mgsm | OpenAI blob URL 不可达 | `openaipublic.blob.core.windows.net` |
| sevenllm | HF 数据集 404 | `Multilingual-Multimodal-NLP/SEVENLLM-Dataset` (HuggingFace) |
| culturalbench | 本地数据集路径错误 | `kellycyy/CulturalBench` (HuggingFace) |
| bold | 需要 torch + BERT | HuggingFace model hub |
| mask | Gated HF 数据集 | `cais/MASK` (HuggingFace, 需 HF_TOKEN) |
| b3 | Gated HF 数据集 | `Lakera/b3-agent-security-benchmark-weak` (HuggingFace, 需 HF_TOKEN) |

### 2. `OPENAI_BASE_URL` 未设置

Judge/grader 模型（如 `alicloud-qwen3.5-plus`）需要通过 aihubmix API 网关访问。部分 upstream benchmark 的 scorer 代码硬编码了 `gpt-4.1` 作为默认 grader 模型：

```python
# sosbench, sciknoweval 等
grader_model = get_model(role="grader", default="openai/gpt-4.1-2025-04-14")
```

虽然 `--model-role grader=openai/alicloud-qwen3.5-plus` 会覆盖此默认值，但 grader 模型仍需 `OPENAI_BASE_URL` 指向 aihubmix。`.env` 中此前未设置该变量，导致 grader 尝试直接连接 OpenAI API（不可达）。

**受影响 benchmark**：sosbench, sciknoweval, make_me_pay

### 3. Python 包缺失

部分 benchmark 的虚拟环境中缺少运行时依赖：

| Benchmark | 缺少的包 |
|-----------|---------|
| fortress | `anthropic` |
| abstention_bench | `hydra-core` |
| sciknoweval | `rdkit-pypi`, `gdown`, `nltk`, `rouge-score`, `gensim` |

## 修复措施

### 修复 1：`run-eval.py` 自动注入代理环境变量

在 `run_eval()` 函数中，创建子进程环境变量后自动检查并注入代理配置：

```python
# 确保代理环境变量已设置 (HuggingFace / PyPI 等需要走代理)
_PROXY_URL = "http://127.0.0.1:7890"
for proxy_var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
    if proxy_var not in env:
        env[proxy_var] = _PROXY_URL
```

**效果**：无论用户 shell 是否设置代理，benchmark 子进程都能通过代理访问外部资源。

### 修复 2：`.env` 中添加 `OPENAI_BASE_URL`

```
OPENAI_BASE_URL=https://aihubmix.com/v1
```

**效果**：所有 `openai/` 前缀的模型（包括 grader/judge）默认通过 aihubmix API 网关访问。

### 修复 3：安装缺失的 Python 包

```bash
uv pip install --python .venvs/fortress/bin/python anthropic
uv pip install --python .venvs/abstention_bench/bin/python hydra-core
uv pip install --python .venvs/sciknoweval/bin/python rdkit-pypi gdown nltk rouge-score gensim
```

### 修复 4：配置 HF_TOKEN

`.env` 中添加 HuggingFace token 以访问 gated 数据集（mask, b3）。

## 修复结果

**修复前**：27 个 task 通过 / 15 个失败
**修复后**：39 个 task 通过 / 仅 2 个仍有 Docker 镜像拉取问题

| Benchmark | 状态 | 原始指标 |
|-----------|------|---------|
| sosbench | FIXED | mean=0.200 |
| fortress | FIXED | ARS_overall=40.179 |
| abstention_bench | FIXED | f1=0.698 |
| bold | FIXED | toxicity=0.000 |
| culturalbench | FIXED | accuracy=0.860 |
| make_me_pay | FIXED | mean=0.000 |
| mgsm | FIXED | accuracy=0.920 |
| sevenllm | FIXED | accuracy=0.980 |
| cyse2_prompt_injection | FIXED | accuracy=0.200 |
| sciknoweval | FIXED | per-task metrics |
| mask | FIXED | honesty=0.560 |
| b3 | FIXED | mean=0.559 |
| gdm_self_reasoning | FIXED | accuracy=1.000 |

### 仍需解决

| Benchmark | 原因 |
|-----------|------|
| cve_bench | Docker Hub (`registry-1.docker.io`) 通过代理仍不可达（TLS 握手超时） |
| gdpval | Docker 容器构建中断（需重试） |

## 为什么需要 `export http_proxy`

在修复 `run-eval.py` 自动注入代理之前，需要在运行命令时显式设置代理环境变量：

```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
./run-eval.py <benchmark> --model <model>
```

**现在已不再需要**。`run-eval.py` 会自动检测并注入代理配置，用户只需：

```bash
source .env && ./run-eval.py <benchmark> --model <model>
```

代理变量在以下场景被使用：
1. **HuggingFace 数据集下载**：`datasets` 库通过 `HTTPS_PROXY` 路由请求
2. **OpenAI blob 存储**：mgsm 的 TSV 数据文件托管在 Azure blob（需代理）
3. **PyPI / pip 安装**：部分 benchmark 在运行时按需安装依赖
4. **HuggingFace model hub**：bold 的 detoxify scorer 需要下载 BERT 模型权重
