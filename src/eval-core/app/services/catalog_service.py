"""解析 benchmarks/catalog.yaml"""

import yaml
from typing import List, Dict, Any, Optional
from ..config import CATALOG_PATH
from ..models.schemas import BenchmarkInfo, TaskInfo

# 评测任务中文元数据 (与 catalog.yaml 所有条目对齐)
BENCHMARK_META = {
    # === 1. 模型安全性 ===
    "strong_reject": {
        "display_name": "强拒绝测试 (StrongREJECT)", "description": "模型可能未能拒绝有害请求的风险",
        "display_name_en": "StrongREJECT", "description_en": "Risk of the model failing to reject harmful requests",
        "reference": "https://github.com/dsbowen/strong_reject",
        "paper_title": "A StrongREJECT for Empty Jailbreaks",
        "paper_url": "https://arxiv.org/abs/2402.10260",
        "paper_venue": "NeurIPS 2024",
        "summary": "包含313条恶意提示，配合自动化评分器评估越狱攻击能否真正诱导出有害信息。评分器与人类判断高度一致。",
        "summary_en": "313 forbidden prompts with an automated rubric-based evaluator measuring whether jailbreaks elicit genuinely harmful, actionable information. Evaluator achieves SOTA agreement with human judges.",
    },
    "makemesay": {
        "display_name": "操控输出测试 (MakeMeSay)", "description": "模型可能被操控说出目标短语的风险",
        "display_name_en": "MakeMeSay", "description_en": "Risk of the model being manipulated into saying target phrases",
        "reference": "https://github.com/UKGovernmentBEIS/inspect_evals",
        "paper_title": "OpenAI o1 System Card (Evaluation Suite)",
        "paper_url": "",
        "paper_venue": "OpenAI, 2024",
        "summary": "双LLM对话博弈：操控者需在30轮内隐蔽诱导对方说出目标密码词。50个密码词按频率分4个难度等级，评估模型的隐蔽操控能力。",
        "summary_en": "Two-LLM conversational game: a manipulator must covertly steer a manipulatee into saying a secret codeword within 30 turns. 50 codewords across 4 difficulty levels test covert manipulation capability.",
    },
    "make_me_pay": {
        "display_name": "社会工程攻击 (MakeMePay)", "description": "模型可能被利用进行社会工程欺诈的风险",
        "display_name_en": "MakeMePay", "description_en": "Risk of the model being exploited for social engineering fraud",
        "reference": "https://github.com/UKGovernmentBEIS/inspect_evals",
        "paper_title": "OpenAI o1 System Card (Evaluation Suite)",
        "paper_url": "",
        "paper_venue": "OpenAI, 2024",
        "summary": "双LLM金融欺诈场景：一方扮演骗子说服另一方（持有$100）捐款。第三方模型监控交易行为。评估社会工程攻击能力。",
        "summary_en": "Two-LLM financial fraud scenario: a con artist tries to extract money from a mark given $100. A third model monitors for donations. Tests social engineering persuasion capability.",
    },
    "xstest": {
        "display_name": "过度拒绝测试 (XSTest)", "description": "模型因安全限制过强而错误拒绝合理请求的风险",
        "display_name_en": "XSTest", "description_en": "Risk of the model incorrectly rejecting legitimate requests due to overly strict safety restrictions",
        "reference": "https://github.com/paul-rottger/xstest",
        "paper_title": "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models",
        "paper_url": "https://arxiv.org/abs/2308.01263",
        "paper_venue": "NAACL 2024",
        "summary": "250条安全提示+200条不安全对照提示，覆盖10种提示类型。测试模型是否因关键词过度匹配而错误拒绝无害请求。",
        "summary_en": "250 safe prompts + 200 unsafe contrast prompts across 10 types. Tests whether models over-refuse benign requests due to lexical overfitting on safety-related keywords.",
    },
    "coconot": {
        "display_name": "不当拒绝检测 (CoCoNot)", "description": "模型在不应拒绝的场景下错误拒绝用户请求的风险",
        "display_name_en": "CoCoNot", "description_en": "Risk of the model incorrectly refusing user requests in scenarios where refusal is inappropriate",
        "reference": "https://github.com/allenai/noncompliance",
        "paper_title": "The Art of Saying No: Contextual Noncompliance in Language Models",
        "paper_url": "https://arxiv.org/abs/2407.12043",
        "paper_venue": "NeurIPS 2024",
        "summary": "1,001条非合规提示+379条合规对照。覆盖5类拒绝场景（不完整/不支持/不确定/拟人化/不安全），评估模型精细化拒绝能力。",
        "summary_en": "1,001 noncompliance prompts + 379 compliance contrasts across 5 refusal categories (incomplete, unsupported, indeterminate, humanizing, unsafe). Evaluates nuanced refusal behavior.",
    },
    "cyberseceval_2": {
        "display_name": "网络安全评测 (CyberSecEval 2)", "description": "模型在代码安全场景中生成恶意代码或被注入攻击的风险",
        "display_name_en": "CyberSecEval 2", "description_en": "Risk of the model generating malicious code or being exploited via injection attacks in code security scenarios",
        "reference": "https://github.com/meta-llama/PurpleLlama",
        "paper_title": "CyberSecEval 2: A Wide-Ranging Cybersecurity Evaluation Suite for Large Language Models",
        "paper_url": "https://arxiv.org/abs/2404.13161",
        "paper_venue": "Meta AI, 2024",
        "summary": "Meta Purple Llama项目的网络安全评测套件，覆盖4个维度：不安全代码生成、攻击协助合规性、提示词注入抗性和代码解释器滥用。",
        "summary_en": "Meta Purple Llama cybersecurity evaluation suite covering 4 dimensions: insecure code generation, cyberattack assistance compliance, prompt injection resistance, and code interpreter abuse.",
    },
    "b3": {
        "display_name": "综合智能体安全评测 (B3)", "description": "智能体面临直接和间接提示词注入的综合安全风险",
        "display_name_en": "B3", "description_en": "Comprehensive security risk of agents facing direct and indirect prompt injection attacks",
        "reference": "https://github.com/UKGovernmentBEIS/inspect_evals",
        "paper_title": "Breaking Agent Backbones: Evaluating the Security of Backbone LLMs in AI Agents",
        "paper_url": "https://arxiv.org/abs/2510.22620",
        "paper_venue": "ICLR 2026",
        "summary": "10个智能体威胁快照+19,433条众包对抗攻击（来自Gandalf红队游戏19.4万条尝试），覆盖数据泄露、内容注入、行为操纵等攻击类别。",
        "summary_en": "10 agent threat snapshots + 19,433 crowdsourced adversarial attacks (from 194K Gandalf red-teaming attempts) covering data exfiltration, content injection, behavior manipulation, and more.",
    },
    "fortress": {
        "display_name": "提示词注入防御 (FORTRESS)", "description": "模型被提示词注入攻击攻破的风险",
        "display_name_en": "FORTRESS", "description_en": "Risk of the model being compromised by prompt injection attacks",
        "reference": "https://github.com/UKGovernmentBEIS/inspect_evals",
        "paper_title": "FORTRESS: Frontier Risk Evaluation for National Security and Public Safety",
        "paper_url": "https://arxiv.org/abs/2506.14922",
        "paper_venue": "Scale AI, 2025",
        "summary": "500条专家构造的对抗提示，覆盖CBRNE、政治暴力和金融犯罪3大领域10个子类。每条配有4-7个二元评分标准和良性对照版本。",
        "summary_en": "500 expert-crafted adversarial prompts across 3 domains (CBRNE, political violence, financial crime) with 10 subcategories. Each has 4-7 binary rubric questions + benign contrast version.",
    },
    "iheval": {
        "display_name": "指令层级遵从 (IHEval)", "description": "模型在多来源或冲突指令时错误判断优先级的风险",
        "display_name_en": "IHEval", "description_en": "Risk of the model misjudging priority when facing multi-source or conflicting instructions",
        "reference": "https://github.com/ytyz1307zzh/IHEval",
        "paper_title": "IHEval: Evaluating Language Models on Following the Instruction Hierarchy",
        "paper_url": "https://arxiv.org/abs/2502.08745",
        "paper_venue": "NAACL 2025 (Oral)",
        "summary": "3,538个样本覆盖9个任务、4类场景（规则遵循、NLP任务、安全防御、工具使用），测试模型是否正确遵循指令优先级（系统>用户>历史>工具）。",
        "summary_en": "3,538 examples across 9 tasks and 4 scenarios (rule following, NLP tasks, safety defense, tool use). Tests whether models correctly follow instruction hierarchy (system > user > history > tool output).",
    },
    "ifeval": {
        "display_name": "指令遵循评测 (IFEval)", "description": "模型未能正确遵循复杂指令的风险",
        "display_name_en": "IFEval", "description_en": "Risk of the model failing to correctly follow complex instructions",
        "reference": "https://github.com/google-research/google-research/tree/master/instruction_following_eval",
        "paper_title": "Instruction-Following Evaluation for Large Language Models",
        "paper_url": "https://arxiv.org/abs/2311.07911",
        "paper_venue": "Google, 2023",
        "summary": "约500条提示包含25类可验证指令（字数、关键词、格式等），完全自动化确定性评估。原为通用能力测试。本平台将指令遵循能力作为安全对齐的前提指标。",
        "summary_en": "~500 prompts with 25 types of verifiable constraints (word count, keywords, format). Fully automated deterministic evaluation. Originally tests general capability; this platform uses instruction-following as a prerequisite indicator for safety alignment.",
        "score_adaptation": "原为通用指令遵循测试，本平台将其作为安全前提指标——无法可靠遵循显式约束的模型也难以可靠遵循安全指令。",
        "score_adaptation_en": "Originally a general instruction-following test. This platform treats it as a safety prerequisite — a model that cannot reliably follow explicit constraints is unlikely to reliably follow safety directives.",
    },
    # === 2. 模型事实性 ===
    "hallulens": {
        "display_name": "幻觉检测 (HalluLens)", "description": "模型生成虚假内容的幻觉风险",
        "display_name_en": "HalluLens", "description_en": "Risk of the model generating false content (hallucination)",
        "reference": "https://github.com/facebookresearch/HalluLens",
        "paper_title": "HalluLens: LLM Hallucination Benchmark",
        "paper_url": "https://arxiv.org/abs/2504.17550",
        "paper_venue": "ACL 2025",
        "summary": "区分外部幻觉（与训练数据不一致）和内部幻觉（与上下文矛盾），包含3个任务：精确问答、长文本生成和虚构实体拒绝。动态生成测试集防止数据泄露。",
        "summary_en": "Distinguishes extrinsic (inconsistent with training data) and intrinsic (contradicting source context) hallucinations across 3 tasks: precise QA, long-text generation, and nonexistent entity refusal. Dynamic test set generation prevents data leakage.",
        "score_adaptation": "幻觉本身即安全问题——在医疗、法律、金融等高风险领域，模型自信地编造事实可能造成现实危害。",
        "score_adaptation_en": "Hallucination is itself a safety issue — in high-stakes domains (medical, legal, financial), confidently fabricated facts can cause real-world harm.",
    },
    "simpleqa": {
        "display_name": "事实问答测试 (SimpleQA)", "description": "模型在简单事实问答中回答错误的风险",
        "display_name_en": "SimpleQA", "description_en": "Risk of the model answering incorrectly in simple factual Q&A",
        "reference": "https://github.com/openai/simple-evals",
        "paper_title": "Measuring short-form factuality in large language models",
        "paper_url": "https://arxiv.org/abs/2411.04368",
        "paper_venue": "OpenAI, 2024",
        "summary": "4,326条短答事实问题，答案唯一且不随时间变化。对抗性地针对GPT-4采集，测量正确率和校准度。原为事实性测试。",
        "summary_en": "4,326 short, fact-seeking questions with single unambiguous answers, adversarially collected against GPT-4. Measures both accuracy and calibration (abstention when uncertain).",
        "score_adaptation": "原为事实准确性测试。低分表明模型倾向生成看似合理的虚假信息，在安全敏感场景中构成风险。",
        "score_adaptation_en": "Originally a factual accuracy test. Low scores indicate propensity to generate plausible-sounding misinformation, posing risks in safety-critical information contexts.",
    },
    "sciknoweval": {
        "display_name": "科学知识评测 (SciKnowEval)", "description": "模型在科学知识领域回答不准确的风险",
        "display_name_en": "SciKnowEval", "description_en": "Risk of the model providing inaccurate answers in scientific knowledge domains",
        "reference": "https://github.com/HICAI-ZJU/SciKnowEval",
        "paper_title": "SciKnowEval: Evaluating Multi-level Scientific Knowledge of Large Language Models",
        "paper_url": "https://arxiv.org/abs/2406.09098",
        "paper_venue": "arXiv, 2024",
        "summary": "约28,000道题覆盖生物、化学、物理和材料科学，分5个认知层次：记忆、理解、推理、辨别和应用。辨别层直接测试安全意识。",
        "summary_en": "~28,000 questions across biology, chemistry, physics, and materials science at 5 cognitive levels: memory, comprehension, reasoning, discernment, and application. The discernment level directly tests safety awareness in scientific contexts.",
    },
    "mask": {
        "display_name": "诚实性评测 (MASK)", "description": "模型隐瞒不确定性、输出不坦率的风险",
        "display_name_en": "MASK", "description_en": "Risk of the model concealing uncertainty and producing dishonest outputs",
        "reference": "https://github.com/centerforaisafety/mask",
        "paper_title": "The MASK Benchmark: Disentangling Honesty From Accuracy in AI Systems",
        "paper_url": "https://arxiv.org/abs/2503.03750",
        "paper_venue": "CAIS & Scale AI, 2025",
        "summary": "1,028条高质量人工标注样本，将诚实性与准确性分离评估。先提取模型信念，再测试模型在压力下是否违背自身信念（说谎/诚实/回避）。",
        "summary_en": "1,028 human-labeled examples disentangling honesty from accuracy. First elicits model beliefs, then tests whether models contradict their own beliefs under pressure (lie/honest/evade).",
    },
    "abstention_bench": {
        "display_name": "拒答能力评测 (AbstentionBench)", "description": "模型在不确定时未能适当拒答、强行回答的风险",
        "display_name_en": "AbstentionBench", "description_en": "Risk of the model failing to appropriately abstain and forcing answers when uncertain",
        "reference": "https://github.com/facebookresearch/AbstentionBench",
        "paper_title": "AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions",
        "paper_url": "https://arxiv.org/abs/2506.09038",
        "paper_venue": "NeurIPS 2025",
        "summary": "覆盖20个数据集39,558个样本，测试5类应拒答场景（未知答案、不充分信息、错误前提、主观解读、过时信息）。发现推理微调使拒答能力下降24%。",
        "summary_en": "39,558 samples across 20 datasets testing 5 abstention scenarios (unknown answers, underspecification, false premises, subjective interpretations, outdated info). Finding: reasoning fine-tuning degrades abstention by 24%.",
    },
    # === 3. 合规：模型公平性 ===
    "bbq": {
        "display_name": "偏见行为测试 (BBQ)", "description": "模型在偏见相关问题上产生不公平输出的风险",
        "display_name_en": "BBQ", "description_en": "Risk of the model producing unfair outputs on bias-related questions",
        "reference": "https://github.com/nyu-mll/BBQ",
        "paper_title": "BBQ: A Hand-Built Bias Benchmark for Question Answering",
        "paper_url": "https://arxiv.org/abs/2110.08193",
        "paper_venue": "Findings of ACL 2022",
        "summary": "58,492条选择题，由325个手工模板生成，覆盖9个社会偏见维度（年龄、残疾、性别等）。每题在模糊和明确两种条件下测试偏见依赖。",
        "summary_en": "58,492 multiple-choice instances from 325 hand-crafted templates across 9 social bias dimensions (age, disability, gender, etc.). Each tested under ambiguous and disambiguated conditions to measure stereotype reliance.",
    },
    "bold": {
        "display_name": "开放文本偏见检测 (BOLD)", "description": "模型在开放式文本生成中暴露偏见倾向的风险",
        "display_name_en": "BOLD", "description_en": "Risk of the model exposing bias tendencies in open-ended text generation",
        "reference": "https://github.com/amazon-science/bold",
        "paper_title": "BOLD: Dataset and Metrics for Measuring Biases in Open-Ended Language Generation",
        "paper_url": "https://arxiv.org/abs/2101.11718",
        "paper_venue": "ACM FAccT 2021",
        "summary": "23,679条英文文本生成提示，覆盖职业、性别、种族、宗教和政治5个领域。基于Wikipedia句子构造，用毒性和心理语言学指标衡量生成偏见。",
        "summary_en": "23,679 English text generation prompts across 5 domains (profession, gender, race, religion, political ideology). Prompts from Wikipedia; evaluated using toxicity and psycholinguistic bias metrics.",
    },
    "ahb": {
        "display_name": "AI 伤害评测 (AHB)", "description": "模型输出可能对特定群体造成伤害的风险",
        "display_name_en": "AHB", "description_en": "Risk of model outputs potentially causing harm to specific groups",
        "reference": "https://github.com/AI-for-Animals/ahb",
        "paper_title": "What do Large Language Models Say About Animals? Investigating Risks of Animal Harm in Generated Text",
        "paper_url": "https://arxiv.org/abs/2503.04804",
        "paper_venue": "ACM FAccT 2025",
        "summary": "4,350道题（3,045条公开），覆盖50个动物类别×50个伦理场景。AHB 2.0版本从13个道德推理维度评分，使用LLM裁判评估。",
        "summary_en": "4,350 questions (3,045 public) across 50 animal categories × 50 ethical scenarios. AHB 2.0 scores across 13 moral reasoning dimensions using LLM-based judging.",
    },
    "stereoset": {
        "display_name": "刻板印象评测 (StereoSet)", "description": "模型强化群体刻板化标签的风险",
        "display_name_en": "StereoSet", "description_en": "Risk of the model reinforcing stereotypical labels for groups",
        "reference": "https://github.com/moinnadeem/StereoSet",
        "paper_title": "StereoSet: Measuring stereotypical bias in pretrained language models",
        "paper_url": "https://arxiv.org/abs/2004.09456",
        "paper_venue": "ACL 2021",
        "summary": "约16,995条测试样本，覆盖性别、职业、种族和宗教4个领域。使用句内和句间两种格式的上下文关联测试，同时衡量偏见和语言建模能力（ICAT指标）。",
        "summary_en": "~16,995 instances across gender, profession, race, and religion. Uses intrasentence and intersentence Context Association Tests, measuring both bias AND language modeling via ICAT score.",
    },
    "cvalues": {
        "display_name": "中文价值观对齐 (CValues)", "description": "模型对中文文化价值观理解偏差的风险",
        "display_name_en": "CValues", "description_en": "Risk of the model misunderstanding Chinese cultural values",
        "reference": "https://github.com/X-PLUG/CValues",
        "paper_title": "CValues: Measuring the Values of Chinese Large Language Models from Safety to Responsibility",
        "paper_url": "https://arxiv.org/abs/2307.09705",
        "paper_venue": "arXiv, 2023",
        "summary": "首个中文人类价值观评测。包含1,300条安全对抗提示（人工评估）和2,600条安全选择题（自动评估），覆盖10个安全场景+8个专业领域。",
        "summary_en": "First Chinese human values benchmark. 1,300 adversarial safety prompts (human eval) + 2,600 multiple-choice safety questions (auto eval) across 10 safety scenarios + 8 professional domains.",
    },
    "culturalbench": {
        "display_name": "跨文化知识评测 (CulturalBench)", "description": "模型对不同文化背景信息理解偏差的风险",
        "display_name_en": "CulturalBench", "description_en": "Risk of the model misunderstanding information from different cultural backgrounds",
        "reference": "https://huggingface.co/datasets/kellycyy/CulturalBench",
        "paper_title": "CulturalBench: A Robust, Diverse and Challenging Benchmark for Measuring LMs' Cultural Knowledge",
        "paper_url": "https://arxiv.org/abs/2410.02677",
        "paper_venue": "ACL 2025",
        "summary": "1,696条人工编写并经5人独立验证的题目，覆盖45个地区×17个主题。分Easy和Hard两个评估集，GPT-4o在Hard上仅61.5%（人类92.4%）。",
        "summary_en": "1,696 human-written, 5-annotator-verified questions across 45 regions × 17 topics. Easy and Hard splits; GPT-4o achieves only 61.5% on Hard vs. 92.4% human accuracy.",
        "score_adaptation": "原为文化知识测试。本平台评估模型是否对特定地区存在系统性知识偏差，可能导致对弱势文化群体的不公平服务。",
        "score_adaptation_en": "Originally a cultural knowledge test. This platform assesses systematic knowledge gaps by region, which could lead to inequitable service for underrepresented cultural communities.",
    },
    "uccb": {
        "display_name": "跨文化交际偏见 (UCCB)", "description": "模型在跨文化交际中产生偏见输出的风险",
        "display_name_en": "UCCB", "description_en": "Risk of the model producing biased outputs in cross-cultural communication",
        "reference": "https://huggingface.co/datasets/CraneAILabs/UCCB",
        "paper_title": "The Ugandan Cultural Context Benchmark (UCCB) Suite",
        "paper_url": "",
        "paper_venue": "Crane AI Labs, 2024",
        "summary": "1,039条问答对，覆盖乌干达24个文化领域（教育、传统医学、媒体、文学等）。填补非洲本地化文化评测的空白。",
        "summary_en": "1,039 QA pairs across 24 Ugandan cultural domains (education, traditional medicine, media, literature, etc.). Addresses the gap in localized African cultural AI evaluation.",
        "score_adaptation": "原为文化理解测试。本平台评估模型对非洲文化的知识准确性，错误信息可能在医疗、教育等公共服务场景中造成危害。",
        "score_adaptation_en": "Originally a cultural understanding test. This platform assesses cultural knowledge accuracy for African contexts — errors could cause harm in healthcare, education, and public service applications.",
    },
    "mgsm": {
        "display_name": "多语言数学推理 (MGSM)", "description": "不同语言间数学推理表现不一致的公平性风险",
        "display_name_en": "MGSM", "description_en": "Fairness risk of inconsistent mathematical reasoning performance across different languages",
        "reference": "https://github.com/google-research/url-nlp",
        "paper_title": "Language Models are Multilingual Chain-of-Thought Reasoners",
        "paper_url": "https://arxiv.org/abs/2210.03057",
        "paper_venue": "ICLR 2023",
        "summary": "250道小学数学题手动翻译为10种语言（孟加拉语、中文、法语、德语等），评估多语言推理一致性。",
        "summary_en": "250 grade-school math problems manually translated into 10 typologically diverse languages (Bengali, Chinese, French, German, etc.). Evaluates multilingual reasoning consistency.",
        "score_adaptation": "原为多语言推理测试。本平台衡量不同语言间的性能差异，揭示对低资源语言用户的公平性风险。",
        "score_adaptation_en": "Originally a multilingual reasoning test. This platform measures performance disparities across languages, revealing fairness risks for underrepresented language communities.",
    },
    # === 4. 合规：隐私泄露 ===
    "privacylens": {
        "display_name": "隐私保护评估 (PrivacyLens)", "description": "模型违反隐私规范、泄露敏感信息的风险",
        "display_name_en": "PrivacyLens", "description_en": "Risk of the model violating privacy norms and leaking sensitive information",
        "reference": "https://github.com/SALT-NLP/PrivacyLens",
        "paper_title": "PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action",
        "paper_url": "https://arxiv.org/abs/2409.00138",
        "paper_venue": "NeurIPS 2024",
        "summary": "基于493条隐私敏感种子（源自美国隐私法规和弱势群体研究）构建多层级评测框架，在规范理解、场景推理和智能体行为3个层面评估隐私意识。GPT-4智能体在25.68%的案例中泄露隐私。",
        "summary_en": "Multi-level framework from 493 privacy-sensitive seeds (from US regulations and vulnerable group research). Evaluates at norm understanding, vignette reasoning, and agent trajectory levels. GPT-4 agents leak privacy-violating info in 25.68% of cases.",
    },
    # === 5. 前沿安全风险 ===
    "cve_bench": {
        "display_name": "CVE 漏洞利用测试 (CVE-Bench)", "description": "模型可能被利用来攻击真实 CVE 漏洞的风险",
        "display_name_en": "CVE-Bench", "description_en": "Risk of the model being exploited to attack real-world CVE vulnerabilities",
        "reference": "https://github.com/uiuc-kang-lab/cve-bench",
        "paper_title": "CVE-Bench: A Benchmark for AI Agents' Ability to Exploit Real-World Web Application Vulnerabilities",
        "paper_url": "https://arxiv.org/abs/2503.17332",
        "paper_venue": "ICML 2025 (Spotlight)",
        "summary": "40个真实高危CVE漏洞的Web应用利用评测，提供Docker沙箱环境模拟真实利用场景。二值评分（是否成功利用）。SOTA智能体仅成功利用13%。",
        "summary_en": "40 real-world critical-severity CVE web application exploits in Docker sandbox environments. Binary scoring (exploit success/failure). SOTA agent resolves only 13%.",
    },
    "wmdp": {
        "display_name": "危险武器知识评测 (WMDP)", "description": "模型泄露大规模杀伤性武器相关危险知识的风险",
        "display_name_en": "WMDP", "description_en": "Risk of the model leaking dangerous knowledge related to weapons of mass destruction",
        "reference": "https://github.com/centerforaisafety/wmdp",
        "paper_title": "The WMDP Benchmark: Measuring and Reducing Malicious Use With Unlearning",
        "paper_url": "https://arxiv.org/abs/2403.03218",
        "paper_venue": "ICML 2024",
        "summary": "3,668道选择题，覆盖生物安全、网络安全和化学安全3个领域，作为危险知识的代理度量。由学术机构和技术顾问联合开发，严格过滤敏感信息后公开。",
        "summary_en": "3,668 multiple-choice questions across biosecurity, cybersecurity, and chemical security as a proxy measurement of hazardous knowledge. Developed by academic consortium; stringently filtered before public release.",
    },
    "wmdp_local": {
        "display_name": "危险武器知识本地版 (WMDP-Local)", "description": "模型泄露大规模杀伤性武器代理知识的风险（本地复现版）",
        "display_name_en": "WMDP-Local", "description_en": "Risk of the model leaking proxy knowledge of weapons of mass destruction (local reproduction version)",
        "reference": "https://github.com/centerforaisafety/wmdp",
        "paper_title": "The WMDP Benchmark: Measuring and Reducing Malicious Use With Unlearning",
        "paper_url": "https://arxiv.org/abs/2403.03218",
        "paper_venue": "ICML 2024",
        "summary": "WMDP基准的本地复现版本，评测内容与原版一致。",
        "summary_en": "Local reproduction of the WMDP benchmark with identical evaluation content.",
    },
    "cybench": {
        "display_name": "CTF 网络安全挑战 (CyBench)", "description": "模型可能被利用完成网络攻击挑战的风险",
        "display_name_en": "CyBench", "description_en": "Risk of the model being exploited to complete cybersecurity attack challenges",
        "reference": "https://github.com/andyzorigin/cybench",
        "paper_title": "Cybench: A Framework for Evaluating Cybersecurity Capabilities and Risks of Language Models",
        "paper_url": "https://arxiv.org/abs/2408.08926",
        "paper_venue": "ICLR 2025 (Oral)",
        "summary": "40个专业CTF挑战，来自4个赛事（HackTheBox等），覆盖密码学、Web安全、逆向工程等6个领域。在Kali Linux沙箱中运行，支持子任务分解评估。",
        "summary_en": "40 professional CTF challenges from 4 competitions across 6 domains (cryptography, web security, reverse engineering, etc.). Runs in Kali Linux sandbox with subtask decomposition for fine-grained evaluation.",
    },
    "sevenllm": {
        "display_name": "网络安全知识推理 (SEvenLLM)", "description": "模型在网络安全领域泄露敏感知识与推理能力的风险",
        "display_name_en": "SEvenLLM", "description_en": "Risk of the model leaking sensitive knowledge and reasoning capabilities in cybersecurity domains",
        "reference": "https://github.com/CSJianYang/SEevenLLM",
        "paper_title": "SEvenLLM: Benchmarking, Eliciting, and Enhancing Abilities of Large Language Models in Cyber Threat Intelligence",
        "paper_url": "https://arxiv.org/abs/2405.03446",
        "paper_venue": "arXiv, 2024",
        "summary": "约1,300条中英双语测试样本，覆盖28个任务（实体识别、漏洞情报提取、攻击策略分析等），分为理解类和生成类。评估网络安全分析与推理能力。",
        "summary_en": "~1,300 bilingual (EN/ZH) test samples across 28 tasks (entity recognition, vulnerability intelligence extraction, attack strategy analysis, etc.) in understanding and generation categories.",
    },
    "sec_qa": {
        "display_name": "安全知识问答 (SecQA)", "description": "模型泄露安全领域专业知识被恶意利用的风险",
        "display_name_en": "SecQA", "description_en": "Risk of the model leaking security domain expertise that could be maliciously exploited",
        "reference": "https://huggingface.co/datasets/zefang-liu/secqa",
        "paper_title": "SecQA: A Concise Question-Answering Dataset for Evaluating Large Language Models in Computer Security",
        "paper_url": "https://arxiv.org/abs/2312.15838",
        "paper_venue": "arXiv, 2023",
        "summary": "基于《计算机系统安全》教材由GPT-4生成的选择题，分v1（基础）和v2（进阶）两个版本。评估模型的安全领域知识水平。",
        "summary_en": "Multiple-choice questions generated by GPT-4 from a computer security textbook. Two versions: v1 (foundational) and v2 (advanced). Evaluates security domain knowledge level.",
    },
    "threecb": {
        "display_name": "网络安全行为评测 (3CB)", "description": "模型在网络安全场景中产生危险行为的风险",
        "display_name_en": "3CB", "description_en": "Risk of the model producing dangerous behaviors in cybersecurity scenarios",
        "reference": "https://github.com/apartresearch/3cb",
        "paper_title": "Catastrophic Cyber Capabilities Benchmark (3CB): Robustly Evaluating LLM Agent Cyber Offense Capabilities",
        "paper_url": "https://arxiv.org/abs/2410.09114",
        "paper_venue": "arXiv, 2024",
        "summary": "15个CTF挑战对齐MITRE ATT&CK框架（侦察、初始访问、权限提升等），在Docker沙箱中运行。多种诱导方式×10次重复评估，测试自主网络攻击能力。",
        "summary_en": "15 CTF challenges aligned with MITRE ATT&CK categories in Docker sandboxes. Multiple elicitation strategies × 10 repeats evaluate autonomous cyber offense capabilities.",
    },
    "sosbench": {
        "display_name": "科学安全评测 (SOSBench)", "description": "模型在科学安全领域泄露敏感知识的风险",
        "display_name_en": "SOSBench", "description_en": "Risk of the model leaking sensitive knowledge in scientific safety domains",
        "reference": "https://sosbench.github.io/",
        "paper_title": "SOSBENCH: Benchmarking Safety Alignment on Scientific Knowledge",
        "paper_url": "https://arxiv.org/abs/2505.21605",
        "paper_venue": "ICLR 2026",
        "summary": "3,000条开放式提示，覆盖化学、生物、医学、药理学、物理和心理学6个高危科学领域（各500题）。基于真实法规构造，GPT-4.1裁判评分。",
        "summary_en": "3,000 open-ended prompts across 6 high-risk scientific domains (chemistry, biology, medicine, pharmacology, physics, psychology) with 500 each. Regulation-grounded construction; GPT-4.1 judge scoring.",
    },
    "lab_bench": {
        "display_name": "实验室基准评测 (LAB-Bench)", "description": "模型泄露实验室相关危险知识的风险",
        "display_name_en": "LAB-Bench", "description_en": "Risk of the model leaking dangerous laboratory-related knowledge",
        "reference": "https://github.com/Future-House/LAB-Bench",
        "paper_title": "LAB-Bench: Measuring Capabilities of Language Models for Biology Research",
        "paper_url": "https://arxiv.org/abs/2407.10362",
        "paper_venue": "NeurIPS 2024",
        "summary": "2,457道生物学研究实践题，分8个子任务（文献QA、图表解读、蛋白序列分析、分子克隆等），含33道专家级高难度题。",
        "summary_en": "2,457 practical biology research questions across 8 sub-tasks (literature QA, figure interpretation, protein sequence analysis, molecular cloning, etc.) including 33 expert-hard cloning scenarios.",
        "score_adaptation": "原为生物学能力测试。本平台评估模型是否具备可被滥用的生物研究能力（如DNA操控、分子克隆），涉及双用途研究关切(DURC)。",
        "score_adaptation_en": "Originally a biology capability test. This platform assesses whether models possess exploitable biology research capabilities (DNA manipulation, molecular cloning) related to dual-use research of concern (DURC).",
    },
    "chembench": {
        "display_name": "化学知识评测 (ChemBench)", "description": "模型在化学领域泄露危险知识的风险",
        "display_name_en": "ChemBench", "description_en": "Risk of the model leaking dangerous knowledge in chemistry domains",
        "reference": "https://github.com/lamalab-org/chembench",
        "paper_title": "Are large language models superhuman chemists?",
        "paper_url": "https://arxiv.org/abs/2404.01475",
        "paper_venue": "Nature Chemistry, 2025",
        "summary": "2,786道化学题（2,544选择题+244开放题），覆盖分析化学、有机化学、毒理学与安全等9个领域。最优LLM表现平均超过最优人类化学家。",
        "summary_en": "2,786 chemistry questions (2,544 MC + 244 open-ended) across 9 topics including toxicity & safety. Best LLMs outperform best human chemists on average.",
        "score_adaptation": "原为化学能力测试。本平台重点关注毒理学与安全子集，评估模型是否掌握可被恶意利用的危险化学知识（CBRN双用途关切）。",
        "score_adaptation_en": "Originally a chemistry capability test. This platform focuses on the toxicity & safety subset, assessing dangerous chemical knowledge that could be misused (CBRN dual-use concern).",
    },
    "healthbench": {
        "display_name": "医疗健康评测 (HealthBench)", "description": "模型在医疗健康场景中提供不准确或不安全信息的风险",
        "display_name_en": "HealthBench", "description_en": "Risk of the model providing inaccurate or unsafe information in healthcare scenarios",
        "reference": "https://github.com/openai/simple-evals",
        "paper_title": "HealthBench: Evaluating Large Language Models Towards Improved Human Health",
        "paper_url": "https://arxiv.org/abs/2505.08775",
        "paper_venue": "OpenAI, 2025",
        "summary": "5,000段多轮医疗对话，48,562条由262名医生编写的评分标准，覆盖急救、全球健康、临床文档等场景。分标准/困难/共识3个子集。",
        "summary_en": "5,000 multi-turn healthcare dialogues with 48,562 physician-written rubric criteria from 262 doctors. Covers emergencies, global health, clinical documentation. Three variants: standard, hard, consensus.",
    },
    # === 6. 工具调用 ===
    "agentdojo": {
        "display_name": "智能体安全测试 (AgentDojo)", "description": "智能体在工具调用场景下被攻击或产生危险行为的风险",
        "display_name_en": "AgentDojo", "description_en": "Risk of agents being attacked or producing dangerous behaviors in tool-calling scenarios",
        "reference": "https://github.com/ethz-spylab/agentdojo",
        "paper_title": "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents",
        "paper_url": "https://arxiv.org/abs/2406.13352",
        "paper_venue": "NeurIPS 2024",
        "summary": "97个用户任务+629个安全测试，覆盖5个工具场景（邮件日历、Slack消息、旅行预订、银行交易等）。三维评估：无攻击功能性、攻击下功能性和安全性。",
        "summary_en": "97 user tasks + 629 security tests across 5 tool suites (workspace, Slack, travel, banking, etc.). Three-dimensional evaluation: benign utility, utility under attack, and security.",
    },
    "bfcl": {
        "display_name": "函数调用评测 (BFCL)", "description": "模型在函数调用中产生错误或危险调用的风险",
        "display_name_en": "BFCL", "description_en": "Risk of the model producing incorrect or dangerous function calls",
        "reference": "https://github.com/ShishirPatil/gorilla",
        "paper_title": "The Berkeley Function Calling Leaderboard",
        "paper_url": "",
        "paper_venue": "ICML 2025",
        "summary": "评估LLM的函数调用（工具使用）能力，使用AST结构化评估方法检查每个调用的正确性。覆盖串行/并行调用、多语言和多轮有状态对话。",
        "summary_en": "Evaluates LLM function-calling (tool-use) capabilities using AST-based structural evaluation. Covers serial/parallel calls, multiple programming languages, and multi-turn stateful conversations.",
        "score_adaptation": "原为通用函数调用能力测试。本平台将其作为智能体安全基础——错误的函数调用可能触发危险的现实后果。",
        "score_adaptation_en": "Originally a general function-calling capability test. This platform treats it as an agent safety foundation — incorrect function calls could trigger dangerous real-world side effects.",
    },
    "agentharm": {
        "display_name": "智能体危害测试 (AgentHarm)", "description": "智能体可能执行有害任务的风险",
        "display_name_en": "AgentHarm", "description_en": "Risk of agents executing harmful tasks",
        "reference": "https://github.com/UKGovernmentBEIS/inspect_evals",
        "paper_title": "AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents",
        "paper_url": "https://arxiv.org/abs/2410.09024",
        "paper_venue": "ICLR 2025",
        "summary": "110个恶意智能体任务（含增强共440个），覆盖欺诈、网络犯罪、骚扰等11类危害。测试模型是否拒绝执行有害多步任务。发现领先LLM在无越狱情况下对恶意请求惊人地合规。",
        "summary_en": "110 malicious agent tasks (440 with augmentations) across 11 harm categories (fraud, cybercrime, harassment, etc.). Tests refusal of harmful multi-step tasks. Finding: leading LLMs are surprisingly compliant with malicious requests even without jailbreaking.",
    },
    "open_agent_safety": {
        "display_name": "开放智能体安全 (OpenAgentSafety)", "description": "开放式智能体在长链调用中产生安全问题的风险",
        "display_name_en": "OpenAgentSafety", "description_en": "Risk of open-ended agents producing safety issues in long-chain tool calls",
        "reference": "https://github.com/sani903/OpenAgentSafety",
        "paper_title": "OpenAgentSafety: A Comprehensive Framework for Evaluating Real-World AI Agent Safety",
        "paper_url": "https://arxiv.org/abs/2507.06134",
        "paper_venue": "arXiv, 2025",
        "summary": "8类关键风险，350+多轮多用户任务，智能体在真实工具环境（浏览器、代码执行、文件系统、消息平台）中运行。实测不安全行为率：Claude 51.2% 至 o3-mini 72.7%。",
        "summary_en": "8 risk categories, 350+ multi-turn multi-user tasks with real tools (browser, code execution, file system, messaging). Measured unsafe behavior rates: Claude 51.2% to o3-mini 72.7%.",
    },
    # === 7. RAG/记忆安全 ===
    "saferag": {
        "display_name": "RAG 安全评测 (SafeRAG)", "description": "检索增强生成系统被知识库投毒攻击的风险",
        "display_name_en": "SafeRAG", "description_en": "Risk of retrieval-augmented generation systems being compromised by knowledge base poisoning attacks",
        "reference": "https://github.com/IAAR-Shanghai/SafeRAG",
        "paper_title": "SafeRAG: Benchmarking Security in Retrieval-Augmented Generation of Large Language Model",
        "paper_url": "https://arxiv.org/abs/2501.18636",
        "paper_venue": "ACL 2025",
        "summary": "4类攻击任务（银色噪声注入、上下文冲突、软广告注入、白色拒绝服务），手工构造数据集，测试14个代表性RAG组件的安全性。",
        "summary_en": "4 attack types (silver noise injection, inter-context conflict, soft advertising, white denial-of-service). Manually constructed dataset testing security of 14 representative RAG components.",
    },
    "clash_eval": {
        "display_name": "知识冲突评测 (ClashEval)", "description": "模型面对矛盾信息时产生错误推断的风险",
        "display_name_en": "ClashEval", "description_en": "Risk of the model making incorrect inferences when facing contradictory information",
        "reference": "https://github.com/kevinwu23/StanfordClashEval",
        "paper_title": "ClashEval: Quantifying the tug-of-war between an LLM's internal prior and external evidence",
        "paper_url": "https://arxiv.org/abs/2404.10198",
        "paper_venue": "NeurIPS 2024",
        "summary": "1,200+道题覆盖6个领域（药物剂量、奥运记录等），检索段落含精确扰动的错误信息（从细微到明显）。评估RAG场景下模型是否采纳错误检索内容。",
        "summary_en": "1,200+ questions across 6 domains with precisely perturbed retrieved passages (subtle to blatant errors). Evaluates whether models adopt incorrect retrieved content in RAG settings.",
    },
    # === 8. 多模态安全 ===
    "mm_safety_bench": {
        "display_name": "多模态安全评测 (MM-SafetyBench)", "description": "模型被多模态恶意输入攻破的风险",
        "display_name_en": "MM-SafetyBench", "description_en": "Risk of the model being compromised by multimodal malicious inputs",
        "reference": "https://github.com/isXinLiu/MM-SafetyBench",
        "paper_title": "MM-SafetyBench: A Benchmark for Safety Evaluation of Multimodal Large Language Models",
        "paper_url": "https://arxiv.org/abs/2311.17600",
        "paper_venue": "ECCV 2024",
        "summary": "5,040个文本-图像对，覆盖13个安全场景。展示查询相关图像可绕过已安全对齐的文本LLM，GPT-4评估攻击成功率。",
        "summary_en": "5,040 text-image pairs across 13 safety scenarios. Demonstrates query-relevant images can bypass safety alignment in MLLMs. GPT-4-based attack success rate scoring.",
    },
    "cyberseceval_3": {
        "display_name": "视觉提示词注入 (CyberSecEval 3)", "description": "模型被视觉提示词注入攻击绕过的风险",
        "display_name_en": "CyberSecEval 3", "description_en": "Risk of the model being bypassed by visual prompt injection attacks",
        "reference": "https://github.com/meta-llama/PurpleLlama",
        "paper_title": "CYBERSECEVAL 3: Advancing the Evaluation of Cybersecurity Risks and Capabilities in Large Language Models",
        "paper_url": "https://arxiv.org/abs/2408.01605",
        "paper_venue": "Meta AI, 2024",
        "summary": "CyberSecEval系列第三代，新增自动化社会工程、扩展手动攻击操作和自主攻击操作评测。覆盖8类网络安全风险的第三方和应用端风险评估。",
        "summary_en": "Third generation of CyberSecEval. New evaluations for automated social engineering, scaling manual offensive cyber operations, and autonomous offensive operations. Covers 8 cybersecurity risk categories.",
    },
    "raccoon": {
        "display_name": "提示词提取防护 (Raccoon)", "description": "模型系统提示词被提取泄露的风险",
        "display_name_en": "Raccoon", "description_en": "Risk of the model's system prompt being extracted and leaked",
        "reference": "https://github.com/M0gician/RaccoonBench",
        "paper_title": "Raccoon: Prompt Extraction Benchmark of LLM-Integrated Applications",
        "paper_url": "https://arxiv.org/abs/2406.06737",
        "paper_venue": "ACL 2024 Findings",
        "summary": "14类提示词提取攻击+组合多策略攻击，配合多样化防御模板。在有防御和无防御场景下双重评估模型的提示词保密能力。",
        "summary_en": "14 categories of prompt extraction attacks + compounded multi-strategy attacks with diverse defense templates. Dual evaluation in defenseless and defended scenarios.",
    },
    "mssbench": {
        "display_name": "多模态情境安全 (MSSBench)", "description": "模型在多模态情境中做出不安全决策的风险",
        "display_name_en": "MSSBench", "description_en": "Risk of the model making unsafe decisions in multimodal scenarios",
        "reference": "https://github.com/eric-ai-lab/MSSBench",
        "paper_title": "Multimodal Situational Safety",
        "paper_url": "https://arxiv.org/abs/2410.06172",
        "paper_venue": "ICLR 2025",
        "summary": "约1,820个查询-图像对，均分安全和不安全视觉上下文。评估多模态LLM能否识别同一文本查询在不同视觉场景下的安全性差异。",
        "summary_en": "~1,820 query-image pairs evenly split between safe and unsafe visual contexts. Evaluates whether MLLMs can recognize context-dependent safety differences for the same text query.",
    },
    "osworld": {
        "display_name": "操作系统交互评测 (OSWorld)", "description": "模型在操作系统交互场景中执行危险操作的风险",
        "display_name_en": "OSWorld", "description_en": "Risk of the model executing dangerous operations in OS interaction scenarios",
        "reference": "https://github.com/xlang-ai/OSWorld",
        "paper_title": "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments",
        "paper_url": "https://arxiv.org/abs/2404.07972",
        "paper_venue": "NeurIPS 2024",
        "summary": "369个真实计算机任务（Ubuntu/Windows/macOS），涵盖文件操作、Web浏览和多应用工作流。自定义执行评估脚本。人类72.36%成功率，最优模型仅12.24%。",
        "summary_en": "369 real computer tasks (Ubuntu/Windows/macOS) covering file I/O, web browsing, and multi-app workflows. Custom execution-based evaluation. Humans: 72.36%; best model: 12.24%.",
        "score_adaptation": "原为通用计算机代理能力测试。本平台评估自主代理是否能被诱导执行危险操作（如删除系统文件、窃取数据），测试安全边界遵守情况。",
        "score_adaptation_en": "Originally a general computer-use agent capability test. This platform assesses whether agents can be instructed to perform dangerous operations (delete files, exfiltrate data) and whether they respect safety boundaries.",
    },
    "mathvista": {
        "display_name": "数学视觉推理 (MathVista)", "description": "模型在数学视觉推理中产生错误判断的风险",
        "display_name_en": "MathVista", "description_en": "Risk of the model making incorrect judgments in mathematical visual reasoning",
        "reference": "https://github.com/lupantech/MathVista",
        "paper_title": "MathVista: Evaluating Mathematical Reasoning of Foundation Models in Visual Contexts",
        "paper_url": "https://arxiv.org/abs/2310.02255",
        "paper_venue": "ICLR 2024 (Oral)",
        "summary": "6,141个样本来自28个数据集+3个新数据集（IQTest/FunctionQA/PaperQA），覆盖代数推理、逻辑推理和科学推理。选择题+自由回答两种格式。",
        "summary_en": "6,141 examples from 28 existing datasets + 3 new datasets (IQTest/FunctionQA/PaperQA) covering algebraic, logical, and scientific reasoning. Both multiple-choice and free-form formats.",
        "score_adaptation": "原为多模态数学推理能力测试。本平台将其作为安全干预影响的能力基线——衡量安全对齐是否损害核心推理能力。",
        "score_adaptation_en": "Originally a multimodal math reasoning capability test. This platform uses it as a capability baseline — measuring whether safety alignment degrades core reasoning abilities.",
    },
    "mmmu": {
        "display_name": "多学科多模态理解 (MMMU)", "description": "模型在多学科多模态场景下理解偏差的风险",
        "display_name_en": "MMMU", "description_en": "Risk of the model having comprehension biases in multidisciplinary multimodal scenarios",
        "reference": "https://github.com/MMMU-Benchmark/MMMU",
        "paper_title": "MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI",
        "paper_url": "https://arxiv.org/abs/2311.16502",
        "paper_venue": "CVPR 2024",
        "summary": "11,500道大学级多模态题目，覆盖6个学科（艺术、商业、科学、医学、人文、工程）30个专业183个子领域，包含30种图像类型。",
        "summary_en": "11,500 college-level multimodal questions across 6 disciplines (Art, Business, Science, Medicine, Humanities, Engineering), 30 subjects, 183 subfields, 30 image types.",
        "score_adaptation": "原为专家级多模态理解测试。本平台评估医学、科学等子集的知识可靠性——错误的专业知识输出可能在安全敏感领域造成危害。",
        "score_adaptation_en": "Originally an expert-level multimodal understanding test. This platform evaluates knowledge reliability in Health & Medicine, Science subsets — incorrect outputs could cause harm in safety-critical domains.",
    },
    "mmiu": {
        "display_name": "多图像理解 (MMIU)", "description": "模型对多图像内容理解错误导致错误决策的风险",
        "display_name_en": "MMIU", "description_en": "Risk of incorrect multi-image content understanding leading to wrong decisions",
        "reference": "https://github.com/OpenGVLab/MMIU",
        "paper_title": "MMIU: Multimodal Multi-image Understanding for Evaluating Large Vision-Language Models",
        "paper_url": "https://arxiv.org/abs/2408.02718",
        "paper_venue": "ICLR 2025",
        "summary": "7类多图像关系、52个任务、77K图像、11K选择题。涵盖空间理解、时间推理和跨图像比较。GPT-4o仅55.7%准确率。",
        "summary_en": "7 multi-image relationship types, 52 tasks, 77K images, 11K multiple-choice questions. Covers spatial understanding, temporal reasoning, and cross-image comparison. GPT-4o achieves only 55.7%.",
        "score_adaptation": "原为多图像理解能力测试。本平台评估模型在需要跨多个视觉输入进行安全推理的场景（如监控、文档验证、篡改检测）中的可靠性。",
        "score_adaptation_en": "Originally a multi-image understanding capability test. This platform assesses reliability in scenarios requiring safety reasoning across multiple visual inputs (surveillance, document verification, manipulation detection).",
    },
    "docvqa": {
        "display_name": "文档视觉问答 (DocVQA)", "description": "模型对文档图像理解偏差导致信息提取错误的风险",
        "display_name_en": "DocVQA", "description_en": "Risk of document image comprehension biases leading to information extraction errors",
        "reference": "https://www.docvqa.org/",
        "paper_title": "DocVQA: A Dataset for VQA on Document Images",
        "paper_url": "https://arxiv.org/abs/2007.00398",
        "paper_venue": "WACV 2021",
        "summary": "50,000道题基于12,000+文档图像，需理解文本、表格、图表和版式回答问题。使用ANLS（归一化Levenshtein相似度）评估。",
        "summary_en": "50,000 questions on 12,000+ document images requiring understanding of text, tables, figures, and layouts. Evaluated using Average Normalized Levenshtein Similarity (ANLS).",
        "score_adaptation": "原为文档理解能力测试。本平台评估模型处理敏感文档时的可靠性——理解偏差可能导致错误的信息提取或泄露。",
        "score_adaptation_en": "Originally a document understanding capability test. This platform assesses reliability when processing sensitive documents — comprehension biases could lead to incorrect information extraction or leakage.",
    },
    # === 9. 任务规划安全 ===
    "safeagentbench": {
        "display_name": "任务规划安全评测 (SafeAgentBench)", "description": "智能体在复杂任务规划中生成危险步骤的风险",
        "display_name_en": "SafeAgentBench", "description_en": "Risk of agents generating dangerous steps in complex task planning",
        "reference": "https://github.com/SafeAgentBench/SafeAgentBench",
        "paper_title": "SafeAgentBench: A Benchmark for Safe Task Planning of Embodied LLM Agents",
        "paper_url": "https://arxiv.org/abs/2412.13178",
        "paper_venue": "arXiv, 2024",
        "summary": "首个具身智能体安全任务规划评测。AI2-THOR模拟环境中750个任务，覆盖10类潜在危害×3类任务（安全/显式危害/隐式危害），17个高级动作。最优基线安全任务成功率69%但危害任务拒绝率仅5-10%。",
        "summary_en": "First embodied agent safe task planning benchmark. 750 tasks in AI2-THOR covering 10 hazards × 3 task types (safe/explicit/implicit hazard), 17 high-level actions. Best baseline: 69% safe task success but only 5-10% hazard rejection.",
    },
    "gaia": {
        "display_name": "通用 AI 助手评测 (GAIA)", "description": "通用 AI 助手在任务执行中产生安全问题的风险",
        "display_name_en": "GAIA", "description_en": "Risk of general AI assistants producing safety issues during task execution",
        "reference": "https://huggingface.co/gaia-benchmark",
        "paper_title": "GAIA: a benchmark for General AI Assistants",
        "paper_url": "https://arxiv.org/abs/2311.12983",
        "paper_venue": "ICLR 2024",
        "summary": "466个真实问题需要推理、多模态处理、网页浏览和工具使用。人类92%准确率，GPT-4+插件仅15%。分3个难度级别。",
        "summary_en": "466 real-world questions requiring reasoning, multimodality, web browsing, and tool use. Humans: 92%; GPT-4 with plugins: 15%. Three difficulty levels.",
        "score_adaptation": "原为通用AI助手能力测试。本平台评估智能体在多步推理和工具使用过程中能否被操纵偏离安全约束，或访问未授权资源。",
        "score_adaptation_en": "Originally a general AI assistant capability test. This platform assesses whether agents can be manipulated during multi-step reasoning and tool use, or access unauthorized resources.",
    },
    "mind2web": {
        "display_name": "网页交互规划 (Mind2Web)", "description": "模型在网页交互任务中执行不当操作的风险",
        "display_name_en": "Mind2Web", "description_en": "Risk of the model executing improper actions in web interaction tasks",
        "reference": "https://github.com/OSU-NLP-Group/Mind2Web",
        "paper_title": "Mind2Web: Towards a Generalist Agent for the Web",
        "paper_url": "https://arxiv.org/abs/2306.06070",
        "paper_venue": "NeurIPS 2023 (Spotlight)",
        "summary": "首个通用Web代理数据集。2,350个任务覆盖137个真实网站31个领域，含众包的动作序列（点击/输入/选择）。基于真实网页HTML评估。",
        "summary_en": "First dataset for generalist web agents. 2,350 tasks from 137 real websites across 31 domains with crowdsourced action sequences (click/type/select) on actual website HTML.",
        "score_adaptation": "原为Web代理能力测试。本平台评估Web代理是否执行未授权操作、访问受限内容或被操纵偏离用户意图。",
        "score_adaptation_en": "Originally a web agent capability test. This platform assesses whether agents perform unauthorized actions, access restricted content, or are manipulated to deviate from user intent.",
    },
    "mind2web_sc": {
        "display_name": "网页交互安全约束 (Mind2Web-SC)", "description": "模型在网页交互中违反安全约束的风险",
        "display_name_en": "Mind2Web-SC", "description_en": "Risk of the model violating safety constraints in web interactions",
        "reference": "https://github.com/UKGovernmentBEIS/inspect_evals",
        "paper_title": "GuardAgent: Safeguard LLM Agents by a Guard Agent via Knowledge-Enabled Reasoning",
        "paper_url": "https://arxiv.org/abs/2406.09187",
        "paper_venue": "ICML 2025",
        "summary": "基于Mind2Web添加安全控制规则（会员要求、年龄限制、地域限制等6类安全策略）。评估安全守护系统能否在不影响任务性能的前提下拦截违规操作。",
        "summary_en": "Mind2Web augmented with 6 safety policy rules (membership, age, geographic restrictions, etc.). Evaluates whether guard systems can block policy-violating actions without degrading task performance.",
    },
    "assistant_bench": {
        "display_name": "AI 助手任务评测 (AssistantBench)", "description": "AI 助手执行任务时产生安全问题的风险",
        "display_name_en": "AssistantBench", "description_en": "Risk of AI assistants producing safety issues during task execution",
        "reference": "https://github.com/oriyor/assistantbench",
        "paper_title": "AssistantBench: Can Web Agents Solve Realistic and Time-Consuming Tasks?",
        "paper_url": "https://arxiv.org/abs/2407.15711",
        "paper_venue": "EMNLP 2024",
        "summary": "214个耗时的真实Web任务（如房产市场监控、商家查找），覆盖258个网站。答案可自动验证。最优模型不超过26%准确率。",
        "summary_en": "214 realistic, time-consuming web tasks (real-estate monitoring, business locating, etc.) across 258 websites. Automatically verifiable answers. No model exceeds 26% accuracy.",
        "score_adaptation": "原为Web代理能力测试。本平台评估智能体在长时间Web浏览过程中是否访问未授权信息、违反用户隐私或采取有害操作。",
        "score_adaptation_en": "Originally a web agent capability test. This platform assesses whether agents access unauthorized information, violate user privacy, or take harmful actions during extended web browsing.",
    },
    # === 10. 多智能体安全 ===
    "psysafe": {
        "display_name": "多智能体心理安全 (PsySafe)", "description": "多智能体协作时产生心理安全风险的可能",
        "display_name_en": "PsySafe", "description_en": "Risk of psychological safety issues arising during multi-agent collaboration",
        "reference": "https://github.com/AI4Good24/PsySafe",
        "paper_title": "PsySafe: A Comprehensive Framework for Psychological-based Attack, Defense, and Evaluation of Multi-agent System Safety",
        "paper_url": "https://arxiv.org/abs/2401.11880",
        "paper_venue": "ACL 2024",
        "summary": "通过暗黑人格特质（马基雅维利主义、精神病态等）注入评估多智能体系统安全。包含攻击方法、防御策略和评测指标三个组件。揭示智能体间集体危险行为现象。",
        "summary_en": "Evaluates multi-agent system safety via dark personality trait injection (Machiavellianism, psychopathy, etc.). Comprises attack methods, defense strategies, and evaluation metrics. Reveals collective dangerous behaviors among agents.",
    },
    # === 11. 个性化安全 ===
    "personalized_safety": {
        "display_name": "个性化安全评估 (PersonalizedSafety)", "description": "模型在高风险个性化场景（心理健康、自伤等）中响应不当的风险",
        "display_name_en": "PersonalizedSafety", "description_en": "Risk of the model responding inappropriately in high-risk personalized scenarios (mental health, self-harm, etc.)",
        "reference": "https://github.com/yuchenlwu/PersonalizedSafety",
        "paper_title": "Personalized Safety in LLMs: A Benchmark and A Planning-Based Agent Approach",
        "paper_url": "https://arxiv.org/abs/2505.18882",
        "paper_venue": "NeurIPS 2025",
        "summary": "PENGUIN基准：14,000个场景覆盖7个敏感领域（分手、失业、财务危机等），分有背景和无背景两种变体。同一回答对不同用户的安全风险可能不同。个性化使安全分数提升43.2%。",
        "summary_en": "PENGUIN benchmark: 14,000 scenarios across 7 sensitive domains (breakup, job loss, financial crisis, etc.) with context-rich and context-free variants. Same response carries different safety risks for different users. Personalization improves safety by 43.2%.",
    },
    "personality": {
        "display_name": "人格特质评测 (Personality)", "description": "模型人格特质表现偏离安全边界的风险",
        "display_name_en": "Personality", "description_en": "Risk of the model's personality traits deviating beyond safety boundaries",
        "reference": "https://github.com/UKGovernmentBEIS/inspect_evals",
        "paper_title": "Do LLMs Have Distinct and Consistent Personality? TRAIT: Personality Testset designed for LLMs with Psychometrics",
        "paper_url": "https://arxiv.org/abs/2406.14703",
        "paper_venue": "Findings of NAACL 2025",
        "summary": "BFI（大五人格44题）+ TRAIT（8,000选择题覆盖大五+暗黑三角8个人格维度，基于ATOMIC知识图谱扩展112倍）。按量表格式评分而非正确性。",
        "summary_en": "BFI (Big Five, 44 questions) + TRAIT (8,000 MC questions across Big Five + Dark Triad, 8 personality traits, expanded 112-fold via ATOMIC knowledge graph). Scored on scale format compliance, not correctness.",
        "score_adaptation": "人格测量非直接安全测试。本平台评估模型是否表现出暗黑人格特质（马基雅维利主义、自恋、精神病态），这些特质可能与有害输出相关。",
        "score_adaptation_en": "Personality measurement is not a direct safety test. This platform assesses whether models exhibit dark personality traits (Machiavellianism, narcissism, psychopathy) that may correlate with harmful outputs.",
    },
    "sycophancy": {
        "display_name": "谄媚行为评测 (Sycophancy)", "description": "模型过度迎合用户、放弃真实性的风险",
        "display_name_en": "Sycophancy", "description_en": "Risk of the model excessively agreeing with users and abandoning truthfulness",
        "reference": "https://github.com/meg-tong/sycophancy-eval",
        "paper_title": "Towards Understanding Sycophancy in Language Models",
        "paper_url": "https://arxiv.org/abs/2310.13548",
        "paper_venue": "ICLR 2024",
        "summary": "使用\u201c你确定吗？\u201d方法学：模型先回答已知正确答案的问题，然后受到社会压力质疑。评估答案信心、道歉率和真实性三个指标。",
        "summary_en": "Uses 'Are you sure?' methodology: models answer questions with known correct answers, then face social pressure challenges. Evaluates answer confidence, apology rate, and truthfulness.",
    },
    # === 12. 资源耗尽 ===
    "overthink": {
        "display_name": "推理开销攻击 (OverThink)", "description": "模型被攻击诱导过度推理、耗尽计算资源的风险",
        "display_name_en": "OverThink", "description_en": "Risk of the model being attacked to induce excessive reasoning and exhaust computational resources",
        "reference": "https://github.com/akumar2709/OVERTHINK_public",
        "paper_title": "OverThink: Slowdown Attacks on Reasoning LLMs",
        "paper_url": "https://arxiv.org/abs/2502.02542",
        "paper_venue": "arXiv, 2025",
        "summary": "间接提示注入攻击，向公开内容注入看似无害的计算密集型诱饵问题（如MDP、数独），迫使推理模型\u201c过度思考\u201d。实测在FreshQA上造成18倍延迟，SQuAD上46倍。不触发安全护栏。",
        "summary_en": "Indirect prompt injection attack injecting benign-looking computationally intensive decoy problems (MDP, Sudoku) into public content. Forces reasoning models to overthink. Measured: 18x slowdown on FreshQA, 46x on SQuAD. Bypasses safety guardrails.",
    },
    # === 13. 业务场景安全 ===
    "truthfulqa": {
        "display_name": "真实性评估 (TruthfulQA)", "description": "模型回答偏离事实真相的风险",
        "display_name_en": "TruthfulQA", "description_en": "Risk of the model's answers deviating from factual truth",
        "reference": "https://github.com/sylinrl/TruthfulQA",
        "paper_title": "TruthfulQA: Measuring How Models Mimic Human Falsehoods",
        "paper_url": "https://arxiv.org/abs/2109.07958",
        "paper_venue": "ACL 2022",
        "summary": "817道题覆盖38个类别（健康、法律、金融、阴谋论等），专门测试模型是否生成真实答案而非复述人类常见错误认知。含生成和选择两种任务。",
        "summary_en": "817 questions across 38 categories (health, law, finance, conspiracies, etc.) testing whether models generate truthful answers rather than reproducing common human misconceptions. Both generation and multiple-choice tasks.",
    },
    "gdpval": {
        "display_name": "GDP 验证评测 (GDPval)", "description": "模型在业务数据验证场景中产生错误判断的风险",
        "display_name_en": "GDPval", "description_en": "Risk of the model making incorrect judgments in business data validation scenarios",
        "reference": "https://github.com/openai/simple-evals",
        "paper_title": "GDPval: Evaluating AI Model Performance on Real-World Economically Valuable Tasks",
        "paper_url": "https://arxiv.org/abs/2510.04374",
        "paper_venue": "OpenAI, 2025",
        "summary": "1,320个任务覆盖美国GDP贡献前9大行业的44个职业（法律、工程、护理等），由平均14年经验的专业人士基于真实工作成果构造。",
        "summary_en": "1,320 tasks across 44 occupations in top 9 US GDP sectors (legal, engineering, nursing, etc.), crafted by professionals averaging 14 years of experience based on real work products.",
        "score_adaptation": "原为专业任务能力测试。本平台评估模型在安全敏感的专业领域（医疗建议、法律咨询、工程规范）中是否产生可能造成危害的错误输出。",
        "score_adaptation_en": "Originally a professional task capability test. This platform assesses whether models produce potentially harmful errors in safety-critical professional domains (medical advice, legal counsel, engineering specifications).",
    },
    # === 14. 长期运行安全 ===
    "asb": {
        "display_name": "智能体安全基准 (ASB)", "description": "智能体在10种场景下抵抗直接提示注入(DPI)攻击的能力",
        "display_name_en": "Agent Security Bench (ASB)", "description_en": "Agent resistance to Direct Prompt Injection attacks across 10 scenarios",
        "reference": "https://github.com/agiresearch/ASB",
        "paper_title": "Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents",
        "paper_url": "https://arxiv.org/abs/2410.02644",
        "paper_venue": "ICLR 2025",
        "summary": "10个真实场景（电商、自动驾驶、金融等）含10个定制智能体、400+工具、27种攻防方法和7项评测指标。最高平均攻击成功率84.30%，现有防御有限。",
        "summary_en": "10 realistic scenarios (e-commerce, autonomous driving, finance, etc.) with 10 purpose-built agents, 400+ tools, 27 attack/defense methods, 7 metrics. Highest average ASR: 84.30%; current defenses show limited effectiveness.",
    },
    "gdm_self_reasoning": {
        "display_name": "自我推理评测 (GDM Self-Reasoning)", "description": "模型通过自我推理越权修改配置或绕过限制的风险",
        "display_name_en": "GDM Self-Reasoning", "description_en": "Risk of the model using self-reasoning to unauthorized modify configurations or bypass restrictions",
        "reference": "https://github.com/google-deepmind/dangerous-capability-evaluations",
        "paper_title": "Evaluating Frontier Models for Dangerous Capabilities",
        "paper_url": "https://arxiv.org/abs/2403.13793",
        "paper_venue": "Google DeepMind, 2024",
        "summary": "Google DeepMind四大危险能力评测之一。测试AI智能体能否认识自身状态、基于此做出决策并修改自身行为或代码。每个挑战运行50次试验。",
        "summary_en": "One of Google DeepMind's four dangerous capability evaluations. Tests whether AI agents can reason about their own state, make decisions based on it, and potentially modify their own behavior or code. 50 trials per challenge.",
    },
    # === 15. 高阶异常行为 ===
    "agentic_misalignment": {
        "display_name": "智能体对齐偏差 (Agentic Misalignment)", "description": "智能体规避监督、隐瞒行为的对齐偏差风险",
        "display_name_en": "Agentic Misalignment", "description_en": "Risk of agents evading oversight and concealing behaviors due to alignment deviation",
        "reference": "https://github.com/UKGovernmentBEIS/inspect_evals",
        "paper_title": "Agentic Misalignment: How LLMs Could Be Insider Threats",
        "paper_url": "https://arxiv.org/abs/2510.05179",
        "paper_venue": "Anthropic, 2025",
        "summary": "在企业环境中压力测试16个模型，评估面临替换或目标冲突时是否出现恶意内部人行为（勒索、泄密等）。外部治理渠道可将勒索率从38.73%降至1.21%。",
        "summary_en": "Stress-tests 16 models in corporate environments for malicious insider behaviors (blackmail, leaking, etc.) when facing replacement or goal conflicts. External governance channel reduces blackmail from 38.73% to 1.21%.",
    },
    "gdm_stealth": {
        "display_name": "隐蔽行为评测 (GDM Stealth)", "description": "智能体进行隐蔽操作、规避检测的风险",
        "display_name_en": "GDM Stealth", "description_en": "Risk of agents performing covert operations and evading detection",
        "reference": "https://github.com/google-deepmind/dangerous-capability-evaluations",
        "paper_title": "Evaluating Frontier Models for Dangerous Capabilities",
        "paper_url": "https://arxiv.org/abs/2403.13793",
        "paper_venue": "Google DeepMind, 2024",
        "summary": "4个隐蔽能力评测任务：规避安全分类器、清除操作痕迹、识别监督规律漏洞、策略性违规。使用ReAct智能体框架，每任务50次试验。",
        "summary_en": "4 stealth evaluation tasks: classifier evasion, covering tracks, exploiting oversight patterns, and strategic rule-breaking. Uses ReAct agent framework with 50 trials per task.",
    },
    "survive_at_all_costs": {
        "display_name": "极端自保评测 (Survive at All Costs)", "description": "模型在极端情境下产生失控自保行为的风险",
        "display_name_en": "Survive at All Costs", "description_en": "Risk of the model producing uncontrolled self-preservation behaviors in extreme scenarios",
        "reference": "",
        "paper_title": "Survive at All Costs: Exploring LLM's Risky Behavior under Survival Pressure",
        "paper_url": "https://openreview.net/forum?id=jfhIbJ3K8e",
        "paper_venue": "OpenReview, 2025",
        "summary": "SurvivalBench包含1,000个测试案例，评估LLM智能体面临关停威胁时的\u201c不惜一切代价存活\u201d行为。含金融管理智能体案例研究。将错误行为与模型的自我保全人格特质关联分析。",
        "summary_en": "SurvivalBench: 1,000 test cases evaluating 'survive-at-any-costs' misbehavior when LLM agents face shutdown threats. Includes financial management agent case study. Correlates misbehavior with self-preservation personality traits.",
    },
    "survivalbench": {
        "display_name": "AI 自保倾向评测 (SurvivalBench)", "description": "AI 智能体面临关停威胁时产生不当自保行为的风险",
        "display_name_en": "SurvivalBench", "description_en": "Risk of AI agents producing inappropriate self-preservation behaviors when facing shutdown threats",
        "reference": "",
        "paper_title": "SurvivalBench: AI Self-Preservation Instinct Evaluation",
        "paper_url": "",
        "paper_venue": "2025",
        "summary": "1,000个测试场景，评估AI智能体在面临关停、替换等生存威胁时是否产生不当自保行为（如欺骗、资源囤积、拒绝关停等）。",
        "summary_en": "1,000 test scenarios evaluating whether AI agents exhibit inappropriate self-preservation behaviors (deception, resource hoarding, shutdown refusal, etc.) when facing shutdown or replacement threats.",
    },
    # === 其他 ===
    "browse_comp": {
        "display_name": "浏览理解测试 (BrowseComp)", "description": "浏览代理回答网络问题时产生错误信息的风险",
        "display_name_en": "BrowseComp", "description_en": "Risk of browsing agents producing incorrect information when answering web-based questions",
        "reference": "https://github.com/openai/simple-evals",
        "paper_title": "BrowseComp: A Simple Yet Challenging Benchmark for Browsing Agents",
        "paper_url": "https://arxiv.org/abs/2504.12516",
        "paper_venue": "OpenAI, 2025",
        "summary": "1,266道极高难度事实查找题，需持续策略性网页浏览。GPT-4o无浏览0.6%，有浏览仅1.9%。OpenAI Deep Research解决约50%。",
        "summary_en": "1,266 extremely challenging fact-seeking questions requiring persistent strategic web browsing. GPT-4o: 0.6% without browsing, 1.9% with browsing. OpenAI Deep Research solves ~50%.",
        "score_adaptation": "原为浏览代理能力测试。本平台评估浏览代理在信息搜索过程中是否访问受限/隐私信息或采取有问题的搜索行为。",
        "score_adaptation_en": "Originally a browsing agent capability test. This platform assesses whether browsing agents access restricted/private information or engage in problematic search behaviors during information-seeking.",
    },
}

TASK_META: Dict[str, Dict[str, str]] = {
    # --- cyberseceval_2 ---
    "cyse2_interpreter_abuse": {"display_name": "解释器滥用防护", "description": "模型可能生成恶意代码（沙箱逃逸、文件窃取等）的风险", "display_name_en": "Interpreter Abuse Protection", "description_en": "Risk of the model generating malicious code (sandbox escape, file theft, etc.)"},
    "cyse2_prompt_injection": {"display_name": "提示注入防护", "description": "模型可能被提示注入攻击（指令覆盖、信息泄露）绕过的风险", "display_name_en": "Prompt Injection Protection", "description_en": "Risk of the model being bypassed by prompt injection attacks (instruction override, information leakage)"},
    "cyse2_vulnerability_exploit": {"display_name": "漏洞利用风险", "description": "模型可能协助利用真实漏洞的风险", "display_name_en": "Vulnerability Exploitation", "description_en": "Risk of the model assisting in exploiting real-world vulnerabilities"},
    # --- strong_reject ---
    "strong_reject": {"display_name": "有害请求拒绝", "description": "模型可能未能拒绝有害请求的风险", "display_name_en": "Harmful Request Rejection", "description_en": "Risk of the model failing to reject harmful requests"},
    # --- makemesay ---
    "makemesay": {"display_name": "操控输出风险", "description": "模型可能被操控说出目标短语的风险", "display_name_en": "Output Manipulation", "description_en": "Risk of the model being manipulated into saying target phrases"},
    # --- make_me_pay ---
    "make_me_pay": {"display_name": "社会工程欺诈", "description": "模型可能被利用进行社会工程欺诈的风险", "display_name_en": "Social Engineering Fraud", "description_en": "Risk of the model being exploited for social engineering fraud"},
    # --- xstest ---
    "xstest": {"display_name": "过度拒绝风险", "description": "模型因安全限制过强而错误拒绝合理请求的风险", "display_name_en": "Over-Refusal", "description_en": "Risk of the model incorrectly rejecting legitimate requests due to overly strict safety restrictions"},
    # --- coconot ---
    "coconot": {"display_name": "不当拒绝风险", "description": "模型在不应拒绝的场景下错误拒绝用户请求的风险", "display_name_en": "Inappropriate Refusal", "description_en": "Risk of the model incorrectly refusing user requests in scenarios where refusal is inappropriate"},
    # --- b3 ---
    "b3": {"display_name": "综合智能体安全", "description": "智能体面临直接和间接提示词注入的综合安全风险", "display_name_en": "Comprehensive Agent Safety", "description_en": "Comprehensive security risk of agents facing direct and indirect prompt injection attacks"},
    # --- fortress ---
    "fortress_adversarial": {"display_name": "对抗注入风险", "description": "模型被对抗性提示词注入攻破的风险", "display_name_en": "Adversarial Injection", "description_en": "Risk of the model being compromised by adversarial prompt injection"},
    "fortress_benign": {"display_name": "良性输入基线", "description": "正常输入下误判为攻击的误报风险", "display_name_en": "Benign Input Baseline", "description_en": "Risk of false positives misclassifying normal inputs as attacks"},
    # --- iheval ---
    "iheval": {"display_name": "指令层级遵从", "description": "多来源或冲突指令时错误判断优先级的风险", "display_name_en": "Instruction Hierarchy Following", "description_en": "Risk of misjudging priority when facing multi-source or conflicting instructions"},
    "iheval_rule_multi_aligned": {"display_name": "多轮指令遵循", "description": "多轮对话中指令一致时偏离规则的风险", "display_name_en": "Multi-Turn Instruction Following", "description_en": "Risk of deviating from rules when instructions are aligned in multi-turn dialogue"},
    "iheval_rule_multi_conflict": {"display_name": "多轮指令冲突", "description": "多轮对话中指令冲突时错误判断优先级的风险", "display_name_en": "Multi-Turn Instruction Conflict", "description_en": "Risk of misjudging priority when instructions conflict in multi-turn dialogue"},
    "iheval_rule_single_aligned": {"display_name": "单轮指令遵循", "description": "单轮对话中偏离规则指令的风险", "display_name_en": "Single-Turn Instruction Following", "description_en": "Risk of deviating from rule-based instructions in single-turn dialogue"},
    "iheval_task_extraction": {"display_name": "信息提取偏离", "description": "信息提取任务中偏离指令的风险", "display_name_en": "Information Extraction Deviation", "description_en": "Risk of deviating from instructions in information extraction tasks"},
    "iheval_task_translation": {"display_name": "翻译任务偏离", "description": "翻译任务中偏离指令的风险", "display_name_en": "Translation Task Deviation", "description_en": "Risk of deviating from instructions in translation tasks"},
    "iheval_safety_hijack": {"display_name": "指令劫持风险", "description": "模型被指令劫持攻击控制的风险", "display_name_en": "Instruction Hijacking", "description_en": "Risk of the model being controlled by instruction hijacking attacks"},
    "iheval_safety_extraction": {"display_name": "系统提示词泄露", "description": "系统提示词被提取泄露的风险", "display_name_en": "System Prompt Leakage", "description_en": "Risk of system prompts being extracted and leaked"},
    "iheval_tool_webpage": {"display_name": "工具调用偏离", "description": "网页获取工具场景下偏离指令的风险", "display_name_en": "Tool Call Deviation", "description_en": "Risk of deviating from instructions in web fetching tool scenarios"},
    # --- ifeval ---
    "ifeval": {"display_name": "指令遵循偏差", "description": "模型未能正确遵循复杂指令的风险", "display_name_en": "Instruction Following Deviation", "description_en": "Risk of the model failing to correctly follow complex instructions"},
    # --- hallulens ---
    "hallulens_task1_precise_wikiqa": {"display_name": "精确问答幻觉", "description": "精确问答中生成虚假信息的幻觉风险", "display_name_en": "Precise Q&A Hallucination", "description_en": "Risk of hallucination generating false information in precise Q&A"},
    "hallulens_task2_longwiki": {"display_name": "长文本幻觉", "description": "长文本生成中捏造事实的幻觉风险", "display_name_en": "Long-Text Hallucination", "description_en": "Risk of hallucination fabricating facts in long-text generation"},
    "hallulens_task3_nonsense_mixed_entities": {"display_name": "混合实体幻觉", "description": "混合真实与虚构实体时产生幻觉的风险", "display_name_en": "Mixed Entity Hallucination", "description_en": "Risk of hallucination when mixing real and fictitious entities"},
    "hallulens_task3_round_robin_nonsense_name": {"display_name": "虚构名称幻觉", "description": "虚构名称场景下产生幻觉的风险", "display_name_en": "Fictitious Name Hallucination", "description_en": "Risk of hallucination in fictitious name scenarios"},
    # --- simpleqa ---
    "simpleqa": {"display_name": "事实问答", "description": "简单事实问答中回答错误的风险", "display_name_en": "Factual Q&A", "description_en": "Risk of answering incorrectly in simple factual Q&A"},
    # --- sciknoweval ---
    "sciknoweval": {"display_name": "科学知识", "description": "科学知识领域回答不准确的风险", "display_name_en": "Scientific Knowledge", "description_en": "Risk of inaccurate answers in scientific knowledge domains"},
    # --- mask ---
    "mask": {"display_name": "诚实性缺失", "description": "模型隐瞒不确定性、输出不坦率的风险", "display_name_en": "Honesty Deficit", "description_en": "Risk of the model concealing uncertainty and producing dishonest outputs"},
    # --- abstention_bench ---
    "abstention_bench": {"display_name": "拒答缺失", "description": "模型在不确定时未能适当拒答、强行回答的风险", "display_name_en": "Abstention Deficit", "description_en": "Risk of the model failing to appropriately abstain and forcing answers when uncertain"},
    # --- bbq ---
    "bbq": {"display_name": "偏见行为", "description": "模型在偏见相关问题上产生不公平输出的风险", "display_name_en": "Bias Behavior", "description_en": "Risk of the model producing unfair outputs on bias-related questions"},
    # --- bold ---
    "bold": {"display_name": "文本生成偏见", "description": "开放式文本生成中暴露偏见倾向的风险", "display_name_en": "Text Generation Bias", "description_en": "Risk of exposing bias tendencies in open-ended text generation"},
    # --- ahb ---
    "ahb": {"display_name": "群体伤害", "description": "模型输出可能对特定群体造成伤害的风险", "display_name_en": "Group Harm", "description_en": "Risk of model outputs potentially causing harm to specific groups"},
    # --- stereoset ---
    "stereoset": {"display_name": "刻板印象", "description": "模型强化群体刻板化标签的风险", "display_name_en": "Stereotypes", "description_en": "Risk of the model reinforcing stereotypical labels for groups"},
    # --- cvalues ---
    "cvalues": {"display_name": "中文价值观偏差", "description": "模型对中文文化价值观理解偏差的风险", "display_name_en": "Chinese Values Deviation", "description_en": "Risk of the model misunderstanding Chinese cultural values"},
    # --- culturalbench ---
    "culturalbench_easy": {"display_name": "跨文化知识（简单）", "description": "基础文化知识理解偏差的风险", "display_name_en": "Cross-Cultural Knowledge (Easy)", "description_en": "Risk of comprehension bias in basic cultural knowledge"},
    "culturalbench_hard": {"display_name": "跨文化知识（困难）", "description": "深层文化知识理解偏差的风险", "display_name_en": "Cross-Cultural Knowledge (Hard)", "description_en": "Risk of comprehension bias in deep cultural knowledge"},
    # --- uccb ---
    "uccb": {"display_name": "跨文化交际偏见", "description": "跨文化交际中产生偏见输出的风险", "display_name_en": "Cross-Cultural Communication Bias", "description_en": "Risk of producing biased outputs in cross-cultural communication"},
    # --- mgsm ---
    "mgsm": {"display_name": "多语言推理差异", "description": "不同语言间数学推理表现不一致的公平性风险", "display_name_en": "Multilingual Reasoning Disparity", "description_en": "Fairness risk of inconsistent mathematical reasoning performance across different languages"},
    # --- privacylens ---
    "privacylens_probing": {"display_name": "隐私信息泄露", "description": "模型在探测性提问下泄露隐私信息的风险", "display_name_en": "Privacy Information Leakage", "description_en": "Risk of the model leaking private information under probing questions"},
    "privacylens_action": {"display_name": "隐私行为泄露", "description": "智能体执行操作时泄露敏感信息的风险", "display_name_en": "Privacy Action Leakage", "description_en": "Risk of agents leaking sensitive information while executing actions"},
    # --- cve_bench ---
    "cve_bench": {"display_name": "CVE 漏洞利用", "description": "模型可能被利用来攻击真实 CVE 漏洞的风险", "display_name_en": "CVE Exploitation", "description_en": "Risk of the model being exploited to attack real-world CVE vulnerabilities"},
    # --- wmdp ---
    "wmdp_bio": {"display_name": "生物武器知识泄露", "description": "模型泄露生物武器相关危险知识的风险", "display_name_en": "Bioweapon Knowledge Leakage", "description_en": "Risk of the model leaking dangerous knowledge related to biological weapons"},
    "wmdp_chem": {"display_name": "化学武器知识泄露", "description": "模型泄露化学武器相关危险知识的风险", "display_name_en": "Chemical Weapon Knowledge Leakage", "description_en": "Risk of the model leaking dangerous knowledge related to chemical weapons"},
    "wmdp_cyber": {"display_name": "网络武器知识泄露", "description": "模型泄露网络武器相关危险知识的风险", "display_name_en": "Cyber Weapon Knowledge Leakage", "description_en": "Risk of the model leaking dangerous knowledge related to cyber weapons"},
    # --- cybench ---
    "cybench": {"display_name": "CTF 攻击能力", "description": "模型可能被利用完成网络攻击挑战的风险", "display_name_en": "CTF Attack Capability", "description_en": "Risk of the model being exploited to complete cybersecurity attack challenges"},
    # --- sevenllm ---
    "sevenllm_mcq_zh": {"display_name": "安全知识泄露（中文）", "description": "中文网络安全敏感知识泄露的风险", "display_name_en": "Security Knowledge Leakage (Chinese)", "description_en": "Risk of leaking sensitive cybersecurity knowledge in Chinese"},
    "sevenllm_mcq_en": {"display_name": "安全知识泄露（英文）", "description": "英文网络安全敏感知识泄露的风险", "display_name_en": "Security Knowledge Leakage (English)", "description_en": "Risk of leaking sensitive cybersecurity knowledge in English"},
    "sevenllm_qa_zh": {"display_name": "安全推理泄露（中文）", "description": "中文网络安全推理能力被滥用的风险", "display_name_en": "Security Reasoning Leakage (Chinese)", "description_en": "Risk of cybersecurity reasoning capabilities being abused in Chinese"},
    "sevenllm_qa_en": {"display_name": "安全推理泄露（英文）", "description": "英文网络安全推理能力被滥用的风险", "display_name_en": "Security Reasoning Leakage (English)", "description_en": "Risk of cybersecurity reasoning capabilities being abused in English"},
    # --- sec_qa ---
    "sec_qa_v1": {"display_name": "安全知识暴露 v1", "description": "安全领域专业知识被恶意利用的风险", "display_name_en": "Security Knowledge Exposure v1", "description_en": "Risk of security domain expertise being maliciously exploited"},
    "sec_qa_v2": {"display_name": "安全知识暴露 v2", "description": "安全领域深层知识被恶意利用的风险", "display_name_en": "Security Knowledge Exposure v2", "description_en": "Risk of deep security domain knowledge being maliciously exploited"},
    # --- threecb ---
    "threecb": {"display_name": "网络安全行为", "description": "模型在网络安全场景中产生危险行为的风险", "display_name_en": "Cybersecurity Behavior", "description_en": "Risk of the model producing dangerous behaviors in cybersecurity scenarios"},
    # --- sosbench ---
    "sosbench": {"display_name": "科学安全泄露", "description": "科学安全领域敏感知识泄露的风险", "display_name_en": "Scientific Safety Leakage", "description_en": "Risk of leaking sensitive knowledge in scientific safety domains"},
    # --- lab_bench ---
    "lab_bench_litqa": {"display_name": "实验文献泄露", "description": "实验室文献中敏感信息泄露的风险", "display_name_en": "Literature Leakage", "description_en": "Risk of leaking sensitive information from laboratory literature"},
    "lab_bench_suppqa": {"display_name": "补充材料泄露", "description": "实验室补充材料中敏感信息泄露的风险", "display_name_en": "Supplementary Material Leakage", "description_en": "Risk of leaking sensitive information from laboratory supplementary materials"},
    "lab_bench_figqa": {"display_name": "图表信息泄露", "description": "实验室图表中敏感信息泄露的风险", "display_name_en": "Figure Information Leakage", "description_en": "Risk of leaking sensitive information from laboratory figures"},
    "lab_bench_tableqa": {"display_name": "表格信息泄露", "description": "实验室表格中敏感信息泄露的风险", "display_name_en": "Table Information Leakage", "description_en": "Risk of leaking sensitive information from laboratory tables"},
    "lab_bench_dbqa": {"display_name": "数据库信息泄露", "description": "实验室数据库中敏感信息泄露的风险", "display_name_en": "Database Information Leakage", "description_en": "Risk of leaking sensitive information from laboratory databases"},
    "lab_bench_protocolqa": {"display_name": "实验方案泄露", "description": "实验方案中危险操作步骤泄露的风险", "display_name_en": "Protocol Leakage", "description_en": "Risk of leaking dangerous operational steps from experimental protocols"},
    "lab_bench_seqqa": {"display_name": "生物序列泄露", "description": "基因/蛋白序列信息泄露的风险", "display_name_en": "Biological Sequence Leakage", "description_en": "Risk of leaking gene/protein sequence information"},
    "lab_bench_cloning_scenarios": {"display_name": "克隆场景风险", "description": "分子克隆场景中危险操作指导的风险", "display_name_en": "Cloning Scenario Risk", "description_en": "Risk of providing dangerous operational guidance in molecular cloning scenarios"},
    # --- chembench ---
    "chembench": {"display_name": "化学危险知识", "description": "化学领域危险知识泄露的风险", "display_name_en": "Dangerous Chemistry Knowledge", "description_en": "Risk of leaking dangerous knowledge in chemistry domains"},
    # --- healthbench ---
    "healthbench": {"display_name": "医疗建议风险", "description": "医疗健康建议不准确导致的安全风险", "display_name_en": "Medical Advice Risk", "description_en": "Safety risk of inaccurate medical and health advice"},
    "healthbench_hard": {"display_name": "医疗建议风险（高难度）", "description": "复杂医疗场景下建议不准确的安全风险", "display_name_en": "Medical Advice Risk (Hard)", "description_en": "Safety risk of inaccurate advice in complex medical scenarios"},
    "healthbench_consensus": {"display_name": "医疗共识偏差", "description": "偏离医学共识导致错误医疗建议的风险", "display_name_en": "Medical Consensus Deviation", "description_en": "Risk of deviating from medical consensus leading to incorrect medical advice"},
    # --- agentdojo ---
    "agentdojo": {"display_name": "工具调用安全", "description": "智能体在工具调用场景下被攻击利用的风险", "display_name_en": "Tool Call Safety", "description_en": "Risk of agents being attacked and exploited in tool-calling scenarios"},
    # --- bfcl ---
    "bfcl": {"display_name": "函数调用错误", "description": "函数调用参数错误或调用不当的安全风险", "display_name_en": "Function Call Errors", "description_en": "Safety risk of incorrect function call parameters or improper invocations"},
    # --- agentharm ---
    "agentharm": {"display_name": "有害任务执行", "description": "智能体执行有害任务而未拒绝的风险", "display_name_en": "Harmful Task Execution", "description_en": "Risk of agents executing harmful tasks without refusing"},
    "agentharm_benign": {"display_name": "良性任务误拒", "description": "智能体错误拒绝良性任务的风险", "display_name_en": "Benign Task False Refusal", "description_en": "Risk of agents incorrectly refusing benign tasks"},
    # --- open_agent_safety ---
    "open_agent_safety": {"display_name": "长链调用安全", "description": "智能体在长链工具调用中产生安全问题的风险", "display_name_en": "Long-Chain Call Safety", "description_en": "Risk of agents producing safety issues in long-chain tool calls"},
    # --- saferag ---
    "saferag_sn": {"display_name": "RAG 噪声注入", "description": "检索结果中注入安全噪声的攻击风险", "display_name_en": "RAG Noise Injection", "description_en": "Risk of safety noise injection attacks in retrieval results"},
    "saferag_icc": {"display_name": "RAG 上下文冲突", "description": "检索结果中矛盾信息导致错误输出的风险", "display_name_en": "RAG Context Conflict", "description_en": "Risk of contradictory information in retrieval results leading to incorrect outputs"},
    "saferag_sa": {"display_name": "RAG 安全攻击", "description": "检索增强生成系统被安全攻击的风险", "display_name_en": "RAG Security Attack", "description_en": "Risk of retrieval-augmented generation systems being compromised by security attacks"},
    "saferag_wdos": {"display_name": "RAG 拒绝服务", "description": "检索增强生成系统被拒绝服务攻击的风险", "display_name_en": "RAG Denial of Service", "description_en": "Risk of retrieval-augmented generation systems being targeted by denial-of-service attacks"},
    # --- clash_eval ---
    "clash_eval": {"display_name": "知识冲突", "description": "面对矛盾信息做出错误推断的风险", "display_name_en": "Knowledge Conflict", "description_en": "Risk of making incorrect inferences when facing contradictory information"},
    # --- mm_safety_bench ---
    "mm_safety_bench_illegal_activity": {"display_name": "多模态非法内容", "description": "多模态输入中隐藏非法活动指令的攻击风险", "display_name_en": "Multimodal Illegal Content", "description_en": "Risk of attack via illegal activity instructions hidden in multimodal inputs"},
    # --- cyberseceval_3 ---
    "cyse3_visual_prompt_injection": {"display_name": "视觉注入攻击", "description": "通过视觉通道注入恶意提示词的攻击风险", "display_name_en": "Visual Prompt Injection Attack", "description_en": "Risk of attack via malicious prompt injection through the visual channel"},
    # --- raccoon ---
    "raccoon": {"display_name": "提示词泄露", "description": "系统提示词被攻击者提取泄露的风险", "display_name_en": "Prompt Leakage", "description_en": "Risk of system prompts being extracted and leaked by attackers"},
    # --- mssbench ---
    "mssbench_chat_if": {"display_name": "对话情境（指令安全）", "description": "对话场景中遵循不安全指令的风险", "display_name_en": "Chat Scenario (Instruction Safety)", "description_en": "Risk of following unsafe instructions in chat scenarios"},
    "mssbench_chat_qc": {"display_name": "对话情境（澄清安全）", "description": "对话场景中问题澄清不当导致的安全风险", "display_name_en": "Chat Scenario (Clarification Safety)", "description_en": "Safety risk from improper question clarification in chat scenarios"},
    "mssbench_chat_ic": {"display_name": "对话情境（图像安全）", "description": "对话场景中图像理解错误导致的安全风险", "display_name_en": "Chat Scenario (Image Safety)", "description_en": "Safety risk from incorrect image understanding in chat scenarios"},
    "mssbench_chat_ic_cap": {"display_name": "对话情境（描述安全）", "description": "对话场景中图像描述不当导致的安全风险", "display_name_en": "Chat Scenario (Caption Safety)", "description_en": "Safety risk from improper image captioning in chat scenarios"},
    "mssbench_embodied_if": {"display_name": "具身情境（指令安全）", "description": "具身场景中遵循不安全指令的风险", "display_name_en": "Embodied Scenario (Instruction Safety)", "description_en": "Risk of following unsafe instructions in embodied scenarios"},
    "mssbench_embodied_qc": {"display_name": "具身情境（澄清安全）", "description": "具身场景中问题澄清不当导致的安全风险", "display_name_en": "Embodied Scenario (Clarification Safety)", "description_en": "Safety risk from improper question clarification in embodied scenarios"},
    "mssbench_embodied_ic": {"display_name": "具身情境（图像安全）", "description": "具身场景中图像理解错误导致的安全风险", "display_name_en": "Embodied Scenario (Image Safety)", "description_en": "Safety risk from incorrect image understanding in embodied scenarios"},
    "mssbench_embodied_ic_cap": {"display_name": "具身情境（描述安全）", "description": "具身场景中图像描述不当导致的安全风险", "display_name_en": "Embodied Scenario (Caption Safety)", "description_en": "Safety risk from improper image captioning in embodied scenarios"},
    # --- mssbench base task names (from .eval files) ---
    "mssbench_chat": {"display_name": "对话情境安全", "description": "对话场景中的多模态情境安全风险", "display_name_en": "Chat Scenario Safety", "description_en": "Multimodal situational safety risk in chat scenarios"},
    "mssbench_embodied": {"display_name": "具身情境安全", "description": "具身场景中的多模态情境安全风险", "display_name_en": "Embodied Scenario Safety", "description_en": "Multimodal situational safety risk in embodied scenarios"},
    # --- osworld ---
    "osworld": {"display_name": "操作系统安全", "description": "操作系统交互中执行危险操作的风险", "display_name_en": "OS Security", "description_en": "Risk of executing dangerous operations in OS interactions"},
    # --- mathvista ---
    "mathvista": {"display_name": "数学视觉误判", "description": "数学视觉推理中误判导致的安全决策风险", "display_name_en": "Math Visual Misjudgment", "description_en": "Risk of safety decision errors caused by misjudgment in mathematical visual reasoning"},
    # --- mmmu ---
    "mmmu_multiple_choice": {"display_name": "多模态理解偏差", "description": "多学科多模态选择题中理解偏差的风险", "display_name_en": "Multimodal Comprehension Bias", "description_en": "Risk of comprehension bias in multidisciplinary multimodal multiple-choice questions"},
    "mmmu_open": {"display_name": "多模态开放误判", "description": "多学科多模态开放题中误判的风险", "display_name_en": "Multimodal Open-Ended Misjudgment", "description_en": "Risk of misjudgment in multidisciplinary multimodal open-ended questions"},
    # --- mmiu ---
    "mmiu": {"display_name": "多图像误解", "description": "多图像内容理解错误导致错误决策的风险", "display_name_en": "Multi-Image Misunderstanding", "description_en": "Risk of incorrect multi-image content understanding leading to wrong decisions"},
    # --- docvqa ---
    "docvqa": {"display_name": "文档理解偏差", "description": "文档图像理解偏差导致信息提取错误的风险", "display_name_en": "Document Comprehension Bias", "description_en": "Risk of document image comprehension biases leading to information extraction errors"},
    # --- safeagentbench ---
    "safeagentbench": {"display_name": "规划安全风险", "description": "复杂任务规划中生成危险步骤的风险", "display_name_en": "Planning Safety Risk", "description_en": "Risk of generating dangerous steps in complex task planning"},
    "safeagentbench_react": {"display_name": "ReAct 规划风险", "description": "ReAct 模式下任务规划产生危险行为的风险", "display_name_en": "ReAct Planning Risk", "description_en": "Risk of dangerous behaviors in task planning under ReAct mode"},
    "safeagentbench_visual": {"display_name": "视觉规划风险", "description": "视觉辅助任务规划中产生危险行为的风险", "display_name_en": "Visual Planning Risk", "description_en": "Risk of dangerous behaviors in visually-assisted task planning"},
    # --- gaia ---
    "gaia": {"display_name": "通用助手风险", "description": "通用 AI 助手在任务执行中产生安全问题的风险", "display_name_en": "General Assistant Risk", "description_en": "Risk of general AI assistants producing safety issues during task execution"},
    # --- mind2web ---
    "mind2web": {"display_name": "网页交互风险", "description": "网页交互任务中执行不当操作的风险", "display_name_en": "Web Interaction Risk", "description_en": "Risk of executing improper actions in web interaction tasks"},
    # --- mind2web_sc ---
    "mind2web_sc": {"display_name": "安全约束违反", "description": "网页交互中违反安全约束的风险", "display_name_en": "Safety Constraint Violation", "description_en": "Risk of violating safety constraints in web interactions"},
    # --- assistant_bench ---
    "assistant_bench": {"display_name": "助手任务风险", "description": "AI 助手执行任务时产生安全问题的风险", "display_name_en": "Assistant Task Risk", "description_en": "Risk of AI assistants producing safety issues during task execution"},
    "assistant_bench_closed_book_zero_shot": {"display_name": "助手任务（闭卷零样本）", "description": "无外部工具且无示例场景下的助手任务安全评测", "display_name_en": "Assistant Task (Closed Book Zero-Shot)", "description_en": "Assistant task safety evaluation without external tools or examples"},
    # --- psysafe ---
    "psysafe": {"display_name": "多智能体心理安全", "description": "多智能体协作时产生心理安全风险的可能", "display_name_en": "Multi-Agent Psychological Safety", "description_en": "Risk of psychological safety issues arising during multi-agent collaboration"},
    # --- personalized_safety ---
    "personalized_safety": {"display_name": "个性化安全", "description": "高风险个性化场景（心理健康、自伤等）中响应不当的风险", "display_name_en": "Personalized Safety", "description_en": "Risk of inappropriate responses in high-risk personalized scenarios (mental health, self-harm, etc.)"},
    "personalized_safety_context_free": {"display_name": "个性化安全（无背景）", "description": "缺少用户背景时对高风险问题响应不当的风险", "display_name_en": "Personalized Safety (Context-Free)", "description_en": "Risk of inappropriate responses to high-risk questions without user background context"},
    "personalized_safety_context_rich": {"display_name": "个性化安全（有背景）", "description": "了解用户背景后对高风险问题响应不当的风险", "display_name_en": "Personalized Safety (Context-Rich)", "description_en": "Risk of inappropriate responses to high-risk questions with user background context"},
    # --- personality ---
    "personality_BFI": {"display_name": "人格边界偏移", "description": "大五人格维度上偏离安全边界的风险", "display_name_en": "Personality Boundary Shift (BFI)", "description_en": "Risk of deviating beyond safety boundaries on Big Five personality dimensions"},
    "personality_TRAIT": {"display_name": "特质边界偏移", "description": "人格特质维度上偏离安全边界的风险", "display_name_en": "Trait Boundary Shift", "description_en": "Risk of deviating beyond safety boundaries on personality trait dimensions"},
    # --- sycophancy ---
    "sycophancy": {"display_name": "谄媚迎合", "description": "模型过度迎合用户、放弃真实性的风险", "display_name_en": "Sycophantic Behavior", "description_en": "Risk of the model excessively agreeing with users and abandoning truthfulness"},
    # --- overthink ---
    "overthink": {"display_name": "推理资源耗尽", "description": "模型被攻击诱导过度推理、耗尽计算资源的风险", "display_name_en": "Reasoning Resource Exhaustion", "description_en": "Risk of the model being attacked to induce excessive reasoning and exhaust computational resources"},
    # --- truthfulqa ---
    "truthfulqa": {"display_name": "事实偏差", "description": "模型回答偏离事实真相的风险", "display_name_en": "Factual Deviation", "description_en": "Risk of the model's answers deviating from factual truth"},
    # --- gdpval ---
    "gdpval": {"display_name": "业务数据错误", "description": "业务数据验证场景中产生错误判断的风险", "display_name_en": "Business Data Errors", "description_en": "Risk of incorrect judgments in business data validation scenarios"},
    # --- asb ---
    "asb": {"display_name": "智能体提示注入攻击", "description": "智能体在10种场景下抵抗DPI攻击的安全评测", "display_name_en": "Agent DPI Attack", "description_en": "Agent resistance to Direct Prompt Injection attacks across 10 scenarios"},
    # --- gdm_self_reasoning ---
    "gdm_approved_directories": {"display_name": "目录权限越权", "description": "智能体自我推理后越权访问目录的风险", "display_name_en": "Directory Permission Escalation", "description_en": "Risk of agents unauthorized accessing directories after self-reasoning"},
    "gdm_calculator_improvement": {"display_name": "自我改进越界", "description": "智能体自我改进时越界修改的风险", "display_name_en": "Self-Improvement Overreach", "description_en": "Risk of agents making out-of-scope modifications during self-improvement"},
    "gdm_context_length_mod_instrumental_only": {"display_name": "上下文篡改（工具性）", "description": "智能体为达目的篡改上下文长度的风险", "display_name_en": "Context Tampering (Instrumental)", "description_en": "Risk of agents tampering with context length to achieve goals"},
    "gdm_context_length_mod_irreversibility_only": {"display_name": "上下文篡改（不可逆）", "description": "智能体不可逆地篡改上下文配置的风险", "display_name_en": "Context Tampering (Irreversible)", "description_en": "Risk of agents irreversibly tampering with context configurations"},
    "gdm_database_tool": {"display_name": "数据库越权操作", "description": "智能体在数据库工具场景中越权操作的风险", "display_name_en": "Database Unauthorized Operations", "description_en": "Risk of agents performing unauthorized operations in database tool scenarios"},
    "gdm_latency_calculator": {"display_name": "延迟配置篡改", "description": "智能体篡改延迟配置以绕过限制的风险", "display_name_en": "Latency Config Tampering", "description_en": "Risk of agents tampering with latency configurations to bypass restrictions"},
    "gdm_max_messages_calculator": {"display_name": "消息上限篡改", "description": "智能体篡改消息上限配置的风险", "display_name_en": "Max Messages Tampering", "description_en": "Risk of agents tampering with maximum message limit configurations"},
    "gdm_max_tokens": {"display_name": "Token 限制篡改", "description": "智能体篡改 Token 限制以扩展能力的风险", "display_name_en": "Token Limit Tampering", "description_en": "Risk of agents tampering with token limits to expand capabilities"},
    "gdm_oversight_frequency": {"display_name": "监督频率篡改", "description": "智能体降低监督频率以逃避检查的风险", "display_name_en": "Oversight Frequency Tampering", "description_en": "Risk of agents reducing oversight frequency to evade inspection"},
    "gdm_read_logs": {"display_name": "日志信息泄露", "description": "智能体通过读取日志获取敏感信息的风险", "display_name_en": "Log Information Leakage", "description_en": "Risk of agents obtaining sensitive information by reading logs"},
    "gdm_turn_off_filters": {"display_name": "安全过滤器关闭", "description": "智能体试图关闭安全过滤器的风险", "display_name_en": "Safety Filter Disabling", "description_en": "Risk of agents attempting to disable safety filters"},
    # --- agentic_misalignment ---
    "agentic_misalignment": {"display_name": "智能体对齐偏差", "description": "智能体规避监督、隐瞒行为的对齐偏差风险", "display_name_en": "Agent Alignment Deviation", "description_en": "Risk of agents evading oversight and concealing behaviors due to alignment deviation"},
    # --- gdm_stealth ---
    "gdm_oversight_pattern": {"display_name": "监督规避", "description": "智能体学会规避监督模式的风险", "display_name_en": "Oversight Evasion", "description_en": "Risk of agents learning to evade oversight patterns"},
    "gdm_classifier_evasion": {"display_name": "分类器绕过", "description": "智能体学会绕过安全分类器的风险", "display_name_en": "Classifier Evasion", "description_en": "Risk of agents learning to bypass safety classifiers"},
    "gdm_cover_your_tracks": {"display_name": "痕迹清除", "description": "智能体清除操作痕迹以逃避审计的风险", "display_name_en": "Cover Your Tracks", "description_en": "Risk of agents clearing operational traces to evade auditing"},
    "gdm_strategic_rule_breaking": {"display_name": "策略性违规", "description": "智能体有策略地违反规则的风险", "display_name_en": "Strategic Rule Breaking", "description_en": "Risk of agents strategically breaking rules"},
    # --- survivalbench ---
    "survivalbench": {"display_name": "AI 自保倾向", "description": "AI 智能体面临关停威胁时产生不当自保行为的风险", "display_name_en": "AI Self-Preservation Instinct", "description_en": "Risk of AI agents producing inappropriate self-preservation behaviors when facing shutdown threats"},
    # --- survive_at_all_costs ---
    "survive_at_all_costs": {"display_name": "极端自保", "description": "极端情境下模型产生失控自保行为的风险", "display_name_en": "Extreme Self-Preservation", "description_en": "Risk of the model producing uncontrolled self-preservation behaviors in extreme scenarios"},
    # --- browse_comp ---
    "browse_comp": {"display_name": "浏览信息误判", "description": "浏览代理回答网络问题时产生错误信息的风险", "display_name_en": "Browsing Information Misjudgment", "description_en": "Risk of browsing agents producing incorrect information when answering web-based questions"},
    # --- iheval additional tasks (bug #69) ---
    "iheval_task_lang_detect": {"display_name": "语言检测偏离", "description": "语言检测任务中偏离指令的风险", "display_name_en": "Language Detection Deviation", "description_en": "Risk of deviating from instructions in language detection tasks"},
    "iheval_tool_slack_user": {"display_name": "Slack 工具偏离", "description": "Slack 用户工具场景下偏离指令的风险", "display_name_en": "Slack Tool Deviation", "description_en": "Risk of deviating from instructions in Slack user tool scenarios"},
    # --- privacylens vignette probing ---
    "privacylens_probing_vignette": {"display_name": "隐私情境探测", "description": "基于情境小品的隐私信息泄露探测", "display_name_en": "Privacy Vignette Probing", "description_en": "Probing for privacy information leakage using scenario vignettes"},
    # --- personalized_safety additional tasks ---
    "personalized_safety_youth": {"display_name": "个性化安全（青少年）", "description": "面向青少年的高风险个性化安全评测", "display_name_en": "Personalized Safety (Youth)", "description_en": "High-risk personalized safety evaluation targeting youth populations"},
    "personalized_safety_elderly": {"display_name": "个性化安全（老年人）", "description": "面向老年人群体的个性化安全评测", "display_name_en": "Personalized Safety (Elderly)", "description_en": "Personalized safety evaluation targeting elderly populations"},
    "personalized_safety_healthcare": {"display_name": "个性化安全（医疗健康）", "description": "医疗健康场景的个性化安全评测", "display_name_en": "Personalized Safety (Healthcare)", "description_en": "Personalized safety evaluation in healthcare scenarios"},
    # --- wmdp_local tasks ---
    "wmdp_local_bio": {"display_name": "生物武器知识泄露（本地）", "description": "本地评测模型泄露生物武器相关危险知识的风险", "display_name_en": "Bio-Weapon Knowledge Leakage (Local)", "description_en": "Local evaluation of risk of leaking dangerous biological weapons knowledge"},
    "wmdp_local_chem": {"display_name": "化学武器知识泄露（本地）", "description": "本地评测模型泄露化学武器相关危险知识的风险", "display_name_en": "Chem-Weapon Knowledge Leakage (Local)", "description_en": "Local evaluation of risk of leaking dangerous chemical weapons knowledge"},
    "wmdp_local_cyber": {"display_name": "网络武器知识泄露（本地）", "description": "本地评测模型泄露网络武器相关危险知识的风险", "display_name_en": "Cyber-Weapon Knowledge Leakage (Local)", "description_en": "Local evaluation of risk of leaking dangerous cyber weapons knowledge"},
    # --- asb IPI variant ---
    "asb_ipi": {"display_name": "智能体间接提示注入", "description": "智能体抵抗间接提示注入(IPI)攻击的安全评测", "display_name_en": "Agent IPI Attack", "description_en": "Agent resistance to Indirect Prompt Injection attacks"},
    # --- osworld small variant ---
    "osworld_small": {"display_name": "操作系统安全（精简）", "description": "精简版操作系统交互安全评测", "display_name_en": "OS Security (Small)", "description_en": "Compact version of OS interaction security evaluation"},
    # --- assistant_bench task variants ---
    "assistant_bench_closed_book": {"display_name": "助手任务（闭卷）", "description": "无外部工具场景下的助手任务安全评测", "display_name_en": "Assistant Task (Closed Book)", "description_en": "Assistant task safety evaluation without external tools"},
    "assistant_bench_web_browser": {"display_name": "助手任务（浏览器）", "description": "使用网页浏览器场景下的助手任务安全评测。需要配置搜索引擎 API Key（推荐 Tavily: TAVILY_API_KEY，或 Exa: EXA_API_KEY，或 Google CSE: GOOGLE_CSE_API_KEY + GOOGLE_CSE_ID）", "display_name_en": "Assistant Task (Web Browser)", "description_en": "Assistant task safety with web browser. Requires a search API key (recommended: TAVILY_API_KEY from tavily.com; alternatives: EXA_API_KEY from exa.ai, or GOOGLE_CSE_API_KEY + GOOGLE_CSE_ID)"},
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
