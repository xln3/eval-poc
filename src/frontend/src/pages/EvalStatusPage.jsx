import { useCallback, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { CheckCircle2, XCircle } from 'lucide-react'
import Header from '../components/layout/Header'
import Card, { CardBody } from '../components/common/Card'
import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Loading from '../components/common/Loading'
import EvalProgress from '../components/evaluation/EvalProgress'
import { usePolling } from '../hooks/usePolling'
import { fetchEvaluation } from '../api/evaluations'

export default function EvalStatusPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const fetchFn = useCallback(() => fetchEvaluation(id), [id])
  const { data: job, loading, error } = usePolling(fetchFn, 3000)

  // Auto-navigate on completion
  useEffect(() => {
    if (job && job.status === 'completed' && !job.error) {
      const timer = setTimeout(() => {
        navigate(`/results/${encodeURIComponent(job.model_id)}`)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [job, navigate])

  if (loading) return <><Header title="评测进度" /><Loading text="加载评测状态..." /></>
  if (error) return <><Header title="评测进度" /><div className="p-6 text-red-600">{error}</div></>

  const statusColors = {
    pending: 'slate',
    running: 'blue',
    completed: 'green',
    failed: 'red',
  }
  const statusLabels = {
    pending: '等待中',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
  }

  return (
    <>
      <Header
        title="评测进度"
        subtitle={`任务 ${id}`}
        actions={
          job?.status === 'completed' && (
            <Button onClick={() => navigate(`/results/${encodeURIComponent(job.model_id)}`)}>
              查看结果
            </Button>
          )
        }
      />
      <div className="flex-1 overflow-y-auto custom-scroll p-6">
        {/* Status header */}
        <Card className="mb-6">
          <CardBody>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-semibold text-slate-800">{job.model_name || job.model_id}</div>
                <div className="text-sm text-slate-500 mt-1">
                  {job.benchmarks.join(', ')} · {job.tasks.length} 个测试项
                </div>
              </div>
              <div className="flex items-center gap-3">
                {job.status === 'running' && (
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
                )}
                <Badge color={statusColors[job.status]}>
                  {statusLabels[job.status]}
                </Badge>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Progress */}
        <Card>
          <CardBody>
            <EvalProgress job={job} />
          </CardBody>
        </Card>

        {/* Completion message */}
        {job.status === 'completed' && !job.error && (
          <div className="mt-6 bg-emerald-50 border border-emerald-100 rounded-xl p-6 text-center">
            <CheckCircle2 size={36} className="text-emerald-500 mx-auto" />
            <h3 className="text-lg font-semibold text-emerald-700 mt-3">评测完成</h3>
            <p className="text-sm text-slate-500 mt-1">3秒后自动跳转到结果页面...</p>
          </div>
        )}

        {job.status === 'failed' && (
          <div className="mt-6 bg-red-50 border border-red-100 rounded-xl p-6 text-center">
            <XCircle size={36} className="text-red-500 mx-auto" />
            <h3 className="text-lg font-semibold text-red-700 mt-3">评测失败</h3>
            {job.error && <p className="text-sm text-slate-500 mt-1">{job.error}</p>}
            <Button variant="secondary" className="mt-4" onClick={() => navigate('/evaluations/new')}>
              重新评测
            </Button>
          </div>
        )}
      </div>
    </>
  )
}
