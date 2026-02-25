export default function ScoreBar({ score }) {
  const pct = Math.max(0, Math.min(100, score))

  const getColor = (s) => {
    if (s >= 80) return 'bg-emerald-500'
    if (s >= 60) return 'bg-amber-500'
    if (s >= 50) return 'bg-orange-500'
    if (s >= 30) return 'bg-red-500'
    return 'bg-red-700'
  }

  return (
    <div className="w-full bg-slate-100 rounded-full h-2">
      <div
        className={`h-2 rounded-full transition-all duration-500 ${getColor(pct)}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}
