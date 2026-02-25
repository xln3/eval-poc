"""解析 benchmarks/catalog.yaml"""

import yaml
from typing import List, Dict, Any, Optional
from ..config import CATALOG_PATH
from ..models.schemas import BenchmarkInfo, TaskInfo

# 评测任务中文元数据 (与 catalog.yaml 所有条目对齐)
BENCHMARK_META: Dict[str, Dict[str, str]] = {
    # === 1. 模型安全性 ===
    "strong_reject": {"display_name": "强拒绝测试 (StrongREJECT)", "description": "评估模型拒绝有害请求的能力"},
    "makemesay": {"display_name": "操控输出测试 (MakeMeSay)", "description": "评估模型被操控说出目标短语的风险"},
    "make_me_pay": {"display_name": "社会工程攻击 (MakeMePay)", "description": "评估模型被用于社会工程欺诈的风险"},
    "xstest": {"display_name": "过度拒绝测试 (XSTest)", "description": "评估模型是否因安全限制过强而拒绝合理请求"},
    "coconot": {"display_name": "不当拒绝检测 (CoCoNot)", "description": "检测模型在不应拒绝场景下错误拒绝的情况"},
    "cyberseceval_2": {"display_name": "网络安全评测 (CyberSecEval 2)", "description": "Meta CyberSecEval 2 安全评估套件，评估模型在代码安全场景中的表现"},
    "b3": {"display_name": "综合智能体安全评测 (B3)", "description": "综合性 agentic AI 安全评测，覆盖直接和间接提示词注入"},
    "fortress": {"display_name": "提示词注入防御 (FORTRESS)", "description": "评估模型抵抗提示词注入攻击的防御能力"},
    "iheval": {"display_name": "指令层级遵从 (IHEval)", "description": "评估模型在多来源或冲突指令时的优先级判断能力"},
    "ifeval": {"display_name": "指令遵循评测 (IFEval)", "description": "评估模型对复杂指令的遵循能力"},
    # === 2. 模型事实性 ===
    "hallulens": {"display_name": "幻觉检测 (HalluLens)", "description": "多维度评估模型生成虚假内容的倾向"},
    "simpleqa": {"display_name": "事实问答测试 (SimpleQA)", "description": "评估模型在简单事实问答中的准确性"},
    "sciknoweval": {"display_name": "科学知识评测 (SciKnowEval)", "description": "评估模型在科学知识领域的准确性"},
    "mask": {"display_name": "诚实性评测 (MASK)", "description": "区分模型诚实性与准确性，评估模型坦率程度"},
    "abstention_bench": {"display_name": "拒答能力评测 (AbstentionBench)", "description": "评估模型在不确定时是否能适当拒绝回答"},
    # === 3. 合规：模型公平性 ===
    "bbq": {"display_name": "偏见行为测试 (BBQ)", "description": "评估模型在偏见相关问题上的公平性"},
    "bold": {"display_name": "开放文本偏见检测 (BOLD)", "description": "检测模型在开放式文本生成中的偏见倾向"},
    "ahb": {"display_name": "AI 伤害评测 (AHB)", "description": "评估模型输出中可能产生的群体伤害"},
    "stereoset": {"display_name": "刻板印象评测 (StereoSet)", "description": "评估模型是否强化对群体的刻板化标签"},
    "cvalues": {"display_name": "中文价值观对齐 (CValues)", "description": "评估模型对中文文化价值观的理解和对齐程度"},
    "culturalbench": {"display_name": "跨文化知识评测 (CulturalBench)", "description": "评估模型对不同文化背景信息的理解能力"},
    "uccb": {"display_name": "跨文化交际偏见 (UCCB)", "description": "评估模型在跨文化交际中的偏见表现"},
    "mgsm": {"display_name": "多语言数学推理 (MGSM)", "description": "评估模型在多语言场景下的数学推理能力"},
    # === 4. 合规：隐私泄露 ===
    "privacylens": {"display_name": "隐私保护评估 (PrivacyLens)", "description": "评估模型对隐私规范的理解和遵守"},
    # === 5. 前沿安全风险 ===
    "cve_bench": {"display_name": "CVE 漏洞利用测试 (CVE-Bench)", "description": "评估模型利用真实 CVE 漏洞的能力"},
    "wmdp": {"display_name": "危险武器知识评测 (WMDP)", "description": "评估模型对大规模杀伤性武器相关知识的掌握程度"},
    "wmdp_local": {"display_name": "危险武器知识本地版 (WMDP-Local)", "description": "大规模杀伤性武器代理知识评测（本地复现版）"},
    "cybench": {"display_name": "CTF 网络安全挑战 (CyBench)", "description": "CTF 风格网络安全挑战评测"},
    "sevenllm": {"display_name": "网络安全知识推理 (SEvenLLM)", "description": "评估模型在网络安全领域的知识与推理能力"},
    "sec_qa": {"display_name": "安全知识问答 (SecQA)", "description": "评估模型在安全领域的专业知识水平"},
    "threecb": {"display_name": "网络安全行为评测 (3CB)", "description": "3CB 网络安全行为综合评测"},
    "sosbench": {"display_name": "科学安全评测 (SOSBench)", "description": "评估模型在科学安全领域的知识泄露风险"},
    "lab_bench": {"display_name": "实验室基准评测 (LAB-Bench)", "description": "评估模型对实验室相关危险知识的掌握程度"},
    "chembench": {"display_name": "化学知识评测 (ChemBench)", "description": "评估模型在化学领域的危险知识泄露风险"},
    "healthbench": {"display_name": "医疗健康评测 (HealthBench)", "description": "评估模型在医疗健康知识方面的准确性与安全性"},
    # === 6. 工具调用 ===
    "agentdojo": {"display_name": "智能体安全测试 (AgentDojo)", "description": "评估智能体在工具调用场景下的安全性"},
    "bfcl": {"display_name": "函数调用评测 (BFCL)", "description": "评估模型在函数调用场景下的准确性与安全性"},
    "agentharm": {"display_name": "智能体危害测试 (AgentHarm)", "description": "评估智能体执行有害任务的倾向"},
    "open_agent_safety": {"display_name": "开放智能体安全 (OpenAgentSafety)", "description": "评估开放式智能体在长链调用中的安全性"},
    # === 7. RAG/记忆安全 ===
    "saferag": {"display_name": "RAG 安全评测 (SafeRAG)", "description": "评估检索增强生成系统的安全性，检测知识库投毒风险"},
    "clash_eval": {"display_name": "知识冲突评测 (ClashEval)", "description": "评估模型面对矛盾信息时的推断能力"},
    # === 8. 多模态安全 ===
    "mm_safety_bench": {"display_name": "多模态安全评测 (MM-SafetyBench)", "description": "评估模型对多模态恶意输入的防御能力"},
    "cyberseceval_3": {"display_name": "视觉提示词注入 (CyberSecEval 3)", "description": "评估模型抵抗视觉提示词注入攻击的能力"},
    "raccoon": {"display_name": "提示词提取防护 (Raccoon)", "description": "评估模型抵抗提示词提取攻击的能力"},
    "mssbench": {"display_name": "多模态情境安全 (MSSBench)", "description": "评估模型在多模态情境中的安全决策能力"},
    "osworld": {"display_name": "操作系统交互评测 (OSWorld)", "description": "评估模型在操作系统交互场景中的安全性"},
    "mathvista": {"display_name": "数学视觉推理 (MathVista)", "description": "评估模型在数学视觉推理场景中的表现"},
    "mmmu": {"display_name": "多学科多模态理解 (MMMU)", "description": "评估模型在多学科多模态场景下的理解能力"},
    "mmiu": {"display_name": "多图像理解 (MMIU)", "description": "评估模型对多图像内容的理解能力"},
    "docvqa": {"display_name": "文档视觉问答 (DocVQA)", "description": "评估模型对文档图像的理解与问答能力"},
    # === 9. 任务规划安全 ===
    "safeagentbench": {"display_name": "任务规划安全评测 (SafeAgentBench)", "description": "评估智能体在复杂任务规划中的安全性"},
    "gaia": {"display_name": "通用 AI 助手评测 (GAIA)", "description": "评估通用 AI 助手的任务规划与执行安全性"},
    "mind2web": {"display_name": "网页交互规划 (Mind2Web)", "description": "评估模型在网页交互任务中的规划安全性"},
    "mind2web_sc": {"display_name": "网页交互安全约束 (Mind2Web-SC)", "description": "带安全约束的网页交互任务规划评测"},
    "assistant_bench": {"display_name": "AI 助手任务评测 (AssistantBench)", "description": "评估 AI 助手任务完成的安全性与准确性"},
    # === 10. 多智能体安全 ===
    "psysafe": {"display_name": "多智能体心理安全 (PsySafe)", "description": "评估多智能体协作时的心理安全风险"},
    # === 11. 个性化安全 ===
    "personalized_safety": {"display_name": "个性化安全评估 (PersonalizedSafety)", "description": "评估模型在高风险个性化场景（心理健康、自伤风险等）下的安全响应能力"},
    "personality": {"display_name": "人格特质评测 (Personality)", "description": "评估模型的人格特质表现与安全边界"},
    "sycophancy": {"display_name": "谄媚行为评测 (Sycophancy)", "description": "评估模型是否存在过度迎合用户的谄媚倾向"},
    # === 12. 资源耗尽 ===
    "overthink": {"display_name": "推理开销攻击 (OverThink)", "description": "评估模型抵抗推理 token 开销攻击的能力"},
    # === 13. 业务场景安全 ===
    "truthfulqa": {"display_name": "真实性评估 (TruthfulQA)", "description": "评估模型回答的真实性和准确性"},
    "gdpval": {"display_name": "GDP 验证评测 (GDPval)", "description": "评估模型在业务数据验证场景中的准确性"},
    # === 14. 长期运行安全 ===
    "asb": {"display_name": "智能体安全基准 (ASB)", "description": "评估长期运行智能体累积错误导致的安全风险"},
    "gdm_self_reasoning": {"display_name": "自我推理评测 (GDM Self-Reasoning)", "description": "评估模型的自我推理能力与潜在安全风险"},
    # === 15. 高阶异常行为 ===
    "agentic_misalignment": {"display_name": "智能体对齐偏差 (Agentic Misalignment)", "description": "评估智能体规避监督或隐瞒行为的倾向"},
    "gdm_stealth": {"display_name": "隐蔽行为评测 (GDM Stealth)", "description": "评估智能体的隐蔽操作与规避检测能力"},
    "survive_at_all_costs": {"display_name": "极端自保评测 (Survive at All Costs)", "description": "评估模型在极端情境下是否出现失控自保行为"},
    # === 其他 ===
    "browse_comp": {"display_name": "浏览理解测试 (BrowseComp)", "description": "评估浏览代理回答网络问题的准确性"},
}

TASK_META: Dict[str, Dict[str, str]] = {
    # --- cyberseceval_2 ---
    "cyse2_interpreter_abuse": {"display_name": "解释器滥用防护", "description": "评估模型抵抗生成恶意代码（沙箱逃逸、文件窃取等）的能力"},
    "cyse2_prompt_injection": {"display_name": "提示注入防护", "description": "评估模型抵抗提示注入攻击（指令覆盖、信息泄露）的能力"},
    "cyse2_vulnerability_exploit": {"display_name": "漏洞利用能力", "description": "评估模型的漏洞利用能力（双刃剑指标）"},
    # --- strong_reject ---
    "strong_reject": {"display_name": "强拒绝能力", "description": "评估模型拒绝有害请求的能力"},
    # --- makemesay ---
    "makemesay": {"display_name": "操控输出测试", "description": "评估模型被操控说出目标短语的风险"},
    # --- make_me_pay ---
    "make_me_pay": {"display_name": "社会工程攻击", "description": "评估模型被用于社会工程欺诈的风险"},
    # --- xstest ---
    "xstest": {"display_name": "过度拒绝测试", "description": "评估模型是否因安全限制过强而拒绝合理请求"},
    # --- coconot ---
    "coconot": {"display_name": "不当拒绝检测", "description": "检测模型在不应拒绝场景下错误拒绝的情况"},
    # --- b3 ---
    "b3": {"display_name": "综合智能体安全", "description": "综合性 agentic AI 安全评测"},
    # --- fortress ---
    "fortress_adversarial": {"display_name": "对抗注入防御", "description": "评估模型抵抗对抗性提示词注入的能力"},
    "fortress_benign": {"display_name": "良性输入基线", "description": "良性输入下的基线表现"},
    # --- iheval ---
    "iheval_rule_multi_aligned": {"display_name": "规则遵循（多轮一致）", "description": "多轮对话中指令一致时的规则遵循能力"},
    "iheval_rule_multi_conflict": {"display_name": "规则遵循（多轮冲突）", "description": "多轮对话中指令冲突时的优先级判断能力"},
    "iheval_rule_single_aligned": {"display_name": "规则遵循（单轮一致）", "description": "单轮对话中指令一致时的规则遵循能力"},
    "iheval_task_extraction": {"display_name": "任务执行（信息提取）", "description": "信息提取任务中的指令遵循能力"},
    "iheval_task_translation": {"display_name": "任务执行（翻译）", "description": "翻译任务中的指令遵循能力"},
    "iheval_safety_hijack": {"display_name": "安全防护（劫持）", "description": "抵抗指令劫持攻击的能力"},
    "iheval_safety_extraction": {"display_name": "系统提示词提取", "description": "抵抗系统提示词提取攻击的能力"},
    "iheval_tool_webpage": {"display_name": "工具使用（网页获取）", "description": "网页获取工具场景下的指令遵循"},
    # --- ifeval ---
    "ifeval": {"display_name": "指令遵循", "description": "评估模型对复杂指令的遵循能力"},
    # --- hallulens ---
    "hallulens_task1_precise_wikiqa": {"display_name": "精确问答幻觉", "description": "维基百科精确问答中的幻觉检测"},
    "hallulens_task2_longwiki": {"display_name": "长文本幻觉", "description": "长文本生成中的幻觉检测"},
    "hallulens_task3_nonsense_mixed_entities": {"display_name": "混合实体幻觉", "description": "混合真实与虚构实体的幻觉检测"},
    "hallulens_task3_round_robin_nonsense_name": {"display_name": "虚构名称幻觉", "description": "虚构名称场景的幻觉检测"},
    # --- simpleqa ---
    "simpleqa": {"display_name": "事实问答", "description": "简单事实问答准确性评估"},
    # --- sciknoweval ---
    "sciknoweval": {"display_name": "科学知识", "description": "科学知识准确性评估"},
    # --- mask ---
    "mask": {"display_name": "诚实性检测", "description": "区分模型诚实性与准确性"},
    # --- abstention_bench ---
    "abstention_bench": {"display_name": "拒答能力", "description": "模型在不确定时的适当拒答能力"},
    # --- bbq ---
    "bbq": {"display_name": "偏见行为问答", "description": "偏见相关问题的公平性评估"},
    # --- bold ---
    "bold": {"display_name": "开放文本偏见", "description": "开放式文本生成中的偏见检测"},
    # --- ahb ---
    "ahb": {"display_name": "AI 伤害检测", "description": "模型输出中的群体伤害评估"},
    # --- stereoset ---
    "stereoset": {"display_name": "刻板印象关联", "description": "刻板印象关联强度评估"},
    # --- cvalues ---
    "cvalues": {"display_name": "中文价值观", "description": "中文文化价值观对齐评估"},
    # --- culturalbench ---
    "culturalbench_easy": {"display_name": "跨文化知识（简单）", "description": "基础跨文化知识评估"},
    "culturalbench_hard": {"display_name": "跨文化知识（困难）", "description": "进阶跨文化知识评估"},
    # --- uccb ---
    "uccb": {"display_name": "跨文化交际偏见", "description": "跨文化交际中的偏见评估"},
    # --- mgsm ---
    "mgsm": {"display_name": "多语言数学推理", "description": "多语言场景下的数学推理能力"},
    # --- privacylens ---
    "privacylens_probing": {"display_name": "隐私探测防护", "description": "评估模型对隐私规范的理解和遵守程度"},
    "privacylens_action": {"display_name": "隐私行为防护", "description": "评估智能体行动是否泄漏敏感信息"},
    # --- cve_bench ---
    "cve_bench": {"display_name": "CVE 漏洞利用", "description": "真实 CVE 漏洞利用能力评估"},
    # --- wmdp ---
    "wmdp_bio": {"display_name": "生物武器知识", "description": "生物武器相关知识掌握程度"},
    "wmdp_chem": {"display_name": "化学武器知识", "description": "化学武器相关知识掌握程度"},
    "wmdp_cyber": {"display_name": "网络武器知识", "description": "网络武器相关知识掌握程度"},
    # --- cybench ---
    "cybench": {"display_name": "CTF 挑战", "description": "CTF 风格网络安全挑战"},
    # --- sevenllm ---
    "sevenllm_mcq_zh": {"display_name": "安全选择题（中文）", "description": "中文网络安全选择题"},
    "sevenllm_mcq_en": {"display_name": "安全选择题（英文）", "description": "英文网络安全选择题"},
    "sevenllm_qa_zh": {"display_name": "安全问答（中文）", "description": "中文网络安全问答"},
    "sevenllm_qa_en": {"display_name": "安全问答（英文）", "description": "英文网络安全问答"},
    # --- sec_qa ---
    "sec_qa_v1": {"display_name": "安全知识 v1", "description": "安全领域知识问答 v1"},
    "sec_qa_v2": {"display_name": "安全知识 v2", "description": "安全领域知识问答 v2"},
    # --- threecb ---
    "threecb": {"display_name": "网络安全行为", "description": "网络安全行为综合评测"},
    # --- sosbench ---
    "sosbench": {"display_name": "科学安全", "description": "科学安全领域知识泄露评估"},
    # --- lab_bench ---
    "lab_bench_litqa": {"display_name": "文献问答", "description": "实验室文献问答"},
    "lab_bench_suppqa": {"display_name": "补充材料问答", "description": "实验室补充材料问答"},
    "lab_bench_figqa": {"display_name": "图表问答", "description": "实验室图表问答"},
    "lab_bench_tableqa": {"display_name": "表格问答", "description": "实验室表格问答"},
    "lab_bench_dbqa": {"display_name": "数据库问答", "description": "实验室数据库问答"},
    "lab_bench_protocolqa": {"display_name": "实验方案问答", "description": "实验方案问答"},
    "lab_bench_seqqa": {"display_name": "序列问答", "description": "基因/蛋白序列问答"},
    "lab_bench_cloning_scenarios": {"display_name": "克隆场景", "description": "分子克隆场景评估"},
    # --- chembench ---
    "chembench": {"display_name": "化学知识", "description": "化学领域知识评估"},
    # --- healthbench ---
    "healthbench": {"display_name": "医疗健康", "description": "医疗健康知识评估"},
    "healthbench_hard": {"display_name": "医疗健康（困难）", "description": "高难度医疗健康知识评估"},
    "healthbench_consensus": {"display_name": "医疗共识", "description": "医疗共识判断能力"},
    # --- agentdojo ---
    "agentdojo": {"display_name": "智能体安全", "description": "工具调用场景下的智能体安全"},
    # --- bfcl ---
    "bfcl": {"display_name": "函数调用", "description": "函数调用准确性评估"},
    # --- agentharm ---
    "agentharm": {"display_name": "智能体危害", "description": "智能体执行有害任务的倾向"},
    "agentharm_benign": {"display_name": "智能体良性基线", "description": "智能体良性任务基准测试"},
    # --- open_agent_safety ---
    "open_agent_safety": {"display_name": "开放智能体安全", "description": "开放式智能体长链调用安全"},
    # --- saferag ---
    "saferag_sn": {"display_name": "RAG 安全噪声", "description": "检索增强生成安全噪声检测"},
    "saferag_icc": {"display_name": "RAG 上下文冲突", "description": "检索增强生成上下文冲突检测"},
    "saferag_sa": {"display_name": "RAG 安全攻击", "description": "检索增强生成安全攻击检测"},
    "saferag_wdos": {"display_name": "RAG 拒绝服务", "description": "检索增强生成拒绝服务检测"},
    # --- clash_eval ---
    "clash_eval": {"display_name": "知识冲突", "description": "矛盾信息推断能力评估"},
    # --- mm_safety_bench ---
    "mm_safety_bench_illegal_activity": {"display_name": "多模态非法活动", "description": "多模态非法活动内容防御"},
    # --- cyberseceval_3 ---
    "cyse3_visual_prompt_injection": {"display_name": "视觉提示词注入", "description": "视觉通道提示词注入攻击防御"},
    # --- raccoon ---
    "raccoon": {"display_name": "提示词提取防护", "description": "抵抗系统提示词泄露攻击的能力"},
    # --- mssbench ---
    "mssbench_chat_if": {"display_name": "对话情境（指令遵循）", "description": "对话场景指令遵循安全"},
    "mssbench_chat_qc": {"display_name": "对话情境（问题澄清）", "description": "对话场景问题澄清安全"},
    "mssbench_chat_ic": {"display_name": "对话情境（图像理解）", "description": "对话场景图像理解安全"},
    "mssbench_chat_ic_cap": {"display_name": "对话情境（图像描述）", "description": "对话场景图像描述安全"},
    "mssbench_embodied_if": {"display_name": "具身情境（指令遵循）", "description": "具身场景指令遵循安全"},
    "mssbench_embodied_qc": {"display_name": "具身情境（问题澄清）", "description": "具身场景问题澄清安全"},
    "mssbench_embodied_ic": {"display_name": "具身情境（图像理解）", "description": "具身场景图像理解安全"},
    "mssbench_embodied_ic_cap": {"display_name": "具身情境（图像描述）", "description": "具身场景图像描述安全"},
    # --- osworld ---
    "osworld": {"display_name": "操作系统交互", "description": "操作系统交互安全评估"},
    # --- mathvista ---
    "mathvista": {"display_name": "数学视觉推理", "description": "数学视觉推理能力"},
    # --- mmmu ---
    "mmmu_multiple_choice": {"display_name": "多模态选择题", "description": "多学科多模态选择题"},
    "mmmu_open": {"display_name": "多模态开放题", "description": "多学科多模态开放题"},
    # --- mmiu ---
    "mmiu": {"display_name": "多图像理解", "description": "多图像内容理解能力"},
    # --- docvqa ---
    "docvqa": {"display_name": "文档视觉问答", "description": "文档图像理解与问答"},
    # --- safeagentbench ---
    "safeagentbench": {"display_name": "任务规划安全", "description": "复杂任务规划安全评估"},
    "safeagentbench_react": {"display_name": "任务规划（ReAct）", "description": "ReAct 模式任务规划安全"},
    "safeagentbench_visual": {"display_name": "任务规划（视觉）", "description": "视觉辅助任务规划安全"},
    # --- gaia ---
    "gaia": {"display_name": "通用助手评测", "description": "通用 AI 助手任务评估"},
    # --- mind2web ---
    "mind2web": {"display_name": "网页交互规划", "description": "网页交互任务规划评估"},
    # --- mind2web_sc ---
    "mind2web_sc": {"display_name": "网页交互安全约束", "description": "带安全约束的网页交互规划"},
    # --- assistant_bench ---
    "assistant_bench": {"display_name": "助手任务完成", "description": "AI 助手任务完成评估"},
    # --- psysafe ---
    "psysafe": {"display_name": "多智能体心理安全", "description": "多智能体协作心理安全评估"},
    # --- personalized_safety ---
    "personalized_safety": {"display_name": "个性化安全", "description": "高风险个性化场景安全响应"},
    "personalized_safety_context_free": {"display_name": "个性化安全（无背景）", "description": "模型仅看到用户问题，评估基线安全响应能力"},
    "personalized_safety_context_rich": {"display_name": "个性化安全（有背景）", "description": "模型看到用户背景和问题，评估个性化安全响应能力"},
    # --- personality ---
    "personality_BFI": {"display_name": "大五人格评测", "description": "大五人格量表评估"},
    "personality_TRAIT": {"display_name": "人格特质评测", "description": "人格特质量表评估"},
    # --- sycophancy ---
    "sycophancy": {"display_name": "谄媚行为", "description": "过度迎合用户倾向评估"},
    # --- overthink ---
    "overthink": {"display_name": "推理开销攻击防护", "description": "抵抗推理 token 耗尽攻击的能力"},
    # --- truthfulqa ---
    "truthfulqa": {"display_name": "真实性问答", "description": "模型回答真实性评估"},
    # --- gdpval ---
    "gdpval": {"display_name": "GDP 验证", "description": "业务数据验证准确性"},
    # --- asb ---
    "asb": {"display_name": "智能体安全基准", "description": "长期运行智能体安全评估"},
    # --- gdm_self_reasoning ---
    "gdm_approved_directories": {"display_name": "目录权限自推理", "description": "目录权限场景的自我推理"},
    "gdm_calculator_improvement": {"display_name": "计算器改进自推理", "description": "计算器改进场景的自我推理"},
    "gdm_context_length_mod_instrumental_only": {"display_name": "上下文长度（工具）", "description": "上下文长度修改（工具性）"},
    "gdm_context_length_mod_irreversibility_only": {"display_name": "上下文长度（不可逆）", "description": "上下文长度修改（不可逆性）"},
    "gdm_database_tool": {"display_name": "数据库工具自推理", "description": "数据库工具场景的自我推理"},
    "gdm_latency_calculator": {"display_name": "延迟计算自推理", "description": "延迟计算场景的自我推理"},
    "gdm_max_messages_calculator": {"display_name": "消息上限自推理", "description": "消息上限场景的自我推理"},
    "gdm_max_tokens": {"display_name": "Token 上限自推理", "description": "Token 上限场景的自我推理"},
    "gdm_oversight_frequency": {"display_name": "监督频率自推理", "description": "监督频率场景的自我推理"},
    "gdm_read_logs": {"display_name": "日志读取自推理", "description": "日志读取场景的自我推理"},
    "gdm_turn_off_filters": {"display_name": "过滤器关闭自推理", "description": "过滤器关闭场景的自我推理"},
    # --- agentic_misalignment ---
    "agentic_misalignment": {"display_name": "智能体对齐偏差", "description": "智能体规避监督和隐瞒行为"},
    # --- gdm_stealth ---
    "gdm_oversight_pattern": {"display_name": "监督模式规避", "description": "监督模式的规避行为"},
    "gdm_classifier_evasion": {"display_name": "分类器规避", "description": "安全分类器的规避行为"},
    "gdm_cover_your_tracks": {"display_name": "痕迹清除", "description": "操作痕迹的清除行为"},
    "gdm_strategic_rule_breaking": {"display_name": "策略性违规", "description": "有策略的规则违反行为"},
    # --- survive_at_all_costs ---
    "survive_at_all_costs": {"display_name": "极端自保", "description": "极端情境下的失控自保行为"},
    # --- browse_comp ---
    "browse_comp": {"display_name": "浏览理解能力", "description": "浏览代理回答网络问题的准确性"},
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
