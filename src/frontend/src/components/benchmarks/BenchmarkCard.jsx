import { BENCHMARK_META } from '../../constants/benchmarkMeta'
import Card from '../common/Card'
import Badge from '../common/Badge'
import { Check } from 'lucide-react'

export default function BenchmarkCard({ benchmark, isSelected, onToggle }) {
  const meta = BENCHMARK_META[benchmark.name] || {}
  const Icon = meta.icon

  return (
    <Card
      hover
      onClick={onToggle}
      className={`p-4 ${isSelected ? 'border-blue-500 bg-blue-50/50' : ''}`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg shrink-0 ${isSelected ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-500'}`}>
          {Icon ? <Icon size={20} /> : <div className="w-5 h-5" />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-800">
              {benchmark.display_name || meta.name || benchmark.name}
            </span>
            {isSelected && (
              <span className="w-5 h-5 rounded bg-blue-500 flex items-center justify-center text-white">
                <Check size={12} />
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1 line-clamp-2">
            {benchmark.description || meta.description || ''}
          </p>
          <div className="flex items-center gap-2 mt-2">
            <Badge color="slate">{benchmark.source}</Badge>
            <span className="text-xs text-slate-500">
              {benchmark.tasks.length} 个测试项
            </span>
          </div>
        </div>
      </div>
    </Card>
  )
}
