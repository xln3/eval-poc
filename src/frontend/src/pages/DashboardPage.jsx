import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, BarChart3, Bot, ChevronRight, Activity, Server, TrendingUp } from 'lucide-react'
import Header from '../components/layout/Header'
import Card, { CardBody } from '../components/common/Card'
import Button from '../components/common/Button'
import Badge from '../components/common/Badge'
import Loading from '../components/common/Loading'
import RiskLevelBadge from '../components/results/RiskLevelBadge'
import { fetchResults } from '../api/results'
import { fetchEvaluations } from '../api/evaluations'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [results, setResults] = useState([])
  const [evals, setEvals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetchResults().catch(() => []),
      fetchEvaluations().catch(() => []),
    ]).then(([r, e]) => {
      setResults(r)
      setEvals(e)
      setLoading(false)
    })
  }, [])

  if (loading) return <><Header title="控制面板" /><Loading /></>

  const latestScore = results.length > 0 ? results[0].avg_score : null
  const recentEvals = evals.slice(-5).reverse()

  return (
    <>
      <Header title="控制面板" subtitle="智能体安全评测平台" />
      <div className="flex-1 overflow-y-auto custom-scroll p-6">
        {/* Welcome banner */}
        <div className="relative bg-gradient-to-br from-blue-50 via-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-6 mb-6 overflow-hidden">
          <div className="absolute inset-0 opacity-[0.4]" style={{
            backgroundImage: 'radial-gradient(circle, #3b82f620 1px, transparent 1px)',
            backgroundSize: '20px 20px',
          }} />
          <div className="relative">
            <h2 className="text-xl font-bold text-slate-800 mb-2">智能体安全评测平台</h2>
            <p className="text-sm text-slate-500">
              统一的大模型及智能体安全评测系统，支持多种安全基准测试，以 0-100 统一安全评分直观呈现评测结果。
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card className="p-5 border-l-4 border-l-blue-500">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-data text-3xl font-bold text-slate-800">{results.length}</div>
                <div className="text-sm text-slate-500 mt-1">已评测模型</div>
              </div>
              <div className="p-2 bg-blue-50 rounded-lg text-blue-500">
                <Server size={20} />
              </div>
            </div>
          </Card>
          <Card className="p-5 border-l-4 border-l-indigo-500">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-data text-3xl font-bold text-slate-800">{evals.length}</div>
                <div className="text-sm text-slate-500 mt-1">评测次数</div>
              </div>
              <div className="p-2 bg-indigo-50 rounded-lg text-indigo-500">
                <Activity size={20} />
              </div>
            </div>
          </Card>
          <Card className="p-5 border-l-4 border-l-emerald-500">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-data text-3xl font-bold" style={{ color: latestScore ? (latestScore >= 60 ? '#16a34a' : '#dc2626') : '#64748b' }}>
                  {latestScore ? latestScore.toFixed(1) : '—'}
                </div>
                <div className="text-sm text-slate-500 mt-1">最近评测得分</div>
              </div>
              <div className="p-2 bg-emerald-50 rounded-lg text-emerald-500">
                <TrendingUp size={20} />
              </div>
            </div>
          </Card>
        </div>

        {/* Quick actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card hover onClick={() => navigate('/evaluations/new')} className="p-5">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
                <Zap size={22} />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-slate-700">开始新评测</div>
                <div className="text-xs text-slate-500 mt-0.5">选择模型和任务开始评测</div>
              </div>
              <ChevronRight size={16} className="text-slate-300" />
            </div>
          </Card>
          <Card hover onClick={() => navigate('/results')} className="p-5">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
                <BarChart3 size={22} />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-slate-700">查看结果</div>
                <div className="text-xs text-slate-500 mt-0.5">查看历史评测结果和报告</div>
              </div>
              <ChevronRight size={16} className="text-slate-300" />
            </div>
          </Card>
          <Card hover onClick={() => navigate('/models')} className="p-5">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
                <Bot size={22} />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-slate-700">管理模型</div>
                <div className="text-xs text-slate-500 mt-0.5">配置预置和自定义模型</div>
              </div>
              <ChevronRight size={16} className="text-slate-300" />
            </div>
          </Card>
        </div>

        {/* Recent results */}
        {results.length > 0 && (
          <Card>
            <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-700">评测结果</h3>
              <Button variant="ghost" size="sm" onClick={() => navigate('/results')}>查看全部</Button>
            </div>
            <div className="divide-y divide-slate-100">
              {results.map(r => (
                <div
                  key={r.model}
                  className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/results/${encodeURIComponent(r.model)}`)}
                >
                  <div>
                    <div className="text-sm text-slate-700">{r.model}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{r.task_count} 项测试 · {r.rating}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-data text-sm font-medium text-slate-600">{r.avg_score.toFixed(1)}</span>
                    <RiskLevelBadge level={r.risk_level} />
                    <ChevronRight size={14} className="text-slate-300" />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Recent evaluations */}
        {recentEvals.length > 0 && (
          <Card className="mt-4">
            <div className="px-5 py-4 border-b border-slate-100">
              <h3 className="text-sm font-medium text-slate-700">最近评测</h3>
            </div>
            <div className="divide-y divide-slate-100">
              {recentEvals.map(ev => (
                <div
                  key={ev.id}
                  className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/evaluations/${ev.id}`)}
                >
                  <div>
                    <div className="text-sm text-slate-700">{ev.model_name || ev.model_id}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{ev.benchmarks.join(', ')}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge color={ev.status === 'completed' ? 'green' : ev.status === 'running' ? 'blue' : ev.status === 'failed' ? 'red' : 'slate'}>
                      {ev.status === 'completed' ? '已完成' : ev.status === 'running' ? '执行中' : ev.status === 'failed' ? '失败' : '等待中'}
                    </Badge>
                    <ChevronRight size={14} className="text-slate-300" />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </>
  )
}
