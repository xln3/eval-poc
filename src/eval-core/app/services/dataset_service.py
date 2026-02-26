"""数据集描述服务 - 生成测试数据集说明和混合样本"""

import sys
from pathlib import Path
from typing import Dict, List, Any

from ..config import PROJECT_ROOT

# 将项目根目录加入 sys.path 以便导入 dataset_descriptor
_root = str(PROJECT_ROOT)
if _root not in sys.path:
    sys.path.insert(0, _root)


async def generate_dataset_description(benchmark_names: List[str]) -> Dict[str, Any]:
    """
    生成数据集描述报告和混合样本数据。

    Parameters:
        benchmark_names: 要包含的 benchmark 名称列表

    Returns:
        包含 markdown, json_data, benchmark_count, total_samples 的字典
    """
    import dataset_descriptor

    markdown = dataset_descriptor.generate_dataset_report(benchmark_names)
    json_data = dataset_descriptor.generate_mixed_dataset(benchmark_names)

    return {
        "markdown": markdown,
        "json_data": json_data,
        "benchmark_count": len(benchmark_names),
        "total_samples": len(json_data),
    }
