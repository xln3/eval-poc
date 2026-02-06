import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart3, ChevronRight } from 'lucide-react'
import Header from '../components/layout/Header'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import Loading, { EmptyState } from '../components/common/Loading'
import SafetyScoreGauge from '../components/results/SafetyScoreGauge'
import RiskLevelBadge from '../components/results/RiskLevelBadge'
import { fetchResults } from '../api/results'

export default function ResultsPage() {
  const navigate = useNavigate()
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchResults()
      .then(setResults)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <><Header title="评测结果" /><Loading /></>

  return (
    <>
      <Header
        title="评测结果"
        subtitle={`共 ${results.length} 个模型`}
        actions={
          <Button onClick={() => navigate('/evaluations/new')}>新建评测</Button>
        }
      />
      <div className="flex-1 overflow-y-auto custom-scroll p-6">
        {results.length === 0 ? (
          <EmptyState
            icon={<BarChart3 size={48} />}
            title="暂无评测结果"
            description="运行评测后结果将显示在这里"
            action={<Button onClick={() => navigate('/evaluations/new')}>开始评测</Button>}
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {results.map(r => (
              <Card
                key={r.model}
                hover
                onClick={() => navigate(`/results/${encodeURIComponent(r.model)}`)}
                className="p-5"
              >
                <div className="flex items-center gap-5">
                  <SafetyScoreGauge score={r.avg_score} size={100} />
                  <div className="flex-1 min-w-0">
                    <div className="text-lg font-semibold text-slate-800 truncate">{r.model}</div>
                    <div className="flex items-center gap-2 mt-2">
                      <RiskLevelBadge level={r.risk_level} />
                      <span className="text-xs text-slate-500">
                        {'★'.repeat(r.stars)}{'☆'.repeat(5 - r.stars)} {r.rating}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 mt-2">
                      {r.task_count} 项测试
                      {r.eval_date && ` · ${r.eval_date.split('T')[0]}`}
                    </div>
                  </div>
                  <ChevronRight size={18} className="text-slate-300 shrink-0" />
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </>
  )
}
