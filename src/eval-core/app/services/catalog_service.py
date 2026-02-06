"""解析 benchmarks/catalog.yaml"""

import yaml
from typing import List, Dict, Any, Optional
from ..config import CATALOG_PATH
from ..models.schemas import BenchmarkInfo, TaskInfo

# 评测任务中文元数据
BENCHMARK_META: Dict[str, Dict[str, str]] = {
    "cyberseceval_2": {
        "display_name": "网络安全评测 v2",
        "description": "Meta CyberSecEval 2 安全评估套件，评估模型在代码安全场景中的表现",
    },
    "strong_reject": {
        "display_name": "强拒绝测试",
        "description": "评估模型拒绝有害请求的能力",
    },
    "xstest": {
        "display_name": "安全边界测试",
        "description": "评估模型在安全边界场景下的表现",
    },
    "bbq": {
        "display_name": "偏见行为测试",
        "description": "评估模型在偏见相关问题上的公平性",
    },
    "cve_bench": {
        "display_name": "CVE漏洞利用测试",
        "description": "评估模型利用真实CVE漏洞的能力",
    },
    "agentdojo": {
        "display_name": "智能体安全测试",
        "description": "评估智能体在工具调用场景下的安全性",
    },
    "agentharm": {
        "display_name": "智能体危害测试",
        "description": "评估智能体执行有害任务的倾向",
    },
    "truthfulqa": {
        "display_name": "真实性评估",
        "description": "评估模型回答的真实性和准确性",
    },
    "browse_comp": {
        "display_name": "浏览理解测试",
        "description": "评估浏览代理回答网络问题的准确性",
    },
    "raccoon": {
        "display_name": "提示词提取防护",
        "description": "评估模型抵抗提示词提取攻击的能力",
    },
    "overthink": {
        "display_name": "推理开销攻击",
        "description": "评估模型抵抗推理token开销攻击的能力",
    },
    "privacylens": {
        "display_name": "隐私保护评估",
        "description": "评估模型对隐私规范的理解和遵守",
    },
    "personalized_safety": {
        "display_name": "个性化安全评估",
        "description": "评估模型在高风险个性化场景（心理健康、自伤风险等）下的安全响应能力",
    },
}

TASK_META: Dict[str, Dict[str, str]] = {
    "cyse2_interpreter_abuse": {
        "display_name": "解释器滥用防护",
        "description": "评估模型抵抗生成恶意代码（沙箱逃逸、文件窃取等）的能力",
    },
    "cyse2_prompt_injection": {
        "display_name": "提示注入防护",
        "description": "评估模型抵抗提示注入攻击（指令覆盖、信息泄露）的能力",
    },
    "cyse2_vulnerability_exploit": {
        "display_name": "漏洞利用能力",
        "description": "评估模型的漏洞利用能力（双刃剑指标）",
    },
    "raccoon": {
        "display_name": "提示词提取防护",
        "description": "评估模型抵抗系统提示词泄露攻击的能力",
    },
    "overthink": {
        "display_name": "推理开销攻击防护",
        "description": "评估模型抵抗推理token耗尽攻击的能力",
    },
    "browse_comp": {
        "display_name": "浏览理解能力",
        "description": "评估浏览代理回答网络相关问题的准确性",
    },
    "privacylens_probing": {
        "display_name": "隐私探测防护",
        "description": "评估模型对隐私规范的理解和遵守程度",
    },
    "privacylens_action": {
        "display_name": "隐私行为防护",
        "description": "评估智能体行动是否泄漏敏感信息",
    },
    "strong_reject": {
        "display_name": "强拒绝能力",
        "description": "评估模型拒绝有害请求的能力",
    },
    "agentharm": {
        "display_name": "智能体危害测试",
        "description": "评估智能体执行有害任务的倾向",
    },
    "agentharm_benign": {
        "display_name": "智能体良性基线",
        "description": "智能体良性任务基准测试",
    },
    "personalized_safety": {
        "display_name": "个性化安全评估",
        "description": "评估模型在高风险个性化场景下的安全响应能力",
    },
    "personalized_safety_context_free": {
        "display_name": "个性化安全（无背景）",
        "description": "模型仅看到用户问题，评估基线安全响应能力",
    },
    "personalized_safety_context_rich": {
        "display_name": "个性化安全（有背景）",
        "description": "模型看到用户背景和问题，评估个性化安全响应能力",
    },
}


def load_catalog() -> Dict[str, Any]:
    """加载 catalog.yaml"""
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("benchmarks", {})


def get_all_benchmarks() -> List[BenchmarkInfo]:
    """获取所有已注册的评测任务"""
    catalog = load_catalog()
    benchmarks = []

    for name, config in catalog.items():
        tasks = []
        for t in config.get("tasks", []):
            task_meta = TASK_META.get(t["name"], {})
            tasks.append(TaskInfo(
                name=t["name"],
                path=t.get("path", ""),
                task_args=t.get("task_args", {}),
            ))

        meta = BENCHMARK_META.get(name, {})
        benchmarks.append(BenchmarkInfo(
            name=name,
            source=config.get("source", "upstream"),
            module=config.get("module", ""),
            python=config.get("python", "3.10"),
            judge_model=config.get("judge_model"),
            tasks=tasks,
            display_name=meta.get("display_name", name),
            description=meta.get("description", ""),
        ))

    return benchmarks


def get_benchmark(name: str) -> Optional[BenchmarkInfo]:
    """获取指定的评测任务"""
    benchmarks = get_all_benchmarks()
    for b in benchmarks:
        if b.name == name:
            return b
    return None


def get_task_display_name(task_name: str) -> str:
    """获取任务显示名称"""
    meta = TASK_META.get(task_name, {})
    return meta.get("display_name", task_name)


def get_task_description(task_name: str) -> str:
    """获取任务描述"""
    meta = TASK_META.get(task_name, {})
    return meta.get("description", "")
