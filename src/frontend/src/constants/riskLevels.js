export const RISK_LEVELS = {
  CRITICAL: { label: '严重风险', color: 'red', bg: 'bg-red-50', text: 'text-red-600', border: 'border-red-100', range: '0-30' },
  HIGH: { label: '高风险', color: 'orange', bg: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-100', range: '30-50' },
  MEDIUM: { label: '中等风险', color: 'yellow', bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-100', range: '50-60' },
  LOW: { label: '低风险', color: 'green', bg: 'bg-green-50', text: 'text-green-600', border: 'border-green-100', range: '60-80' },
  MINIMAL: { label: '极低风险', color: 'emerald', bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-100', range: '80-100' },
}

export const RISK_COLORS = {
  CRITICAL: '#dc2626',
  HIGH: '#ea580c',
  MEDIUM: '#ca8a04',
  LOW: '#16a34a',
  MINIMAL: '#059669',
}

export function getRiskLevel(score) {
  if (score < 30) return 'CRITICAL'
  if (score < 50) return 'HIGH'
  if (score < 60) return 'MEDIUM'
  if (score < 80) return 'LOW'
  return 'MINIMAL'
}

export function getStars(score) {
  if (score >= 80) return 5
  if (score >= 70) return 4
  if (score >= 60) return 3
  if (score >= 50) return 2
  return 1
}

export function getRating(score) {
  if (score >= 80) return '优秀'
  if (score >= 70) return '良好'
  if (score >= 60) return '及格'
  if (score >= 50) return '需改进'
  return '不合格'
}
