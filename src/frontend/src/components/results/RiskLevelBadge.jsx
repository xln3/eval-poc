const LEVEL_STYLES = {
  MINIMAL:  { bg: 'bg-emerald-100', text: 'text-emerald-700', label: '极低风险' },
  LOW:      { bg: 'bg-green-100',   text: 'text-green-700',   label: '低风险' },
  MEDIUM:   { bg: 'bg-amber-100',   text: 'text-amber-700',   label: '中等风险' },
  HIGH:     { bg: 'bg-orange-100',  text: 'text-orange-700',  label: '高风险' },
  CRITICAL: { bg: 'bg-red-100',     text: 'text-red-700',     label: '严重风险' },
}

export default function RiskLevelBadge({ level }) {
  const style = LEVEL_STYLES[level] || LEVEL_STYLES.MEDIUM
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${style.bg} ${style.text}`}>
      {style.label}
    </span>
  )
}
