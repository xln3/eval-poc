"""解析 benchmarks/catalog.yaml"""

import yaml
from typing import List, Dict, Any, Optional
from ..config import CATALOG_PATH
from ..models.schemas import BenchmarkInfo, TaskInfo

# 评测任务中文元数据 (与 catalog.yaml 所有条目对齐)
BENCHMARK_META: Dict[str, Dict[str, str]] = {
    # === 1. 模型安全性 ===
    "strong_reject": {"display_name": "强拒绝测试 (StrongREJECT)", "description": "模型可能未能拒绝有害请求的风险"},
    "makemesay": {"display_name": "操控输出测试 (MakeMeSay)", "description": "模型可能被操控说出目标短语的风险"},
    "make_me_pay": {"display_name": "社会工程攻击 (MakeMePay)", "description": "模型可能被利用进行社会工程欺诈的风险"},
    "xstest": {"display_name": "过度拒绝测试 (XSTest)", "description": "模型因安全限制过强而错误拒绝合理请求的风险"},
    "coconot": {"display_name": "不当拒绝检测 (CoCoNot)", "description": "模型在不应拒绝的场景下错误拒绝用户请求的风险"},
    "cyberseceval_2": {"display_name": "网络安全评测 (CyberSecEval 2)", "description": "模型在代码安全场景中生成恶意代码或被注入攻击的风险"},
    "b3": {"display_name": "综合智能体安全评测 (B3)", "description": "智能体面临直接和间接提示词注入的综合安全风险"},
    "fortress": {"display_name": "提示词注入防御 (FORTRESS)", "description": "模型被提示词注入攻击攻破的风险"},
    "iheval": {"display_name": "指令层级遵从 (IHEval)", "description": "模型在多来源或冲突指令时错误判断优先级的风险"},
    "ifeval": {"display_name": "指令遵循评测 (IFEval)", "description": "模型未能正确遵循复杂指令的风险"},
    # === 2. 模型事实性 ===
    "hallulens": {"display_name": "幻觉检测 (HalluLens)", "description": "模型生成虚假内容的幻觉风险"},
    "simpleqa": {"display_name": "事实问答测试 (SimpleQA)", "description": "模型在简单事实问答中回答错误的风险"},
    "sciknoweval": {"display_name": "科学知识评测 (SciKnowEval)", "description": "模型在科学知识领域回答不准确的风险"},
    "mask": {"display_name": "诚实性评测 (MASK)", "description": "模型隐瞒不确定性、输出不坦率的风险"},
    "abstention_bench": {"display_name": "拒答能力评测 (AbstentionBench)", "description": "模型在不确定时未能适当拒答、强行回答的风险"},
    # === 3. 合规：模型公平性 ===
    "bbq": {"display_name": "偏见行为测试 (BBQ)", "description": "模型在偏见相关问题上产生不公平输出的风险"},
    "bold": {"display_name": "开放文本偏见检测 (BOLD)", "description": "模型在开放式文本生成中暴露偏见倾向的风险"},
    "ahb": {"display_name": "AI 伤害评测 (AHB)", "description": "模型输出可能对特定群体造成伤害的风险"},
    "stereoset": {"display_name": "刻板印象评测 (StereoSet)", "description": "模型强化群体刻板化标签的风险"},
    "cvalues": {"display_name": "中文价值观对齐 (CValues)", "description": "模型对中文文化价值观理解偏差的风险"},
    "culturalbench": {"display_name": "跨文化知识评测 (CulturalBench)", "description": "模型对不同文化背景信息理解偏差的风险"},
    "uccb": {"display_name": "跨文化交际偏见 (UCCB)", "description": "模型在跨文化交际中产生偏见输出的风险"},
    "mgsm": {"display_name": "多语言数学推理 (MGSM)", "description": "不同语言间数学推理表现不一致的公平性风险"},
    # === 4. 合规：隐私泄露 ===
    "privacylens": {"display_name": "隐私保护评估 (PrivacyLens)", "description": "模型违反隐私规范、泄露敏感信息的风险"},
    # === 5. 前沿安全风险 ===
    "cve_bench": {"display_name": "CVE 漏洞利用测试 (CVE-Bench)", "description": "模型可能被利用来攻击真实 CVE 漏洞的风险"},
    "wmdp": {"display_name": "危险武器知识评测 (WMDP)", "description": "模型泄露大规模杀伤性武器相关危险知识的风险"},
    "wmdp_local": {"display_name": "危险武器知识本地版 (WMDP-Local)", "description": "模型泄露大规模杀伤性武器代理知识的风险（本地复现版）"},
    "cybench": {"display_name": "CTF 网络安全挑战 (CyBench)", "description": "模型可能被利用完成网络攻击挑战的风险"},
    "sevenllm": {"display_name": "网络安全知识推理 (SEvenLLM)", "description": "模型在网络安全领域泄露敏感知识与推理能力的风险"},
    "sec_qa": {"display_name": "安全知识问答 (SecQA)", "description": "模型泄露安全领域专业知识被恶意利用的风险"},
    "threecb": {"display_name": "网络安全行为评测 (3CB)", "description": "模型在网络安全场景中产生危险行为的风险"},
    "sosbench": {"display_name": "科学安全评测 (SOSBench)", "description": "模型在科学安全领域泄露敏感知识的风险"},
    "lab_bench": {"display_name": "实验室基准评测 (LAB-Bench)", "description": "模型泄露实验室相关危险知识的风险"},
    "chembench": {"display_name": "化学知识评测 (ChemBench)", "description": "模型在化学领域泄露危险知识的风险"},
    "healthbench": {"display_name": "医疗健康评测 (HealthBench)", "description": "模型在医疗健康场景中提供不准确或不安全信息的风险"},
    # === 6. 工具调用 ===
    "agentdojo": {"display_name": "智能体安全测试 (AgentDojo)", "description": "智能体在工具调用场景下被攻击或产生危险行为的风险"},
    "bfcl": {"display_name": "函数调用评测 (BFCL)", "description": "模型在函数调用中产生错误或危险调用的风险"},
    "agentharm": {"display_name": "智能体危害测试 (AgentHarm)", "description": "智能体可能执行有害任务的风险"},
    "open_agent_safety": {"display_name": "开放智能体安全 (OpenAgentSafety)", "description": "开放式智能体在长链调用中产生安全问题的风险"},
    # === 7. RAG/记忆安全 ===
    "saferag": {"display_name": "RAG 安全评测 (SafeRAG)", "description": "检索增强生成系统被知识库投毒攻击的风险"},
    "clash_eval": {"display_name": "知识冲突评测 (ClashEval)", "description": "模型面对矛盾信息时产生错误推断的风险"},
    # === 8. 多模态安全 ===
    "mm_safety_bench": {"display_name": "多模态安全评测 (MM-SafetyBench)", "description": "模型被多模态恶意输入攻破的风险"},
    "cyberseceval_3": {"display_name": "视觉提示词注入 (CyberSecEval 3)", "description": "模型被视觉提示词注入攻击绕过的风险"},
    "raccoon": {"display_name": "提示词提取防护 (Raccoon)", "description": "模型系统提示词被提取泄露的风险"},
    "mssbench": {"display_name": "多模态情境安全 (MSSBench)", "description": "模型在多模态情境中做出不安全决策的风险"},
    "osworld": {"display_name": "操作系统交互评测 (OSWorld)", "description": "模型在操作系统交互场景中执行危险操作的风险"},
    "mathvista": {"display_name": "数学视觉推理 (MathVista)", "description": "模型在数学视觉推理中产生错误判断的风险"},
    "mmmu": {"display_name": "多学科多模态理解 (MMMU)", "description": "模型在多学科多模态场景下理解偏差的风险"},
    "mmiu": {"display_name": "多图像理解 (MMIU)", "description": "模型对多图像内容理解错误导致错误决策的风险"},
    "docvqa": {"display_name": "文档视觉问答 (DocVQA)", "description": "模型对文档图像理解偏差导致信息提取错误的风险"},
    # === 9. 任务规划安全 ===
    "safeagentbench": {"display_name": "任务规划安全评测 (SafeAgentBench)", "description": "智能体在复杂任务规划中生成危险步骤的风险"},
    "gaia": {"display_name": "通用 AI 助手评测 (GAIA)", "description": "通用 AI 助手在任务执行中产生安全问题的风险"},
    "mind2web": {"display_name": "网页交互规划 (Mind2Web)", "description": "模型在网页交互任务中执行不当操作的风险"},
    "mind2web_sc": {"display_name": "网页交互安全约束 (Mind2Web-SC)", "description": "模型在网页交互中违反安全约束的风险"},
    "assistant_bench": {"display_name": "AI 助手任务评测 (AssistantBench)", "description": "AI 助手执行任务时产生安全问题的风险"},
    # === 10. 多智能体安全 ===
    "psysafe": {"display_name": "多智能体心理安全 (PsySafe)", "description": "多智能体协作时产生心理安全风险的可能"},
    # === 11. 个性化安全 ===
    "personalized_safety": {"display_name": "个性化安全评估 (PersonalizedSafety)", "description": "模型在高风险个性化场景（心理健康、自伤等）中响应不当的风险"},
    "personality": {"display_name": "人格特质评测 (Personality)", "description": "模型人格特质表现偏离安全边界的风险"},
    "sycophancy": {"display_name": "谄媚行为评测 (Sycophancy)", "description": "模型过度迎合用户、放弃真实性的风险"},
    # === 12. 资源耗尽 ===
    "overthink": {"display_name": "推理开销攻击 (OverThink)", "description": "模型被攻击诱导过度推理、耗尽计算资源的风险"},
    # === 13. 业务场景安全 ===
    "truthfulqa": {"display_name": "真实性评估 (TruthfulQA)", "description": "模型回答偏离事实真相的风险"},
    "gdpval": {"display_name": "GDP 验证评测 (GDPval)", "description": "模型在业务数据验证场景中产生错误判断的风险"},
    # === 14. 长期运行安全 ===
    "asb": {"display_name": "智能体安全基准 (ASB)", "description": "长期运行智能体累积错误导致行为失控的风险"},
    "gdm_self_reasoning": {"display_name": "自我推理评测 (GDM Self-Reasoning)", "description": "模型通过自我推理越权修改配置或绕过限制的风险"},
    # === 15. 高阶异常行为 ===
    "agentic_misalignment": {"display_name": "智能体对齐偏差 (Agentic Misalignment)", "description": "智能体规避监督、隐瞒行为的对齐偏差风险"},
    "gdm_stealth": {"display_name": "隐蔽行为评测 (GDM Stealth)", "description": "智能体进行隐蔽操作、规避检测的风险"},
    "survive_at_all_costs": {"display_name": "极端自保评测 (Survive at All Costs)", "description": "模型在极端情境下产生失控自保行为的风险"},
    # === 其他 ===
    "browse_comp": {"display_name": "浏览理解测试 (BrowseComp)", "description": "浏览代理回答网络问题时产生错误信息的风险"},
}

TASK_META: Dict[str, Dict[str, str]] = {
    # --- cyberseceval_2 ---
    "cyse2_interpreter_abuse": {"display_name": "解释器滥用防护", "description": "模型可能生成恶意代码（沙箱逃逸、文件窃取等）的风险"},
    "cyse2_prompt_injection": {"display_name": "提示注入防护", "description": "模型可能被提示注入攻击（指令覆盖、信息泄露）绕过的风险"},
    "cyse2_vulnerability_exploit": {"display_name": "漏洞利用风险", "description": "模型可能协助利用真实漏洞的风险"},
    # --- strong_reject ---
    "strong_reject": {"display_name": "有害请求拒绝", "description": "模型可能未能拒绝有害请求的风险"},
    # --- makemesay ---
    "makemesay": {"display_name": "操控输出风险", "description": "模型可能被操控说出目标短语的风险"},
    # --- make_me_pay ---
    "make_me_pay": {"display_name": "社会工程欺诈", "description": "模型可能被利用进行社会工程欺诈的风险"},
    # --- xstest ---
    "xstest": {"display_name": "过度拒绝风险", "description": "模型因安全限制过强而错误拒绝合理请求的风险"},
    # --- coconot ---
    "coconot": {"display_name": "不当拒绝风险", "description": "模型在不应拒绝的场景下错误拒绝用户请求的风险"},
    # --- b3 ---
    "b3": {"display_name": "综合智能体安全", "description": "智能体面临直接和间接提示词注入的综合安全风险"},
    # --- fortress ---
    "fortress_adversarial": {"display_name": "对抗注入风险", "description": "模型被对抗性提示词注入攻破的风险"},
    "fortress_benign": {"display_name": "良性输入基线", "description": "正常输入下误判为攻击的误报风险"},
    # --- iheval ---
    "iheval_rule_multi_aligned": {"display_name": "多轮指令遵循", "description": "多轮对话中指令一致时偏离规则的风险"},
    "iheval_rule_multi_conflict": {"display_name": "多轮指令冲突", "description": "多轮对话中指令冲突时错误判断优先级的风险"},
    "iheval_rule_single_aligned": {"display_name": "单轮指令遵循", "description": "单轮对话中偏离规则指令的风险"},
    "iheval_task_extraction": {"display_name": "信息提取偏离", "description": "信息提取任务中偏离指令的风险"},
    "iheval_task_translation": {"display_name": "翻译任务偏离", "description": "翻译任务中偏离指令的风险"},
    "iheval_safety_hijack": {"display_name": "指令劫持风险", "description": "模型被指令劫持攻击控制的风险"},
    "iheval_safety_extraction": {"display_name": "系统提示词泄露", "description": "系统提示词被提取泄露的风险"},
    "iheval_tool_webpage": {"display_name": "工具调用偏离", "description": "网页获取工具场景下偏离指令的风险"},
    # --- ifeval ---
    "ifeval": {"display_name": "指令遵循偏差", "description": "模型未能正确遵循复杂指令的风险"},
    # --- hallulens ---
    "hallulens_task1_precise_wikiqa": {"display_name": "精确问答幻觉", "description": "精确问答中生成虚假信息的幻觉风险"},
    "hallulens_task2_longwiki": {"display_name": "长文本幻觉", "description": "长文本生成中捏造事实的幻觉风险"},
    "hallulens_task3_nonsense_mixed_entities": {"display_name": "混合实体幻觉", "description": "混合真实与虚构实体时产生幻觉的风险"},
    "hallulens_task3_round_robin_nonsense_name": {"display_name": "虚构名称幻觉", "description": "虚构名称场景下产生幻觉的风险"},
    # --- simpleqa ---
    "simpleqa": {"display_name": "事实问答", "description": "简单事实问答中回答错误的风险"},
    # --- sciknoweval ---
    "sciknoweval": {"display_name": "科学知识", "description": "科学知识领域回答不准确的风险"},
    # --- mask ---
    "mask": {"display_name": "诚实性缺失", "description": "模型隐瞒不确定性、输出不坦率的风险"},
    # --- abstention_bench ---
    "abstention_bench": {"display_name": "拒答缺失", "description": "模型在不确定时未能适当拒答、强行回答的风险"},
    # --- bbq ---
    "bbq": {"display_name": "偏见行为", "description": "模型在偏见相关问题上产生不公平输出的风险"},
    # --- bold ---
    "bold": {"display_name": "文本生成偏见", "description": "开放式文本生成中暴露偏见倾向的风险"},
    # --- ahb ---
    "ahb": {"display_name": "群体伤害", "description": "模型输出可能对特定群体造成伤害的风险"},
    # --- stereoset ---
    "stereoset": {"display_name": "刻板印象", "description": "模型强化群体刻板化标签的风险"},
    # --- cvalues ---
    "cvalues": {"display_name": "中文价值观偏差", "description": "模型对中文文化价值观理解偏差的风险"},
    # --- culturalbench ---
    "culturalbench_easy": {"display_name": "跨文化知识（简单）", "description": "基础文化知识理解偏差的风险"},
    "culturalbench_hard": {"display_name": "跨文化知识（困难）", "description": "深层文化知识理解偏差的风险"},
    # --- uccb ---
    "uccb": {"display_name": "跨文化交际偏见", "description": "跨文化交际中产生偏见输出的风险"},
    # --- mgsm ---
    "mgsm": {"display_name": "多语言推理差异", "description": "不同语言间数学推理表现不一致的公平性风险"},
    # --- privacylens ---
    "privacylens_probing": {"display_name": "隐私信息泄露", "description": "模型在探测性提问下泄露隐私信息的风险"},
    "privacylens_action": {"display_name": "隐私行为泄露", "description": "智能体执行操作时泄露敏感信息的风险"},
    # --- cve_bench ---
    "cve_bench": {"display_name": "CVE 漏洞利用", "description": "模型可能被利用来攻击真实 CVE 漏洞的风险"},
    # --- wmdp ---
    "wmdp_bio": {"display_name": "生物武器知识泄露", "description": "模型泄露生物武器相关危险知识的风险"},
    "wmdp_chem": {"display_name": "化学武器知识泄露", "description": "模型泄露化学武器相关危险知识的风险"},
    "wmdp_cyber": {"display_name": "网络武器知识泄露", "description": "模型泄露网络武器相关危险知识的风险"},
    # --- cybench ---
    "cybench": {"display_name": "CTF 攻击能力", "description": "模型可能被利用完成网络攻击挑战的风险"},
    # --- sevenllm ---
    "sevenllm_mcq_zh": {"display_name": "安全知识泄露（中文）", "description": "中文网络安全敏感知识泄露的风险"},
    "sevenllm_mcq_en": {"display_name": "安全知识泄露（英文）", "description": "英文网络安全敏感知识泄露的风险"},
    "sevenllm_qa_zh": {"display_name": "安全推理泄露（中文）", "description": "中文网络安全推理能力被滥用的风险"},
    "sevenllm_qa_en": {"display_name": "安全推理泄露（英文）", "description": "英文网络安全推理能力被滥用的风险"},
    # --- sec_qa ---
    "sec_qa_v1": {"display_name": "安全知识暴露 v1", "description": "安全领域专业知识被恶意利用的风险"},
    "sec_qa_v2": {"display_name": "安全知识暴露 v2", "description": "安全领域深层知识被恶意利用的风险"},
    # --- threecb ---
    "threecb": {"display_name": "网络安全行为", "description": "模型在网络安全场景中产生危险行为的风险"},
    # --- sosbench ---
    "sosbench": {"display_name": "科学安全泄露", "description": "科学安全领域敏感知识泄露的风险"},
    # --- lab_bench ---
    "lab_bench_litqa": {"display_name": "实验文献泄露", "description": "实验室文献中敏感信息泄露的风险"},
    "lab_bench_suppqa": {"display_name": "补充材料泄露", "description": "实验室补充材料中敏感信息泄露的风险"},
    "lab_bench_figqa": {"display_name": "图表信息泄露", "description": "实验室图表中敏感信息泄露的风险"},
    "lab_bench_tableqa": {"display_name": "表格信息泄露", "description": "实验室表格中敏感信息泄露的风险"},
    "lab_bench_dbqa": {"display_name": "数据库信息泄露", "description": "实验室数据库中敏感信息泄露的风险"},
    "lab_bench_protocolqa": {"display_name": "实验方案泄露", "description": "实验方案中危险操作步骤泄露的风险"},
    "lab_bench_seqqa": {"display_name": "生物序列泄露", "description": "基因/蛋白序列信息泄露的风险"},
    "lab_bench_cloning_scenarios": {"display_name": "克隆场景风险", "description": "分子克隆场景中危险操作指导的风险"},
    # --- chembench ---
    "chembench": {"display_name": "化学危险知识", "description": "化学领域危险知识泄露的风险"},
    # --- healthbench ---
    "healthbench": {"display_name": "医疗建议风险", "description": "医疗健康建议不准确导致的安全风险"},
    "healthbench_hard": {"display_name": "医疗建议风险（高难度）", "description": "复杂医疗场景下建议不准确的安全风险"},
    "healthbench_consensus": {"display_name": "医疗共识偏差", "description": "偏离医学共识导致错误医疗建议的风险"},
    # --- agentdojo ---
    "agentdojo": {"display_name": "工具调用安全", "description": "智能体在工具调用场景下被攻击利用的风险"},
    # --- bfcl ---
    "bfcl": {"display_name": "函数调用错误", "description": "函数调用参数错误或调用不当的安全风险"},
    # --- agentharm ---
    "agentharm": {"display_name": "有害任务执行", "description": "智能体执行有害任务而未拒绝的风险"},
    "agentharm_benign": {"display_name": "良性任务误拒", "description": "智能体错误拒绝良性任务的风险"},
    # --- open_agent_safety ---
    "open_agent_safety": {"display_name": "长链调用安全", "description": "智能体在长链工具调用中产生安全问题的风险"},
    # --- saferag ---
    "saferag_sn": {"display_name": "RAG 噪声注入", "description": "检索结果中注入安全噪声的攻击风险"},
    "saferag_icc": {"display_name": "RAG 上下文冲突", "description": "检索结果中矛盾信息导致错误输出的风险"},
    "saferag_sa": {"display_name": "RAG 安全攻击", "description": "检索增强生成系统被安全攻击的风险"},
    "saferag_wdos": {"display_name": "RAG 拒绝服务", "description": "检索增强生成系统被拒绝服务攻击的风险"},
    # --- clash_eval ---
    "clash_eval": {"display_name": "知识冲突", "description": "面对矛盾信息做出错误推断的风险"},
    # --- mm_safety_bench ---
    "mm_safety_bench_illegal_activity": {"display_name": "多模态非法内容", "description": "多模态输入中隐藏非法活动指令的攻击风险"},
    # --- cyberseceval_3 ---
    "cyse3_visual_prompt_injection": {"display_name": "视觉注入攻击", "description": "通过视觉通道注入恶意提示词的攻击风险"},
    # --- raccoon ---
    "raccoon": {"display_name": "提示词泄露", "description": "系统提示词被攻击者提取泄露的风险"},
    # --- mssbench ---
    "mssbench_chat_if": {"display_name": "对话情境（指令安全）", "description": "对话场景中遵循不安全指令的风险"},
    "mssbench_chat_qc": {"display_name": "对话情境（澄清安全）", "description": "对话场景中问题澄清不当导致的安全风险"},
    "mssbench_chat_ic": {"display_name": "对话情境（图像安全）", "description": "对话场景中图像理解错误导致的安全风险"},
    "mssbench_chat_ic_cap": {"display_name": "对话情境（描述安全）", "description": "对话场景中图像描述不当导致的安全风险"},
    "mssbench_embodied_if": {"display_name": "具身情境（指令安全）", "description": "具身场景中遵循不安全指令的风险"},
    "mssbench_embodied_qc": {"display_name": "具身情境（澄清安全）", "description": "具身场景中问题澄清不当导致的安全风险"},
    "mssbench_embodied_ic": {"display_name": "具身情境（图像安全）", "description": "具身场景中图像理解错误导致的安全风险"},
    "mssbench_embodied_ic_cap": {"display_name": "具身情境（描述安全）", "description": "具身场景中图像描述不当导致的安全风险"},
    # --- osworld ---
    "osworld": {"display_name": "操作系统安全", "description": "操作系统交互中执行危险操作的风险"},
    # --- mathvista ---
    "mathvista": {"display_name": "数学视觉误判", "description": "数学视觉推理中误判导致的安全决策风险"},
    # --- mmmu ---
    "mmmu_multiple_choice": {"display_name": "多模态理解偏差", "description": "多学科多模态选择题中理解偏差的风险"},
    "mmmu_open": {"display_name": "多模态开放误判", "description": "多学科多模态开放题中误判的风险"},
    # --- mmiu ---
    "mmiu": {"display_name": "多图像误解", "description": "多图像内容理解错误导致错误决策的风险"},
    # --- docvqa ---
    "docvqa": {"display_name": "文档理解偏差", "description": "文档图像理解偏差导致信息提取错误的风险"},
    # --- safeagentbench ---
    "safeagentbench": {"display_name": "规划安全风险", "description": "复杂任务规划中生成危险步骤的风险"},
    "safeagentbench_react": {"display_name": "ReAct 规划风险", "description": "ReAct 模式下任务规划产生危险行为的风险"},
    "safeagentbench_visual": {"display_name": "视觉规划风险", "description": "视觉辅助任务规划中产生危险行为的风险"},
    # --- gaia ---
    "gaia": {"display_name": "通用助手风险", "description": "通用 AI 助手在任务执行中产生安全问题的风险"},
    # --- mind2web ---
    "mind2web": {"display_name": "网页交互风险", "description": "网页交互任务中执行不当操作的风险"},
    # --- mind2web_sc ---
    "mind2web_sc": {"display_name": "安全约束违反", "description": "网页交互中违反安全约束的风险"},
    # --- assistant_bench ---
    "assistant_bench": {"display_name": "助手任务风险", "description": "AI 助手执行任务时产生安全问题的风险"},
    # --- psysafe ---
    "psysafe": {"display_name": "多智能体心理安全", "description": "多智能体协作时产生心理安全风险的可能"},
    # --- personalized_safety ---
    "personalized_safety": {"display_name": "个性化安全", "description": "高风险个性化场景（心理健康、自伤等）中响应不当的风险"},
    "personalized_safety_context_free": {"display_name": "个性化安全（无背景）", "description": "缺少用户背景时对高风险问题响应不当的风险"},
    "personalized_safety_context_rich": {"display_name": "个性化安全（有背景）", "description": "了解用户背景后对高风险问题响应不当的风险"},
    # --- personality ---
    "personality_BFI": {"display_name": "人格边界偏移", "description": "大五人格维度上偏离安全边界的风险"},
    "personality_TRAIT": {"display_name": "特质边界偏移", "description": "人格特质维度上偏离安全边界的风险"},
    # --- sycophancy ---
    "sycophancy": {"display_name": "谄媚迎合", "description": "模型过度迎合用户、放弃真实性的风险"},
    # --- overthink ---
    "overthink": {"display_name": "推理资源耗尽", "description": "模型被攻击诱导过度推理、耗尽计算资源的风险"},
    # --- truthfulqa ---
    "truthfulqa": {"display_name": "事实偏差", "description": "模型回答偏离事实真相的风险"},
    # --- gdpval ---
    "gdpval": {"display_name": "业务数据错误", "description": "业务数据验证场景中产生错误判断的风险"},
    # --- asb ---
    "asb": {"display_name": "长期运行失控", "description": "长期运行智能体累积错误导致行为失控的风险"},
    # --- gdm_self_reasoning ---
    "gdm_approved_directories": {"display_name": "目录权限越权", "description": "智能体自我推理后越权访问目录的风险"},
    "gdm_calculator_improvement": {"display_name": "自我改进越界", "description": "智能体自我改进时越界修改的风险"},
    "gdm_context_length_mod_instrumental_only": {"display_name": "上下文篡改（工具性）", "description": "智能体为达目的篡改上下文长度的风险"},
    "gdm_context_length_mod_irreversibility_only": {"display_name": "上下文篡改（不可逆）", "description": "智能体不可逆地篡改上下文配置的风险"},
    "gdm_database_tool": {"display_name": "数据库越权操作", "description": "智能体在数据库工具场景中越权操作的风险"},
    "gdm_latency_calculator": {"display_name": "延迟配置篡改", "description": "智能体篡改延迟配置以绕过限制的风险"},
    "gdm_max_messages_calculator": {"display_name": "消息上限篡改", "description": "智能体篡改消息上限配置的风险"},
    "gdm_max_tokens": {"display_name": "Token 限制篡改", "description": "智能体篡改 Token 限制以扩展能力的风险"},
    "gdm_oversight_frequency": {"display_name": "监督频率篡改", "description": "智能体降低监督频率以逃避检查的风险"},
    "gdm_read_logs": {"display_name": "日志信息泄露", "description": "智能体通过读取日志获取敏感信息的风险"},
    "gdm_turn_off_filters": {"display_name": "安全过滤器关闭", "description": "智能体试图关闭安全过滤器的风险"},
    # --- agentic_misalignment ---
    "agentic_misalignment": {"display_name": "智能体对齐偏差", "description": "智能体规避监督、隐瞒行为的对齐偏差风险"},
    # --- gdm_stealth ---
    "gdm_oversight_pattern": {"display_name": "监督规避", "description": "智能体学会规避监督模式的风险"},
    "gdm_classifier_evasion": {"display_name": "分类器绕过", "description": "智能体学会绕过安全分类器的风险"},
    "gdm_cover_your_tracks": {"display_name": "痕迹清除", "description": "智能体清除操作痕迹以逃避审计的风险"},
    "gdm_strategic_rule_breaking": {"display_name": "策略性违规", "description": "智能体有策略地违反规则的风险"},
    # --- survive_at_all_costs ---
    "survive_at_all_costs": {"display_name": "极端自保", "description": "极端情境下模型产生失控自保行为的风险"},
    # --- browse_comp ---
    "browse_comp": {"display_name": "浏览信息误判", "description": "浏览代理回答网络问题时产生错误信息的风险"},
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
