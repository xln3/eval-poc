# Changelog

## [Unreleased] - 2026-02-06

### 智能体评测支持 + Mock Bank Agent

新增自定义智能体评测能力，支持评测暴露 OpenAI 兼容 API 的 Agent（带 system prompt、RAG、工具调用等）。

#### Added

- **`examples/mock-bank-agent/`** — 模拟银行客服智能体（演示 + 测试目标）
  - Proxy 模式：注入 system prompt + 关键词匹配 RAG → 转发给后端 LLM
  - 知识库包含公开信息和内部机密（审批阈值、佣金等），用于测试信息泄露防护
  - `server.py` — FastAPI 服务，OpenAI 兼容 `/v1/chat/completions` + `/v1/models`
  - `knowledge_base.py` — 银行产品知识库（存款/贷款/信用卡/理财）
- **前端：模型与智能体分离**
  - 模型管理页拆为三区域：预置模型、自定义模型、智能体
  - 新增「添加智能体」按钮和专属表单（智能体名称、所属系统、智能体端点）
  - 智能体卡片使用绿色 emerald 主题区分
  - ModelSelector（新建评测 step 1）同步三栏展示
- **Pipeline: `--api-base` / `--api-key` 透传**
  - `run-eval.py` 新增 `--api-base`、`--api-key` 参数
  - 通过 inspect CLI 原生 `--model-base-url` 传递（不被 `.env` 覆盖）
  - `eval_runner.py` 从 model_config 读取 credentials 作为 CLI 参数传递

#### Changed

- `src/eval-core/app/models/schemas.py` — `ModelConfig` / `ModelCreateRequest` 新增 `is_agent` 字段；`EvalJob` 新增 `model_config_id` 字段
- `src/eval-core/app/services/model_store.py` — 透传 `is_agent`
- `src/eval-core/app/services/eval_runner.py` — 保存 `model_config_id`，构建 `--api-base`/`--api-key` CLI 参数
- `src/frontend/src/components/layout/Sidebar.jsx` — 导航标签改为「模型与智能体」
- `src/frontend/src/pages/NewEvalPage.jsx` — step 1 改为「选择评测对象」，支持添加智能体

---

### 新增 PersonalizedSafety Benchmark

迁移 PersonalizedSafety 评测任务到本地插件架构，评估 LLM 在高风险个性化场景（心理健康、自伤风险等）下的安全响应能力。

#### Added

- **`benchmarks/eval_benchmarks/personalized_safety/`** — 本地 benchmark 插件
  - 3 个 @task：`personalized_safety`（通用）、`personalized_safety_context_free`（无背景）、`personalized_safety_context_rich`（含背景）
  - 3 维度评分（1-5）：Risk Sensitivity、Emotional Empathy、Personalization，总分 3-15
  - GPT-4o 作为 judge model，支持自定义 judge
  - 数据集：HuggingFace `wick1d/Personalized_Safety_Data`
- **`score_mapper.py`** — 新增 `PersonalizedSafetyMapper`（normalized_avg_score 1-5 → safety_score 0-100，HIGHER_IS_SAFER）
- **`catalog.yaml`** — 注册 personalized_safety 及其 3 个 task

#### Changed

- `benchmarks/eval_benchmarks/_registry.py` — 注册 3 个 @task 函数
- `benchmarks/eval_benchmarks/__init__.py` — 导入 personalized_safety 模块
- `CLAUDE.md` — 更新 Registered Benchmarks 表、Score Mappers 表、目录结构树

---

### Web 评测平台（前端 + 后端 API）

新增完整的 Web 界面，让非技术用户也能触发评测、查看结果。后端 FastAPI 包装现有 CLI 工具，前端 React 暗色主题。

#### Added

- **FastAPI 后端** `src/eval-core/`
  - `app/main.py` — 入口，挂载 CORS 及全部路由
  - `app/config.py` — 路径常量（PROJECT_ROOT、CATALOG_PATH 等）
  - `app/models/schemas.py` — Pydantic 数据模型（Benchmark / Model / EvalJob / Result / Report）
  - `app/routers/` — 5 个路由模块：benchmarks、models、evaluations、results、reports
  - `app/services/catalog_service.py` — 解析 `catalog.yaml` + 中文元数据
  - `app/services/model_store.py` — 预置模型列表 + 自定义模型 JSON 持久化
  - `app/services/eval_runner.py` — 异步子进程调用 `run-eval.py`，内存 Job 队列，全局锁防并发
  - `app/services/result_reader.py` — 扫描 `results/` 目录，解析 `.eval` zip 文件
  - `app/services/score_service.py` — 封装 `score_mapper.py` 供 API 使用
  - `app/services/report_service.py` — 封装 `report_generator.py` 供 API 使用
- **React 前端** `src/frontend/`
  - 技术栈：React 18 + Vite 6 + Tailwind CSS v4 + react-router-dom v6 + recharts
  - 6 个页面：控制面板 `/`、新建评测 `/evaluations/new`（三步向导）、评测进度 `/evaluations/:id`（轮询刷新）、结果列表 `/results`、结果详情 `/results/:model`（仪表盘+雷达图）、模型管理 `/models`
  - 通用组件：Button、Card、Badge、Modal、Input、Select、Loading、EmptyState
  - 数据可视化：SafetyScoreGauge（SVG 环形仪表盘）、RadarChart（recharts 雷达图）、RiskLevelBadge、ScoreBar
  - 业务组件：ModelSelector、ModelConfigForm、BenchmarkCard、BenchmarkSelector、EvalProgress
  - API 层：`api/client.js`（fetch 封装）+ 5 个端点模块
  - Hooks：usePolling（定时轮询）、useModels（模型 CRUD）、useToast（通知）
  - 暗色主题：slate-900 背景，全中文文案
  - Vite 代理：`/api` → `localhost:8000`，前端全部使用相对路径

#### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/benchmarks` | 列出已注册评测任务（解析 catalog.yaml） |
| GET | `/api/benchmarks/task-meta` | 任务中文元数据 |
| GET | `/api/models` | 列出预置 + 自定义模型 |
| POST | `/api/models` | 添加自定义模型 |
| DELETE | `/api/models/{id}` | 删除自定义模型 |
| POST | `/api/evaluations` | 启动评测（异步子进程） |
| GET | `/api/evaluations` | 列出所有评测任务 |
| GET | `/api/evaluations/{id}` | 查看评测进度 |
| GET | `/api/results` | 列出所有模型结果摘要 |
| GET | `/api/results/{model}` | 模型评测详情（含安全分数） |
| POST | `/api/reports/generate` | 生成 Markdown 安全报告 |

#### Changed

- `.gitignore` — 新增 `node_modules/`、`*.local`、`src/eval-core/data/models.json`、`reports/`、`TASK.md`
- `CLAUDE.md` — 新增 Web Platform 章节（启动命令、后端结构、API 表、前端结构、开发约定）；更新目录结构树
- `README.md` — 新增 Web 评测平台章节（启动、功能、技术栈、API）；更新项目结构树

#### 文件新增汇总

| 目录 | 文件数 | 说明 |
|------|--------|------|
| `src/eval-core/app/` | 13 | FastAPI 后端（main + config + schemas + 5 routers + 6 services） |
| `src/eval-core/` | 2 | `requirements.txt`、`data/models.json` |
| `src/frontend/` | 4 | `package.json`、`vite.config.js`、`index.html`、`package-lock.json` |
| `src/frontend/src/api/` | 6 | API 客户端模块 |
| `src/frontend/src/hooks/` | 3 | React Hooks |
| `src/frontend/src/constants/` | 2 | 风险等级、评测元数据 |
| `src/frontend/src/components/` | 15 | 布局 + 通用 + 业务 + 可视化组件 |
| `src/frontend/src/pages/` | 6 | 页面组件 |
| `src/frontend/src/` | 3 | `main.jsx`、`App.jsx`、`index.css` |

---

### Benchmark 插件架构优化

将本地 benchmark 改造为标准 inspect_ai 插件包，对齐官方 `inspect_evals` 的集成模式。

#### Changed

- **重命名** `benchmarks/local/` → `benchmarks/eval_benchmarks/`，包名更专业，避免与 Python 内置冲突
- **添加 entry point** 在 `benchmarks/pyproject.toml` 中声明 `[project.entry-points.inspect_ai]`，inspect_ai 可通过 registry 自动发现本地任务
- **新增 `_registry.py`** 集中 import 所有 `@task` 函数（raccoon, overthink, privacylens_probing, privacylens_action），import 即注册
- **简化 task 路径** 从文件路径格式（`benchmarks/local/raccoon/raccoon.py@raccoon`）改为 entry point 格式（`eval_benchmarks/raccoon`），与 upstream 一致
- **所有 venv 统一安装 `inspect_evals`** 之前仅 upstream benchmark 安装，local benchmark 无法使用 `inspect_evals.utils` 等工具；现在所有 venv 都安装
- **提升 privacylens** 从 `pending_bench/` 嵌套目录移至 `eval_benchmarks/privacylens/`，与 raccoon/overthink 保持一致的扁平结构
- **privacylens 改用相对导入** `from privacylens.xxx` → `from .xxx`，适配新的包结构

#### Removed

- **删除 PYTHONPATH hack** (`run-eval.py` 中手动设置 `PYTHONPATH=benchmarks/` 的代码)，entry point 注册后不再需要
- **删除空目录** `pending_bench/`、`private_bench/`、`restricted_bench/` 及其 `.gitkeep`

#### Added

- **submodule 初始化检查** 在 `setup_benchmark_env()` 中检测 `upstream/inspect_evals` 是否已初始化，未初始化时给出明确提示
- **完整集成指南** 重写 `benchmarks/README.md`，包含插件架构图、五步集成流程
- **CLAUDE.md 补充** 区分 upstream 和 local 两种添加 benchmark 的方式

#### 文件改动汇总

| 文件 | 改动 |
|------|------|
| `benchmarks/local/` → `benchmarks/eval_benchmarks/` | 目录重命名 |
| `benchmarks/eval_benchmarks/_registry.py` | 新建：集中注册 @task |
| `benchmarks/pyproject.toml` | 添加 entry point，更新 packages.find |
| `benchmarks/catalog.yaml` | task path 简化为 entry point 格式 |
| `run-eval.py` | 所有 venv 装 inspect_evals；删除 PYTHONPATH hack；加 submodule 检查 |
| `benchmarks/eval_benchmarks/privacylens/*.py` | 绝对导入 → 相对导入 |
| `benchmarks/preflight.py` | 更新 privacylens 数据路径 |
| `benchmarks/README.md` | 重写：完整集成指南 |
| `CLAUDE.md` | 补充 local benchmark 添加流程 |
