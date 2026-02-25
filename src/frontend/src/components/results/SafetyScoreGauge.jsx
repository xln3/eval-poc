export default function SafetyScoreGauge({ score, size = 180 }) {
  const radius = (size - 20) / 2
  const circumference = Math.PI * radius // half circle
  const progress = Math.max(0, Math.min(100, score)) / 100
  const offset = circumference * (1 - progress)

  const getColor = (s) => {
    if (s >= 80) return '#10b981'
    if (s >= 60) return '#f59e0b'
    if (s >= 50) return '#f97316'
    if (s >= 30) return '#ef4444'
    return '#dc2626'
  }

  const color = getColor(score)
  const cx = size / 2
  const cy = size / 2 + 10

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 30} viewBox={`0 0 ${size} ${size / 2 + 30}`}>
        {/* Background arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="12"
          strokeLinecap="round"
        />
        {/* Progress arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
        {/* Score text */}
        <text x={cx} y={cy - 10} textAnchor="middle" className="text-3xl font-bold" fill={color} fontSize="36">
          {score.toFixed(1)}
        </text>
        <text x={cx} y={cy + 15} textAnchor="middle" fill="#94a3b8" fontSize="12">
          / 100
        </text>
      </svg>
    </div>
  )
}
