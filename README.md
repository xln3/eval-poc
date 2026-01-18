# agent-sec

Agent 安全评估框架。

## 项目结构

```
src/               - 源代码
  frontend/        - 前端应用
  eval-core/       - 评估核心
  report-engine/   - 报告引擎
benchmarks/        - 基准测试
  local/           - 本地基准测试
upstream/          - 上游依赖（子模块）
vendor/            - 第三方依赖
internal/          - 内部文档和资源
  specs/           - 规范文档
  dev-docs/        - 开发文档
  project/         - 项目管理
  resources/       - 资源文件
LICENSES/          - 许可证文件
```

## 子模块

- `upstream/inspect_ai` - Inspect AI 框架
- `upstream/inspect_evals` - Inspect 评估集

## 快速开始

```bash
# 克隆并初始化子模块
git clone --recursive <repo-url>

# 或在已克隆的仓库中初始化子模块
git submodule update --init --recursive
```
