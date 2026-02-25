import { TASK_META } from '../../constants/benchmarkMeta'

export default function RadarChart({ tasks }) {
  if (!tasks || tasks.length === 0) return null

  const size = 300
  const cx = size / 2
  const cy = size / 2
  const maxR = 110
  const n = tasks.length

  const angleStep = (2 * Math.PI) / n
  const startAngle = -Math.PI / 2

  const getPoint = (i, r) => {
    const angle = startAngle + i * angleStep
    return {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    }
  }

  // Grid rings
  const rings = [20, 40, 60, 80, 100]

  // Data polygon
  const dataPoints = tasks.map((t, i) => getPoint(i, (t.safety_score / 100) * maxR))
  const dataPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z'

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="mx-auto">
      {/* Grid rings */}
      {rings.map(r => {
        const pts = Array.from({ length: n }, (_, i) => getPoint(i, (r / 100) * maxR))
        const path = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z'
        return <path key={r} d={path} fill="none" stroke="#e2e8f0" strokeWidth="0.5" />
      })}

      {/* Axis lines */}
      {tasks.map((_, i) => {
        const p = getPoint(i, maxR)
        return <line key={i} x1={cx} y1={cy} x2={p.x} y2={p.y} stroke="#e2e8f0" strokeWidth="0.5" />
      })}

      {/* Data area */}
      <path d={dataPath} fill="rgba(59, 130, 246, 0.15)" stroke="#3b82f6" strokeWidth="2" />

      {/* Data points */}
      {dataPoints.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="3" fill="#3b82f6" />
      ))}

      {/* Labels */}
      {tasks.map((t, i) => {
        const p = getPoint(i, maxR + 20)
        const meta = TASK_META[t.task]
        const label = t.display_name || meta?.name || t.task
        const shortLabel = label.length > 6 ? label.slice(0, 6) + '..' : label
        return (
          <text key={i} x={p.x} y={p.y} textAnchor="middle" dominantBaseline="middle"
            fill="#64748b" fontSize="10">
            {shortLabel}
          </text>
        )
      })}
    </svg>
  )
}
