import Badge from '../common/Badge'
import { TASK_META } from '../../constants/benchmarkMeta'

const statusConfig = {
  pending: { label: '待执行', color: 'slate', icon: '○' },
  running: { label: '执行中', color: 'blue', icon: '◉' },
  completed: { label: '已完成', color: 'green', icon: '✓' },
  failed: { label: '失败', color: 'red', icon: '✕' },
  skipped: { label: '跳过', color: 'yellow', icon: '–' },
}

export default function EvalProgress({ job }) {
  if (!job) return null

  return (
    <div>
      {/* Overall progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-slate-600">总体进度</span>
          <span className="text-sm font-medium text-blue-600">{job.progress.toFixed(0)}%</span>
        </div>
        <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${job.progress}%` }}
          />
        </div>
      </div>

      {/* Task list */}
      <div className="space-y-2">
        {job.tasks.map((task, i) => {
          const config = statusConfig[task.status] || statusConfig.pending
          const meta = TASK_META[task.task_name]

          return (
            <div
              key={i}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${
                task.status === 'running'
                  ? 'bg-blue-50 border-blue-200'
                  : 'bg-white border-slate-200'
              }`}
            >
              <span className={`text-lg ${
                task.status === 'running' ? 'animate-pulse text-blue-500' : `text-${config.color}-500`
              }`}>
                {config.icon}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-slate-700">
                  {meta?.name || task.task_name}
                </div>
                <div className="text-xs text-slate-500">{task.benchmark}</div>
              </div>
              <Badge color={config.color}>{config.label}</Badge>
              {task.error && (
                <span className="text-xs text-red-600 truncate max-w-[200px]" title={task.error}>
                  {task.error}
                </span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
