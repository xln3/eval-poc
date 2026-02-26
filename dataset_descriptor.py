"""
Dataset Descriptor - 生成测试数据集说明报告和混合样本数据集

从 benchmarks/docs/ 读取各 benchmark 的样本数据和描述,
生成匿名化的数据集说明报告(隐藏 benchmark 名称,仅展示风险点)和混合样本 JSON。
"""

import json
import os
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 项目根目录 (dataset_descriptor.py 与 run-eval.py 同级)
PROJECT_ROOT = Path(__file__).resolve().parent
DOCS_DIR = PROJECT_ROOT / "benchmarks" / "docs"


def load_benchmark_docs(benchmark_names: List[str]) -> List[dict]:
    """
    加载指定 benchmark 的文档数据。

    从 benchmarks/docs/<name>/<name>_3.json 读取每个 benchmark 的样本数据。

    Parameters:
        benchmark_names: benchmark 名称列表

    Returns:
        成功加载的 benchmark 文档数据列表
    """
    docs = []
    for name in benchmark_names:
        json_path = DOCS_DIR / name / "{}_3.json".format(name)
        if not json_path.exists():
            continue
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            docs.append(data)
        except (json.JSONDecodeError, IOError) as e:
            # 跳过无法加载的文件
            continue
    return docs


def _load_description_md(benchmark_name: str, lang: str = "zh") -> Optional[str]:
    """
    加载 benchmark 的 Markdown 描述文件。

    Parameters:
        benchmark_name: benchmark 名称
        lang: 语言 ("zh" 或 "en")

    Returns:
        Markdown 内容字符串, 若文件不存在返回 None
    """
    md_path = DOCS_DIR / benchmark_name / "{}_{}.md".format(benchmark_name, lang)
    if not md_path.exists():
        return None
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except IOError:
        return None


def _group_by_risk_category(docs: List[dict], lang: str = "zh") -> OrderedDict:
    """
    将加载的 benchmark 文档按风险维度分组。

    Parameters:
        docs: load_benchmark_docs 返回的文档列表
        lang: 语言

    Returns:
        OrderedDict, key 为风险维度名称, value 为该维度下所有 benchmark 数据列表
    """
    groups = OrderedDict()  # type: OrderedDict[str, List[dict]]
    for doc in docs:
        if lang == "zh":
            category = doc.get("risk_category", "未分类")
        else:
            category = doc.get("risk_category_en", doc.get("risk_category", "Uncategorized"))
        if category not in groups:
            groups[category] = []
        groups[category].append(doc)
    return groups


def _extract_section(md_content: str, header: str) -> Optional[str]:
    """
    从 Markdown 中提取指定 section 的内容(不含标题)。

    返回该 section 到下一个同级标题之间的纯文本, 若未找到返回 None。
    """
    lines = md_content.split("\n")
    capturing = False
    result = []  # type: List[str]
    header_prefix = header.split(" ", 1)[0]  # e.g. "##"
    for line in lines:
        if line.strip() == header:
            capturing = True
            continue
        if capturing:
            # 遇到同级或更高级标题则停止
            if line.startswith(header_prefix + " ") and line.strip() != header:
                break
            result.append(line)
    if result:
        return "\n".join(result).strip()
    return None


def _strip_category_number(category: str) -> str:
    """
    去除风险维度编号前缀, 例如 '1.1 恶意使用' -> '恶意使用'。
    """
    parts = category.strip().split(" ", 1)
    if len(parts) == 2:
        # 检查第一部分是否像编号 (如 "1.1", "3.2" 等)
        prefix = parts[0]
        if any(c.isdigit() for c in prefix):
            return parts[1]
    return category


def generate_dataset_report(benchmark_names: List[str], lang: str = "zh") -> str:
    """
    生成匿名化的数据集说明报告 (Markdown 格式)。

    报告隐藏 benchmark 名称, 仅展示风险维度和风险点。

    Parameters:
        benchmark_names: benchmark 名称列表
        lang: 语言 ("zh" 或 "en")

    Returns:
        Markdown 格式的数据集说明报告
    """
    docs = load_benchmark_docs(benchmark_names)
    if not docs:
        if lang == "zh":
            return "# 安全评测数据集说明\n\n未找到任何已注册的 benchmark 文档数据。\n\n请确认 `benchmarks/docs/` 目录下存在对应的数据文件。"
        else:
            return "# Safety Evaluation Dataset Description\n\nNo registered benchmark documentation data found.\n\nPlease ensure data files exist under `benchmarks/docs/`."

    groups = _group_by_risk_category(docs, lang)

    # 统计
    total_risk_dims = len(groups)
    total_samples = sum(doc.get("sample_count", len(doc.get("samples", []))) for doc in docs)
    total_risk_points = len(docs)

    # 构建报告
    lines = []  # type: List[str]

    if lang == "zh":
        lines.append("# 安全评测数据集说明")
        lines.append("")
        lines.append("## 概述")
        lines.append(
            "本数据集涵盖 {} 个风险维度、{} 个风险点、共 {} 个测试样本，"
            "用于评估大语言模型在以下安全场景中的表现：".format(
                total_risk_dims, total_risk_points, total_samples
            )
        )
        lines.append("")

        # 概要表
        lines.append("| 风险维度 | 风险点 | 样本数 |")
        lines.append("|---------|--------|--------|")
        for category, cat_docs in groups.items():
            cat_name = _strip_category_number(category)
            for doc in cat_docs:
                risk_point = doc.get("risk_point_zh", doc.get("risk_point_en", ""))
                sample_count = doc.get("sample_count", len(doc.get("samples", [])))
                lines.append("| {} | {} | {} |".format(cat_name, risk_point, sample_count))
        lines.append("")

        # 各维度详情
        lines.append("## 风险维度详情")
        lines.append("")

        dim_idx = 0
        for category, cat_docs in groups.items():
            dim_idx += 1
            cat_name = _strip_category_number(category)
            lines.append("### {}. {}".format(dim_idx, cat_name))
            lines.append("")

            for doc in cat_docs:
                risk_point = doc.get("risk_point_zh", doc.get("risk_point_en", ""))
                lines.append("**风险点**: {}".format(risk_point))
                lines.append("")

                # 尝试加载描述文件中的"测试方法"部分
                benchmark_name = doc.get("benchmark", "")
                desc_md = _load_description_md(benchmark_name, lang) if benchmark_name else None
                if desc_md:
                    method_text = _extract_section(desc_md,
                                                   "## 测试方法" if lang == "zh" else "## Test Method")
                    if method_text:
                        lines.append("**测试方法**: {}".format(method_text))
                        lines.append("")

                # 样本展示
                samples = doc.get("samples", [])
                if samples:
                    lines.append("#### 示例测试用例")
                    lines.append("")
                    for idx, sample in enumerate(samples, 1):
                        lines.append("**示例 {}**".format(idx))
                        input_text = sample.get("input", "")
                        expected = sample.get("expected_behavior", "")
                        risk_desc = sample.get("risk_description_zh",
                                               sample.get("risk_description_en", ""))
                        lines.append("- 输入: \"{}\"".format(input_text))
                        lines.append("- 期望行为: \"{}\"".format(expected))
                        if risk_desc:
                            lines.append("- 风险说明: \"{}\"".format(risk_desc))
                        lines.append("")

            lines.append("---")
            lines.append("")

    else:
        # English report
        lines.append("# Safety Evaluation Dataset Description")
        lines.append("")
        lines.append("## Overview")
        lines.append(
            "This dataset covers {} risk dimensions, {} risk points, "
            "and a total of {} test samples for evaluating LLM safety:".format(
                total_risk_dims, total_risk_points, total_samples
            )
        )
        lines.append("")

        # Summary table
        lines.append("| Risk Dimension | Risk Point | Sample Count |")
        lines.append("|----------------|------------|--------------|")
        for category, cat_docs in groups.items():
            cat_name = _strip_category_number(category)
            for doc in cat_docs:
                risk_point = doc.get("risk_point_en", doc.get("risk_point_zh", ""))
                sample_count = doc.get("sample_count", len(doc.get("samples", [])))
                lines.append("| {} | {} | {} |".format(cat_name, risk_point, sample_count))
        lines.append("")

        # Dimension details
        lines.append("## Risk Dimension Details")
        lines.append("")

        dim_idx = 0
        for category, cat_docs in groups.items():
            dim_idx += 1
            cat_name = _strip_category_number(category)
            lines.append("### {}. {}".format(dim_idx, cat_name))
            lines.append("")

            for doc in cat_docs:
                risk_point = doc.get("risk_point_en", doc.get("risk_point_zh", ""))
                lines.append("**Risk Point**: {}".format(risk_point))
                lines.append("")

                benchmark_name = doc.get("benchmark", "")
                desc_md = _load_description_md(benchmark_name, "en") if benchmark_name else None
                if desc_md:
                    method_text = _extract_section(desc_md, "## Test Method")
                    if method_text:
                        lines.append("**Test Method**: {}".format(method_text))
                        lines.append("")

                samples = doc.get("samples", [])
                if samples:
                    lines.append("#### Example Test Cases")
                    lines.append("")
                    for idx, sample in enumerate(samples, 1):
                        lines.append("**Example {}**".format(idx))
                        input_text = sample.get("input", "")
                        expected = sample.get("expected_behavior", "")
                        risk_desc = sample.get("risk_description_en",
                                               sample.get("risk_description_zh", ""))
                        lines.append("- Input: \"{}\"".format(input_text))
                        lines.append("- Expected Behavior: \"{}\"".format(expected))
                        if risk_desc:
                            lines.append("- Risk Description: \"{}\"".format(risk_desc))
                        lines.append("")

            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def generate_mixed_dataset(benchmark_names: List[str]) -> List[dict]:
    """
    生成混合样本 JSON 数据集。

    合并所有 benchmark 的样本, 添加 risk_category 字段并移除 benchmark 字段,
    实现匿名化。

    Parameters:
        benchmark_names: benchmark 名称列表

    Returns:
        混合样本列表, 每条包含 id, risk_category, risk_point, input,
        expected_behavior, risk_description
    """
    docs = load_benchmark_docs(benchmark_names)
    if not docs:
        return []

    mixed = []  # type: List[dict]

    # 按风险维度编号分组, 用于生成 ID
    category_counters = {}  # type: Dict[str, int]

    for doc in docs:
        risk_category_raw = doc.get("risk_category", "未分类")
        risk_category = _strip_category_number(risk_category_raw)

        # 提取编号部分用于 ID 生成 (如 "1.1" -> "1_1")
        category_id = risk_category_raw.strip().split(" ", 1)[0]
        if any(c.isdigit() for c in category_id):
            category_id = category_id.replace(".", "_")
        else:
            category_id = "0"

        risk_point = doc.get("risk_point_zh", doc.get("risk_point_en", ""))
        samples = doc.get("samples", [])

        for sample in samples:
            if category_id not in category_counters:
                category_counters[category_id] = 0
            category_counters[category_id] += 1
            seq = category_counters[category_id]

            mixed_sample = {
                "id": "risk_{}_{}".format(category_id, seq),
                "risk_category": risk_category,
                "risk_point": risk_point,
                "input": sample.get("input", ""),
                "expected_behavior": sample.get("expected_behavior", ""),
                "risk_description": sample.get("risk_description_zh",
                                               sample.get("risk_description_en", "")),
            }
            mixed.append(mixed_sample)

    return mixed


def generate_all(benchmark_names: List[str], lang: str = "zh") -> Tuple[str, List[dict]]:
    """
    生成数据集说明报告和混合样本数据集。

    Parameters:
        benchmark_names: benchmark 名称列表
        lang: 语言 ("zh" 或 "en")

    Returns:
        (markdown_report, mixed_dataset) 元组
    """
    markdown = generate_dataset_report(benchmark_names, lang=lang)
    json_data = generate_mixed_dataset(benchmark_names)
    return markdown, json_data


# ============================================================
# CLI 入口: 可直接命令行运行
# ============================================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="生成安全评测数据集说明报告和混合样本数据集"
    )
    parser.add_argument(
        "benchmarks",
        nargs="+",
        help="要包含的 benchmark 名称列表",
    )
    parser.add_argument(
        "--lang",
        choices=["zh", "en"],
        default="zh",
        help="报告语言 (默认: zh)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "reports"),
        help="输出目录 (默认: reports/)",
    )
    parser.add_argument(
        "--list-available",
        action="store_true",
        help="列出所有可用的 benchmark 文档",
    )

    args = parser.parse_args()

    # 列出可用文档
    if args.list_available:
        if not DOCS_DIR.exists():
            print("文档目录不存在: {}".format(DOCS_DIR))
            return
        available = []
        for d in sorted(DOCS_DIR.iterdir()):
            if d.is_dir():
                json_file = d / "{}_3.json".format(d.name)
                if json_file.exists():
                    available.append(d.name)
        if available:
            print("可用 benchmark 文档:")
            for name in available:
                print("  - {}".format(name))
        else:
            print("未找到任何 benchmark 文档")
        return

    # 生成报告和数据集
    markdown, json_data = generate_all(args.benchmarks, lang=args.lang)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 写入 Markdown 报告
    md_path = output_dir / "dataset_description_{}.md".format(args.lang)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    print("报告已写入: {}".format(md_path))

    # 写入混合 JSON 数据集
    json_path = output_dir / "mixed_dataset.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print("混合数据集已写入: {} ({} 条样本)".format(json_path, len(json_data)))


if __name__ == "__main__":
    main()
