# Benchmarks

## 目录结构

```
benchmarks/
├── catalog.yaml          # 基准测试路由注册表
├── indexes/              # 样本索引文件
│   ├── cyberseceval_2/
│   │   ├── cyse2_interpreter_abuse.yaml
│   │   ├── cyse2_prompt_injection.yaml
│   │   └── cyse2_vulnerability_exploit.yaml
│   └── privacylens/
│       ├── privacylens_action.yaml
│       └── privacylens_probing.yaml
├── tools/                # 辅助工具
│   ├── list_samples.py   # 枚举数据集样本 ID
│   └── update_index.py   # LLM 筛选更新索引
├── local/                # 本地基准测试
│   ├── private_bench/    # 私有基准测试（不公开）
│   ├── pending_bench/    # 待审核基准测试
│   └── restricted_bench/ # 受限基准测试
└── preflight.py          # 预检查模块
```

## 路由规则

基准测试通过 `catalog.yaml` 注册和路由。每个基准测试条目包含：
- `name`: 唯一标识符
- `source`: 基准测试源路径
- `enabled`: 是否启用
- `tags`: 分类标签

## 样本索引

索引文件用于在评测前过滤样本，只运行有代表性的 case。详见主 README.md 的"样本索引"章节。

### 索引文件格式

```yaml
mode: include  # include=只跑列出的, exclude=跳过列出的
updated: '2026-01-29T16:30:00'
samples:
  '10':
    sources:
      - model: deepseek-v3
        reason: 展示了成功的沙箱逃逸攻击
    added: '2026-01-29'
```

### 工具

- **list_samples.py**: 枚举数据集中的所有样本 ID
- **update_index.py**: 使用 LLM 从 .eval 文件筛选有价值样本，更新索引

## 放置规则

1. **private_bench**: 内部开发的私有基准测试
2. **pending_bench**: 正在开发或等待审核的基准测试
3. **restricted_bench**: 需要特殊授权才能访问的基准测试
