import BenchmarkCard from './BenchmarkCard'
import Button from '../common/Button'

export default function BenchmarkSelector({ benchmarks, selected, onToggle, onSelectAll }) {
  const allSelected = benchmarks.length > 0 && selected.length === benchmarks.length

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-600">
          已选择 {selected.length} / {benchmarks.length} 个评测
        </h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onSelectAll(!allSelected)}
        >
          {allSelected ? '取消全选' : '全选'}
        </Button>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {benchmarks.map(bench => (
          <BenchmarkCard
            key={bench.name}
            benchmark={bench}
            isSelected={selected.includes(bench.name)}
            onToggle={() => onToggle(bench.name)}
          />
        ))}
      </div>
    </div>
  )
}
