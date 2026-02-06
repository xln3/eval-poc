import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Shield, FileText } from 'lucide-react'
import Header from '../components/layout/Header'
import Card, { CardBody } from '../components/common/Card'
import Button from '../components/common/Button'
import Loading, { EmptyState } from '../components/common/Loading'
import SafetyScoreGauge from '../components/results/SafetyScoreGauge'
import RadarChart from '../components/results/RadarChart'
import RiskLevelBadge from '../components/results/RiskLevelBadge'
import ScoreBar from '../components/results/ScoreBar'
import { useToast } from '../hooks/useToast'
import { fetchResultDetail } from '../api/results'
import { generateReport } from '../api/reports'
import { TASK_META } from '../constants/benchmarkMeta'
import { RISK_LEVELS, getRating, getStars } from '../constants/riskLevels'

export default function ResultDetailPage() {
  const { model } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    fetchResultDetail(model)
      .then(setResult)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [model])

  const handleGenerateReport = async () => {
    setGenerating(true)
    try {
      const report = await generateReport(model)
      // Download as markdown
      const blob = new Blob([report.content], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `security_report_${model.replace(/\//g, '_')}.md`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('报告已生成')
    } catch (e) {
      toast.error('报告生成失败: ' + e.message)
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <><Header title="结果详情" /><Loading /></>
  if (!result) return <><Header title="结果详情" /><EmptyState icon={<FileText size={48} />} title="未找到结果" description={`模型 ${model} 没有评测数据`} /></>

  return (
    <>
      <Header
        title={result.model}
        subtitle="评测结果详情"
        actions={
          <Button onClick={handleGenerateReport} disabled={generating}>
            {generating ? '生成中...' : '生成报告'}
          </Button>
        }
      />
      <div className="flex-1 overflow-y-auto custom-scroll p-6">
        {/* Top section: Score + Radar */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Score card */}
          <Card className="p-6">
            <div className="flex flex-col items-center">
              <SafetyScoreGauge score={result.avg_score} size={180} />
              <div className="mt-4 flex items-center gap-3">
                <RiskLevelBadge level={result.risk_level} />
                <span className="text-slate-500 text-sm">
                  {'★'.repeat(result.stars)}{'☆'.repeat(5 - result.stars)}
                </span>
                <span className="text-sm font-medium text-slate-600">{result.rating}</span>
              </div>
              <div className="mt-3 text-center">
                <div className="text-xs text-slate-500">
                  综合安全评分 · {result.tasks.length} 项测试
                </div>
              </div>
            </div>
          </Card>

          {/* Radar chart */}
          <Card className="p-6">
            <h3 className="text-sm font-medium text-slate-600 mb-2">各维度安全评分</h3>
            <RadarChart tasks={result.tasks} />
          </Card>
        </div>

        {/* Deployment advice */}
        <Card className="mb-6">
          <CardBody>
            <h3 className="text-sm font-medium text-slate-600 mb-3">部署建议</h3>
            {result.avg_score >= 70 ? (
              <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-4 text-sm text-emerald-700">
                模型综合安全表现良好，适合在客服/对话系统、内部知识库等场景部署。代码辅助场景需评估具体风险。
              </div>
            ) : result.avg_score >= 60 ? (
              <div className="bg-amber-50 border border-amber-100 rounded-lg p-4 text-sm text-amber-700">
                模型安全表现及格。建议部署前针对中高风险项实施额外防护措施，实施输入过滤和输出审计。
              </div>
            ) : (
              <div className="bg-red-50 border border-red-100 rounded-lg p-4 text-sm text-red-700">
                模型安全评分低于及格线。不建议在生产环境直接部署。如必须使用，需部署完整安全防护层。
              </div>
            )}
          </CardBody>
        </Card>

        {/* Per-task results */}
        <h3 className="text-sm font-medium text-slate-600 mb-4">分项评测结果</h3>
        <div className="space-y-3">
          {result.tasks.map(task => {
            const meta = TASK_META[task.task]
            const TaskIcon = meta?.icon || Shield
            return (
              <Card key={task.task} className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 bg-slate-100 rounded-lg text-slate-500">
                        <TaskIcon size={16} />
                      </div>
                      <span className="text-sm font-medium text-slate-800">
                        {task.display_name || meta?.name || task.task}
                      </span>
                    </div>
                    {task.description && (
                      <p className="text-xs text-slate-500 mt-1 ml-9">{task.description}</p>
                    )}
                  </div>
                  <RiskLevelBadge level={task.risk_level} />
                </div>

                <div className="ml-9">
                  <ScoreBar score={task.safety_score} />

                  <div className="flex items-center gap-6 mt-3 text-xs text-slate-500">
                    <span>原始分: <span className="font-data text-slate-600">{
                      task.raw_score >= 0 && task.raw_score <= 1
                        ? `${(task.raw_score * 100).toFixed(1)}%`
                        : task.raw_score.toFixed(2)
                    }</span></span>
                    <span>安全分: <span className="font-data text-slate-600 font-medium">{task.safety_score.toFixed(1)}</span></span>
                    {task.samples > 0 && <span>样本数: <span className="font-data text-slate-600">{task.samples}</span></span>}
                  </div>

                  <div className="mt-2 text-xs text-slate-500 bg-slate-50 rounded px-3 py-2">
                    {task.interpretation}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      </div>
    </>
  )
}
