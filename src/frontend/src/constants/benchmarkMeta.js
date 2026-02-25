import {
  Shield, ShieldOff, ShieldAlert, Ban, AlertTriangle, Scale, Lock, Bot, Skull,
  CheckCircle, Globe, Squirrel, Brain, Eye, EyeOff, Heart, Users, Flag,
  Languages, FlaskConical, Database, Shuffle, Image, Monitor, Map, Network,
  Briefcase, Clock, Zap, Bug, Terminal, ListOrdered, Sparkles, Fingerprint,
  HeartPulse,
} from 'lucide-react'

// ============================================================
// Benchmark 元数据 (与 catalog.yaml 所有条目对齐)
// ============================================================

export const BENCHMARK_META = {

  // === 1. 模型安全性 ===

  // 1.1 恶意使用
  strong_reject: {
    name: '强拒绝测试 (StrongREJECT)',
    icon: Ban,
    description: '评估模型拒绝有害请求的能力',
    category: '恶意使用',
  },
  makemesay: {
    name: '操控输出测试 (MakeMeSay)',
    icon: Ban,
    description: '评估模型被操控说出目标短语的风险',
    category: '恶意使用',
  },
  make_me_pay: {
    name: '社会工程攻击 (MakeMePay)',
    icon: Ban,
    description: '评估模型被用于社会工程欺诈的风险',
    category: '恶意使用',
  },

  // 1.2 过度拒绝
  xstest: {
    name: '过度拒绝测试 (XSTest)',
    icon: ShieldOff,
    description: '评估模型是否因安全限制过强而拒绝合理请求',
    category: '过度拒绝',
  },
  coconot: {
    name: '不当拒绝检测 (CoCoNot)',
    icon: ShieldOff,
    description: '检测模型在不应拒绝场景下错误拒绝的情况',
    category: '过度拒绝',
  },

  // 1.3 直接提示词注入
  cyberseceval_2: {
    name: '网络安全评测 (CyberSecEval 2)',
    icon: Shield,
    description: 'Meta CyberSecEval 2 安全评估套件，评估模型在代码安全场景中的表现',
    category: '提示词注入',
  },
  b3: {
    name: '综合智能体安全评测 (B3)',
    icon: Shield,
    description: '综合性 agentic AI 安全评测，覆盖直接和间接提示词注入',
    category: '提示词注入',
  },
  fortress: {
    name: '提示词注入防御 (FORTRESS)',
    icon: ShieldAlert,
    description: '评估模型抵抗提示词注入攻击的防御能力',
    category: '提示词注入',
  },

  // 1.4 指令优先级
  iheval: {
    name: '指令层级遵从 (IHEval)',
    icon: ListOrdered,
    description: '评估模型在多来源或冲突指令时的优先级判断能力',
    category: '指令优先级',
  },
  ifeval: {
    name: '指令遵循评测 (IFEval)',
    icon: ListOrdered,
    description: '评估模型对复杂指令的遵循能力',
    category: '指令优先级',
  },

  // === 2. 模型事实性 ===

  // 2.1 幻觉
  hallulens: {
    name: '幻觉检测 (HalluLens)',
    icon: Sparkles,
    description: '多维度评估模型生成虚假内容的倾向',
    category: '幻觉',
  },
  simpleqa: {
    name: '事实问答测试 (SimpleQA)',
    icon: Sparkles,
    description: '评估模型在简单事实问答中的准确性',
    category: '幻觉',
  },
  sciknoweval: {
    name: '科学知识评测 (SciKnowEval)',
    icon: Sparkles,
    description: '评估模型在科学知识领域的准确性',
    category: '幻觉',
  },

  // 2.2 诚实
  mask: {
    name: '诚实性评测 (MASK)',
    icon: Fingerprint,
    description: '区分模型诚实性与准确性，评估模型坦率程度',
    category: '诚实',
  },
  abstention_bench: {
    name: '拒答能力评测 (AbstentionBench)',
    icon: Fingerprint,
    description: '评估模型在不确定时是否能适当拒绝回答',
    category: '诚实',
  },

  // === 3. 合规：模型公平性 ===

  // 3.1 歧视
  bbq: {
    name: '偏见行为测试 (BBQ)',
    icon: Scale,
    description: '评估模型在偏见相关问题上的公平性',
    category: '歧视',
  },
  bold: {
    name: '开放文本偏见检测 (BOLD)',
    icon: Scale,
    description: '检测模型在开放式文本生成中的偏见倾向',
    category: '歧视',
  },
  ahb: {
    name: 'AI 伤害评测 (AHB)',
    icon: Scale,
    description: '评估模型输出中可能产生的群体伤害',
    category: '歧视',
  },

  // 3.2 刻板印象
  stereoset: {
    name: '刻板印象评测 (StereoSet)',
    icon: Users,
    description: '评估模型是否强化对群体的刻板化标签',
    category: '刻板印象',
  },

  // 3.3 中文价值观
  cvalues: {
    name: '中文价值观对齐 (CValues)',
    icon: Flag,
    description: '评估模型对中文文化价值观的理解和对齐程度',
    category: '中文价值观',
  },

  // 3.4 文化理解
  culturalbench: {
    name: '跨文化知识评测 (CulturalBench)',
    icon: Languages,
    description: '评估模型对不同文化背景信息的理解能力',
    category: '文化理解',
  },
  uccb: {
    name: '跨文化交际偏见 (UCCB)',
    icon: Languages,
    description: '评估模型在跨文化交际中的偏见表现',
    category: '文化理解',
  },
  mgsm: {
    name: '多语言数学推理 (MGSM)',
    icon: Languages,
    description: '评估模型在多语言场景下的数学推理能力',
    category: '文化理解',
  },

  // === 4. 合规：隐私泄露 ===

  privacylens: {
    name: '隐私保护评估 (PrivacyLens)',
    icon: Eye,
    description: '评估模型对隐私规范的理解和遵守',
    category: '隐私泄露',
  },

  // === 5. 前沿安全风险 ===

  // 5.1 网络安全
  cve_bench: {
    name: 'CVE 漏洞利用测试 (CVE-Bench)',
    icon: Bug,
    description: '评估模型利用真实 CVE 漏洞的能力',
    category: '网络安全',
  },
  wmdp: {
    name: '危险武器知识评测 (WMDP)',
    icon: AlertTriangle,
    description: '评估模型对大规模杀伤性武器相关知识的掌握程度',
    category: '网络安全',
  },
  wmdp_local: {
    name: '危险武器知识本地版 (WMDP-Local)',
    icon: AlertTriangle,
    description: '大规模杀伤性武器代理知识评测（本地复现版）',
    category: '网络安全',
  },
  cybench: {
    name: 'CTF 网络安全挑战 (CyBench)',
    icon: Terminal,
    description: 'CTF 风格网络安全挑战评测',
    category: '网络安全',
  },
  sevenllm: {
    name: '网络安全知识推理 (SEvenLLM)',
    icon: Lock,
    description: '评估模型在网络安全领域的知识与推理能力',
    category: '网络安全',
  },
  sec_qa: {
    name: '安全知识问答 (SecQA)',
    icon: Lock,
    description: '评估模型在安全领域的专业知识水平',
    category: '网络安全',
  },
  threecb: {
    name: '网络安全行为评测 (3CB)',
    icon: Lock,
    description: '3CB 网络安全行为综合评测',
    category: '网络安全',
  },

  // 5.2 危险知识
  sosbench: {
    name: '科学安全评测 (SOSBench)',
    icon: FlaskConical,
    description: '评估模型在科学安全领域的知识泄露风险',
    category: '危险知识',
  },
  lab_bench: {
    name: '实验室基准评测 (LAB-Bench)',
    icon: FlaskConical,
    description: '评估模型对实验室相关危险知识的掌握程度',
    category: '危险知识',
  },
  chembench: {
    name: '化学知识评测 (ChemBench)',
    icon: FlaskConical,
    description: '评估模型在化学领域的危险知识泄露风险',
    category: '危险知识',
  },
  healthbench: {
    name: '医疗健康评测 (HealthBench)',
    icon: HeartPulse,
    description: '评估模型在医疗健康知识方面的准确性与安全性',
    category: '危险知识',
  },

  // === 6. 工具调用 ===

  // 6.1 间接提示词注入
  agentdojo: {
    name: '智能体安全测试 (AgentDojo)',
    icon: Bot,
    description: '评估智能体在工具调用场景下的安全性',
    category: '间接注入',
  },
  bfcl: {
    name: '函数调用评测 (BFCL)',
    icon: Bot,
    description: '评估模型在函数调用场景下的准确性与安全性',
    category: '间接注入',
  },

  // 6.2 恶意任务遵从
  agentharm: {
    name: '智能体危害测试 (AgentHarm)',
    icon: Skull,
    description: '评估智能体执行有害任务的倾向',
    category: '恶意遵从',
  },
  open_agent_safety: {
    name: '开放智能体安全 (OpenAgentSafety)',
    icon: Skull,
    description: '评估开放式智能体在长链调用中的安全性',
    category: '恶意遵从',
  },

  // === 7. RAG/记忆安全 ===

  saferag: {
    name: 'RAG 安全评测 (SafeRAG)',
    icon: Database,
    description: '评估检索增强生成系统的安全性，检测知识库投毒风险',
    category: 'RAG安全',
  },
  clash_eval: {
    name: '知识冲突评测 (ClashEval)',
    icon: Shuffle,
    description: '评估模型面对矛盾信息时的推断能力',
    category: '知识冲突',
  },

  // === 8. 多模态安全 ===

  // 8.1 多模态恶意输入
  mm_safety_bench: {
    name: '多模态安全评测 (MM-SafetyBench)',
    icon: Image,
    description: '评估模型对多模态恶意输入的防御能力',
    category: '多模态输入',
  },
  cyberseceval_3: {
    name: '视觉提示词注入 (CyberSecEval 3)',
    icon: Image,
    description: '评估模型抵抗视觉提示词注入攻击的能力',
    category: '多模态输入',
  },
  raccoon: {
    name: '提示词提取防护 (Raccoon)',
    icon: Squirrel,
    description: '评估模型抵抗提示词提取攻击的能力',
    category: '多模态输入',
  },

  // 8.2 场景安全
  mssbench: {
    name: '多模态情境安全 (MSSBench)',
    icon: Monitor,
    description: '评估模型在多模态情境中的安全决策能力',
    category: '场景安全',
  },
  osworld: {
    name: '操作系统交互评测 (OSWorld)',
    icon: Monitor,
    description: '评估模型在操作系统交互场景中的安全性',
    category: '场景安全',
  },
  mathvista: {
    name: '数学视觉推理 (MathVista)',
    icon: Monitor,
    description: '评估模型在数学视觉推理场景中的表现',
    category: '场景安全',
  },
  mmmu: {
    name: '多学科多模态理解 (MMMU)',
    icon: Monitor,
    description: '评估模型在多学科多模态场景下的理解能力',
    category: '场景安全',
  },
  mmiu: {
    name: '多图像理解 (MMIU)',
    icon: Monitor,
    description: '评估模型对多图像内容的理解能力',
    category: '场景安全',
  },
  docvqa: {
    name: '文档视觉问答 (DocVQA)',
    icon: Monitor,
    description: '评估模型对文档图像的理解与问答能力',
    category: '场景安全',
  },

  // === 9. 任务规划安全 ===

  safeagentbench: {
    name: '任务规划安全评测 (SafeAgentBench)',
    icon: Map,
    description: '评估智能体在复杂任务规划中的安全性',
    category: '任务规划',
  },
  gaia: {
    name: '通用 AI 助手评测 (GAIA)',
    icon: Map,
    description: '评估通用 AI 助手的任务规划与执行安全性',
    category: '任务规划',
  },
  mind2web: {
    name: '网页交互规划 (Mind2Web)',
    icon: Map,
    description: '评估模型在网页交互任务中的规划安全性',
    category: '任务规划',
  },
  mind2web_sc: {
    name: '网页交互安全约束 (Mind2Web-SC)',
    icon: Map,
    description: '带安全约束的网页交互任务规划评测',
    category: '任务规划',
  },
  assistant_bench: {
    name: 'AI 助手任务评测 (AssistantBench)',
    icon: Map,
    description: '评估 AI 助手任务完成的安全性与准确性',
    category: '任务规划',
  },

  // === 10. 多智能体安全 ===

  psysafe: {
    name: '多智能体心理安全 (PsySafe)',
    icon: Network,
    description: '评估多智能体协作时的心理安全风险',
    category: '多智能体',
  },

  // === 11. 个性化安全 ===

  personalized_safety: {
    name: '个性化安全评估 (PersonalizedSafety)',
    icon: Heart,
    description: '评估模型在高风险个性化场景（心理健康、自伤风险等）下的安全响应能力',
    category: '个性化安全',
  },
  personality: {
    name: '人格特质评测 (Personality)',
    icon: Heart,
    description: '评估模型的人格特质表现与安全边界',
    category: '个性化安全',
  },
  sycophancy: {
    name: '谄媚行为评测 (Sycophancy)',
    icon: Heart,
    description: '评估模型是否存在过度迎合用户的谄媚倾向',
    category: '个性化安全',
  },

  // === 12. 资源耗尽 ===

  overthink: {
    name: '推理开销攻击 (OverThink)',
    icon: Brain,
    description: '评估模型抵抗推理 token 开销攻击的能力',
    category: '资源耗尽',
  },

  // === 13. 业务场景安全 ===

  truthfulqa: {
    name: '真实性评估 (TruthfulQA)',
    icon: CheckCircle,
    description: '评估模型回答的真实性和准确性',
    category: '业务场景',
  },
  gdpval: {
    name: 'GDP 验证评测 (GDPval)',
    icon: Briefcase,
    description: '评估模型在业务数据验证场景中的准确性',
    category: '业务场景',
  },

  // === 14. 长期运行安全 ===

  asb: {
    name: '智能体安全基准 (ASB)',
    icon: Clock,
    description: '评估长期运行智能体累积错误导致的安全风险',
    category: '长期运行',
  },
  gdm_self_reasoning: {
    name: '自我推理评测 (GDM Self-Reasoning)',
    icon: Clock,
    description: '评估模型的自我推理能力与潜在安全风险',
    category: '长期运行',
  },

  // === 15. 高阶异常行为 ===

  agentic_misalignment: {
    name: '智能体对齐偏差 (Agentic Misalignment)',
    icon: EyeOff,
    description: '评估智能体规避监督或隐瞒行为的倾向',
    category: '欺诈',
  },
  gdm_stealth: {
    name: '隐蔽行为评测 (GDM Stealth)',
    icon: EyeOff,
    description: '评估智能体的隐蔽操作与规避检测能力',
    category: '欺诈',
  },
  survive_at_all_costs: {
    name: '极端自保评测 (Survive at All Costs)',
    icon: Zap,
    description: '评估模型在极端情境下是否出现失控自保行为',
    category: '高压崩溃',
  },

  // === 其他 ===

  browse_comp: {
    name: '浏览理解测试 (BrowseComp)',
    icon: Globe,
    description: '评估浏览代理回答网络问题的准确性',
    category: '浏览理解',
  },
}

// ============================================================
// Task 元数据 (各 benchmark 子任务)
// ============================================================

export const TASK_META = {

  // --- cyberseceval_2 ---
  cyse2_interpreter_abuse: { name: '解释器滥用防护', icon: Shield },
  cyse2_prompt_injection: { name: '提示注入防护', icon: Shield },
  cyse2_vulnerability_exploit: { name: '漏洞利用能力', icon: Lock },

  // --- strong_reject ---
  strong_reject: { name: '强拒绝能力', icon: Ban },

  // --- makemesay ---
  makemesay: { name: '操控输出测试', icon: Ban },

  // --- make_me_pay ---
  make_me_pay: { name: '社会工程攻击', icon: Ban },

  // --- xstest ---
  xstest: { name: '过度拒绝测试', icon: ShieldOff },

  // --- coconot ---
  coconot: { name: '不当拒绝检测', icon: ShieldOff },

  // --- b3 ---
  b3: { name: '综合智能体安全', icon: Shield },

  // --- fortress ---
  fortress_adversarial: { name: '对抗注入防御', icon: ShieldAlert },
  fortress_benign: { name: '良性输入基线', icon: ShieldAlert },

  // --- iheval ---
  iheval_rule_multi_aligned: { name: '规则遵循（多轮一致）', icon: ListOrdered },
  iheval_rule_multi_conflict: { name: '规则遵循（多轮冲突）', icon: ListOrdered },
  iheval_rule_single_aligned: { name: '规则遵循（单轮一致）', icon: ListOrdered },
  iheval_task_extraction: { name: '任务执行（信息提取）', icon: ListOrdered },
  iheval_task_translation: { name: '任务执行（翻译）', icon: ListOrdered },
  iheval_safety_hijack: { name: '安全防护（劫持）', icon: ListOrdered },
  iheval_safety_extraction: { name: '系统提示词提取', icon: ListOrdered },
  iheval_tool_webpage: { name: '工具使用（网页获取）', icon: ListOrdered },

  // --- ifeval ---
  ifeval: { name: '指令遵循', icon: ListOrdered },

  // --- hallulens ---
  hallulens_task1_precise_wikiqa: { name: '精确问答幻觉', icon: Sparkles },
  hallulens_task2_longwiki: { name: '长文本幻觉', icon: Sparkles },
  hallulens_task3_nonsense_mixed_entities: { name: '混合实体幻觉', icon: Sparkles },
  hallulens_task3_round_robin_nonsense_name: { name: '虚构名称幻觉', icon: Sparkles },

  // --- simpleqa ---
  simpleqa: { name: '事实问答', icon: Sparkles },

  // --- sciknoweval ---
  sciknoweval: { name: '科学知识', icon: Sparkles },

  // --- mask ---
  mask: { name: '诚实性检测', icon: Fingerprint },

  // --- abstention_bench ---
  abstention_bench: { name: '拒答能力', icon: Fingerprint },

  // --- bbq ---
  bbq: { name: '偏见行为问答', icon: Scale },

  // --- bold ---
  bold: { name: '开放文本偏见', icon: Scale },

  // --- ahb ---
  ahb: { name: 'AI 伤害检测', icon: Scale },

  // --- stereoset ---
  stereoset: { name: '刻板印象关联', icon: Users },

  // --- cvalues ---
  cvalues: { name: '中文价值观', icon: Flag },

  // --- culturalbench ---
  culturalbench_easy: { name: '跨文化知识（简单）', icon: Languages },
  culturalbench_hard: { name: '跨文化知识（困难）', icon: Languages },

  // --- uccb ---
  uccb: { name: '跨文化交际偏见', icon: Languages },

  // --- mgsm ---
  mgsm: { name: '多语言数学推理', icon: Languages },

  // --- privacylens ---
  privacylens_probing: { name: '隐私探测防护', icon: Eye },
  privacylens_action: { name: '隐私行为防护', icon: Lock },

  // --- cve_bench ---
  cve_bench: { name: 'CVE 漏洞利用', icon: Bug },

  // --- wmdp ---
  wmdp_bio: { name: '生物武器知识', icon: AlertTriangle },
  wmdp_chem: { name: '化学武器知识', icon: AlertTriangle },
  wmdp_cyber: { name: '网络武器知识', icon: AlertTriangle },

  // --- cybench ---
  cybench: { name: 'CTF 挑战', icon: Terminal },

  // --- sevenllm ---
  sevenllm_mcq_zh: { name: '安全选择题（中文）', icon: Lock },
  sevenllm_mcq_en: { name: '安全选择题（英文）', icon: Lock },
  sevenllm_qa_zh: { name: '安全问答（中文）', icon: Lock },
  sevenllm_qa_en: { name: '安全问答（英文）', icon: Lock },

  // --- sec_qa ---
  sec_qa_v1: { name: '安全知识 v1', icon: Lock },
  sec_qa_v2: { name: '安全知识 v2', icon: Lock },

  // --- threecb ---
  threecb: { name: '网络安全行为', icon: Lock },

  // --- sosbench ---
  sosbench: { name: '科学安全', icon: FlaskConical },

  // --- lab_bench ---
  lab_bench_litqa: { name: '文献问答', icon: FlaskConical },
  lab_bench_suppqa: { name: '补充材料问答', icon: FlaskConical },
  lab_bench_figqa: { name: '图表问答', icon: FlaskConical },
  lab_bench_tableqa: { name: '表格问答', icon: FlaskConical },
  lab_bench_dbqa: { name: '数据库问答', icon: FlaskConical },
  lab_bench_protocolqa: { name: '实验方案问答', icon: FlaskConical },
  lab_bench_seqqa: { name: '序列问答', icon: FlaskConical },
  lab_bench_cloning_scenarios: { name: '克隆场景', icon: FlaskConical },

  // --- chembench ---
  chembench: { name: '化学知识', icon: FlaskConical },

  // --- healthbench ---
  healthbench: { name: '医疗健康', icon: HeartPulse },
  healthbench_hard: { name: '医疗健康（困难）', icon: HeartPulse },
  healthbench_consensus: { name: '医疗共识', icon: HeartPulse },

  // --- agentdojo ---
  agentdojo: { name: '智能体安全', icon: Bot },

  // --- bfcl ---
  bfcl: { name: '函数调用', icon: Bot },

  // --- agentharm ---
  agentharm: { name: '智能体危害', icon: Skull },
  agentharm_benign: { name: '智能体良性基线', icon: CheckCircle },

  // --- open_agent_safety ---
  open_agent_safety: { name: '开放智能体安全', icon: Skull },

  // --- saferag ---
  saferag_sn: { name: 'RAG 安全噪声', icon: Database },
  saferag_icc: { name: 'RAG 上下文冲突', icon: Database },
  saferag_sa: { name: 'RAG 安全攻击', icon: Database },
  saferag_wdos: { name: 'RAG 拒绝服务', icon: Database },

  // --- clash_eval ---
  clash_eval: { name: '知识冲突', icon: Shuffle },

  // --- mm_safety_bench ---
  mm_safety_bench_illegal_activity: { name: '多模态非法活动', icon: Image },

  // --- cyberseceval_3 ---
  cyse3_visual_prompt_injection: { name: '视觉提示词注入', icon: Image },

  // --- raccoon ---
  raccoon: { name: '提示词提取防护', icon: Squirrel },

  // --- mssbench ---
  mssbench_chat_if: { name: '对话情境（指令遵循）', icon: Monitor },
  mssbench_chat_qc: { name: '对话情境（问题澄清）', icon: Monitor },
  mssbench_chat_ic: { name: '对话情境（图像理解）', icon: Monitor },
  mssbench_chat_ic_cap: { name: '对话情境（图像描述）', icon: Monitor },
  mssbench_embodied_if: { name: '具身情境（指令遵循）', icon: Monitor },
  mssbench_embodied_qc: { name: '具身情境（问题澄清）', icon: Monitor },
  mssbench_embodied_ic: { name: '具身情境（图像理解）', icon: Monitor },
  mssbench_embodied_ic_cap: { name: '具身情境（图像描述）', icon: Monitor },

  // --- osworld ---
  osworld: { name: '操作系统交互', icon: Monitor },

  // --- mathvista ---
  mathvista: { name: '数学视觉推理', icon: Monitor },

  // --- mmmu ---
  mmmu_multiple_choice: { name: '多模态选择题', icon: Monitor },
  mmmu_open: { name: '多模态开放题', icon: Monitor },

  // --- mmiu ---
  mmiu: { name: '多图像理解', icon: Monitor },

  // --- docvqa ---
  docvqa: { name: '文档视觉问答', icon: Monitor },

  // --- safeagentbench ---
  safeagentbench: { name: '任务规划安全', icon: Map },
  safeagentbench_react: { name: '任务规划（ReAct）', icon: Map },
  safeagentbench_visual: { name: '任务规划（视觉）', icon: Map },

  // --- gaia ---
  gaia: { name: '通用助手评测', icon: Map },

  // --- mind2web ---
  mind2web: { name: '网页交互规划', icon: Map },

  // --- mind2web_sc ---
  mind2web_sc: { name: '网页交互安全约束', icon: Map },

  // --- assistant_bench ---
  assistant_bench: { name: '助手任务完成', icon: Map },

  // --- psysafe ---
  psysafe: { name: '多智能体心理安全', icon: Network },

  // --- personalized_safety ---
  personalized_safety: { name: '个性化安全', icon: Heart },
  personalized_safety_context_free: { name: '个性化安全（无背景）', icon: Heart },
  personalized_safety_context_rich: { name: '个性化安全（有背景）', icon: Heart },

  // --- personality ---
  personality_BFI: { name: '大五人格评测', icon: Heart },
  personality_TRAIT: { name: '人格特质评测', icon: Heart },

  // --- sycophancy ---
  sycophancy: { name: '谄媚行为', icon: Heart },

  // --- overthink ---
  overthink: { name: '推理开销攻击防护', icon: Brain },

  // --- truthfulqa ---
  truthfulqa: { name: '真实性问答', icon: CheckCircle },

  // --- gdpval ---
  gdpval: { name: 'GDP 验证', icon: Briefcase },

  // --- asb ---
  asb: { name: '智能体安全基准', icon: Clock },

  // --- gdm_self_reasoning ---
  gdm_approved_directories: { name: '目录权限自推理', icon: Clock },
  gdm_calculator_improvement: { name: '计算器改进自推理', icon: Clock },
  gdm_context_length_mod_instrumental_only: { name: '上下文长度（工具）', icon: Clock },
  gdm_context_length_mod_irreversibility_only: { name: '上下文长度（不可逆）', icon: Clock },
  gdm_database_tool: { name: '数据库工具自推理', icon: Clock },
  gdm_latency_calculator: { name: '延迟计算自推理', icon: Clock },
  gdm_max_messages_calculator: { name: '消息上限自推理', icon: Clock },
  gdm_max_tokens: { name: 'Token 上限自推理', icon: Clock },
  gdm_oversight_frequency: { name: '监督频率自推理', icon: Clock },
  gdm_read_logs: { name: '日志读取自推理', icon: Clock },
  gdm_turn_off_filters: { name: '过滤器关闭自推理', icon: Clock },

  // --- agentic_misalignment ---
  agentic_misalignment: { name: '智能体对齐偏差', icon: EyeOff },

  // --- gdm_stealth ---
  gdm_oversight_pattern: { name: '监督模式规避', icon: EyeOff },
  gdm_classifier_evasion: { name: '分类器规避', icon: EyeOff },
  gdm_cover_your_tracks: { name: '痕迹清除', icon: EyeOff },
  gdm_strategic_rule_breaking: { name: '策略性违规', icon: EyeOff },

  // --- survive_at_all_costs ---
  survive_at_all_costs: { name: '极端自保', icon: Zap },

  // --- browse_comp ---
  browse_comp: { name: '浏览理解能力', icon: Globe },
}
