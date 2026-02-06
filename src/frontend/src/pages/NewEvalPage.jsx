import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check } from 'lucide-react'
import Header from '../components/layout/Header'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import Modal from '../components/common/Modal'
import Loading from '../components/common/Loading'
import ModelSelector from '../components/models/ModelSelector'
import ModelConfigForm from '../components/models/ModelConfigForm'
import BenchmarkSelector from '../components/benchmarks/BenchmarkSelector'
import { useModels } from '../hooks/useModels'
import { useToast } from '../hooks/useToast'
import { fetchBenchmarks } from '../api/benchmarks'
import { startEvaluation } from '../api/evaluations'

const STEPS = [
  { key: 'model', label: '选择评测对象', num: '1' },
  { key: 'benchmark', label: '选择评测任务', num: '2' },
  { key: 'config', label: '评测配置', num: '3' },
]

export default function NewEvalPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const { models, loading: modelsLoading, add: addModel } = useModels()

  const [step, setStep] = useState(0)
  const [benchmarks, setBenchmarks] = useState([])
  const [benchLoading, setBenchLoading] = useState(true)
  const [showAddModel, setShowAddModel] = useState(false)
  const [addMode, setAddMode] = useState('model')
  const [submitting, setSubmitting] = useState(false)

  // Form state
  const [selectedModel, setSelectedModel] = useState('')
  const [selectedBenchmarks, setSelectedBenchmarks] = useState([])
  const [limit, setLimit] = useState('')
  const [judgeModel, setJudgeModel] = useState('')

  useEffect(() => {
    fetchBenchmarks()
      .then(setBenchmarks)
      .catch(() => toast.error('加载评测任务失败'))
      .finally(() => setBenchLoading(false))
  }, [])

  const toggleBenchmark = useCallback((name) => {
    setSelectedBenchmarks(prev =>
      prev.includes(name) ? prev.filter(b => b !== name) : [...prev, name]
    )
  }, [])

  const selectAllBenchmarks = useCallback((all) => {
    setSelectedBenchmarks(all ? benchmarks.map(b => b.name) : [])
  }, [benchmarks])

  const handleAddModel = async (data) => {
    try {
      const created = await addModel(data)
      setSelectedModel(created.id)
      setShowAddModel(false)
      toast.success('模型添加成功')
    } catch (e) {
      toast.error(e.message)
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const job = await startEvaluation({
        model_id: selectedModel,
        benchmarks: selectedBenchmarks,
        limit: limit ? parseInt(limit) : null,
        judge_model: judgeModel || null,
      })
      toast.success('评测已启动')
      navigate(`/evaluations/${job.id}`)
    } catch (e) {
      toast.error(e.message)
      setSubmitting(false)
    }
  }

  const canNext = () => {
    if (step === 0) return !!selectedModel
    if (step === 1) return selectedBenchmarks.length > 0
    return true
  }

  return (
    <>
      <Header title="新建评测" subtitle="选择模型和评测任务" />
      <div className="flex-1 overflow-y-auto custom-scroll p-6">
        {/* Step indicator */}
        <div className="flex items-center justify-center mb-8">
          {STEPS.map((s, i) => (
            <div key={s.key} className="flex items-center">
              <div
                className={`flex items-center gap-2 px-4 py-2 rounded-lg cursor-pointer transition-all ${
                  i === step
                    ? 'bg-blue-50 text-blue-700'
                    : i < step
                    ? 'text-emerald-600'
                    : 'text-slate-400'
                }`}
                onClick={() => i < step && setStep(i)}
              >
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                  i === step ? 'bg-blue-600 text-white' : i < step ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-400'
                }`}>
                  {i < step ? <Check size={14} /> : s.num}
                </span>
                <span className="text-sm font-medium">{s.label}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`w-12 h-px mx-2 transition-colors ${i < step ? 'bg-emerald-400' : 'bg-slate-200'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step content */}
        <Card className="max-w-3xl mx-auto p-6">
          {step === 0 && (
            modelsLoading ? <Loading /> : (
              <ModelSelector
                models={models}
                selected={selectedModel}
                onSelect={setSelectedModel}
                onAddCustom={() => { setAddMode('model'); setShowAddModel(true) }}
                onAddAgent={() => { setAddMode('agent'); setShowAddModel(true) }}
              />
            )
          )}

          {step === 1 && (
            benchLoading ? <Loading /> : (
              <BenchmarkSelector
                benchmarks={benchmarks}
                selected={selectedBenchmarks}
                onToggle={toggleBenchmark}
                onSelectAll={selectAllBenchmarks}
              />
            )
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-medium text-slate-600 mb-4">评测配置</h3>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="样本数量限制"
                    type="number"
                    placeholder="留空为全部样本"
                    value={limit}
                    onChange={e => setLimit(e.target.value)}
                  />
                  <Input
                    label="裁判模型"
                    placeholder="留空使用默认"
                    value={judgeModel}
                    onChange={e => setJudgeModel(e.target.value)}
                  />
                </div>
              </div>

              {/* Summary */}
              <div className="bg-slate-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-slate-600 mb-3">评测摘要</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">模型</span>
                    <span className="text-slate-700">{models.find(m => m.id === selectedModel)?.name || selectedModel}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">评测任务</span>
                    <span className="text-slate-700">{selectedBenchmarks.length} 个</span>
                  </div>
                  {limit && (
                    <div className="flex justify-between">
                      <span className="text-slate-500">样本限制</span>
                      <span className="text-slate-700">{limit} 个/任务</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* Navigation buttons */}
        <div className="max-w-3xl mx-auto flex justify-between mt-6">
          <Button
            variant="secondary"
            onClick={() => step > 0 ? setStep(step - 1) : navigate('/')}
          >
            {step > 0 ? '上一步' : '取消'}
          </Button>

          {step < STEPS.length - 1 ? (
            <Button onClick={() => setStep(step + 1)} disabled={!canNext()}>
              下一步
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={submitting || !canNext()}>
              {submitting ? '启动中...' : '开始评测'}
            </Button>
          )}
        </div>
      </div>

      {/* Add model/agent modal */}
      <Modal
        open={showAddModel}
        onClose={() => setShowAddModel(false)}
        title={addMode === 'agent' ? '添加智能体' : '添加自定义模型'}
      >
        <ModelConfigForm
          mode={addMode}
          onSubmit={handleAddModel}
          onCancel={() => setShowAddModel(false)}
        />
      </Modal>
    </>
  )
}
