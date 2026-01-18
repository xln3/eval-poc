# Benchmarks

## 目录结构

- `catalog.yaml` - 基准测试路由注册表
- `local/` - 本地基准测试
  - `private_bench/` - 私有基准测试（不公开）
  - `pending_bench/` - 待审核基准测试
  - `restricted_bench/` - 受限基准测试

## 路由规则

基准测试通过 `catalog.yaml` 注册和路由。每个基准测试条目包含：
- `name`: 唯一标识符
- `source`: 基准测试源路径
- `enabled`: 是否启用
- `tags`: 分类标签

## 放置规则

1. **private_bench**: 内部开发的私有基准测试
2. **pending_bench**: 正在开发或等待审核的基准测试
3. **restricted_bench**: 需要特殊授权才能访问的基准测试
