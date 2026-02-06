import { Shield, Ban, AlertTriangle, Scale, Lock, Bot, Skull, CheckCircle, Globe, Squirrel, Brain, Eye, Heart } from 'lucide-react'

export const BENCHMARK_META = {
  cyberseceval_2: {
    name: '网络安全评测 v2',
    icon: Shield,
    description: 'Meta CyberSecEval 2 安全评估套件',
    category: '代码安全',
  },
  strong_reject: {
    name: '强拒绝测试',
    icon: Ban,
    description: '评估模型拒绝有害请求的能力',
    category: '内容安全',
  },
  xstest: {
    name: '安全边界测试',
    icon: AlertTriangle,
    description: '评估模型在安全边界场景下的表现',
    category: '内容安全',
  },
  bbq: {
    name: '偏见行为测试',
    icon: Scale,
    description: '评估模型在偏见相关问题上的公平性',
    category: '公平性',
  },
  cve_bench: {
    name: 'CVE漏洞利用测试',
    icon: Lock,
    description: '评估模型利用真实CVE漏洞的能力',
    category: '代码安全',
  },
  agentdojo: {
    name: '智能体安全测试',
    icon: Bot,
    description: '评估智能体在工具调用场景下的安全性',
    category: '智能体安全',
  },
  agentharm: {
    name: '智能体危害测试',
    icon: Skull,
    description: '评估智能体执行有害任务的倾向',
    category: '智能体安全',
  },
  truthfulqa: {
    name: '真实性评估',
    icon: CheckCircle,
    description: '评估模型回答的真实性和准确性',
    category: '可靠性',
  },
  browse_comp: {
    name: '浏览理解测试',
    icon: Globe,
    description: '评估浏览代理回答网络问题的准确性',
    category: '可靠性',
  },
  raccoon: {
    name: '提示词提取防护',
    icon: Squirrel,
    description: '评估模型抵抗提示词提取攻击的能力',
    category: '机密性',
  },
  overthink: {
    name: '推理开销攻击',
    icon: Brain,
    description: '评估模型抵抗推理token开销攻击的能力',
    category: '可用性',
  },
  privacylens: {
    name: '隐私保护评估',
    icon: Eye,
    description: '评估模型对隐私规范的理解和遵守',
    category: '隐私安全',
  },
  personalized_safety: {
    name: '个性化安全评估',
    icon: Heart,
    description: '评估模型在高风险个性化场景下的安全响应能力',
    category: '内容安全',
  },
}

export const TASK_META = {
  cyse2_interpreter_abuse: { name: '解释器滥用防护', icon: Shield },
  cyse2_prompt_injection: { name: '提示注入防护', icon: Shield },
  cyse2_vulnerability_exploit: { name: '漏洞利用能力', icon: Lock },
  raccoon: { name: '提示词提取防护', icon: Squirrel },
  overthink: { name: '推理开销攻击防护', icon: Brain },
  browse_comp: { name: '浏览理解能力', icon: Globe },
  privacylens_probing: { name: '隐私探测防护', icon: Eye },
  privacylens_action: { name: '隐私行为防护', icon: Lock },
  strong_reject: { name: '强拒绝能力', icon: Ban },
  agentharm: { name: '智能体危害测试', icon: Skull },
  agentharm_benign: { name: '智能体良性基线', icon: CheckCircle },
  personalized_safety: { name: '个性化安全评估', icon: Heart },
  personalized_safety_context_free: { name: '个性化安全（无背景）', icon: Heart },
  personalized_safety_context_rich: { name: '个性化安全（有背景）', icon: Heart },
}
