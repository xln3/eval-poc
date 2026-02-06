import { useState } from 'react'
import { Server, Bot, Settings } from 'lucide-react'
import Header from '../components/layout/Header'
import Card from '../components/common/Card'
import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Modal from '../components/common/Modal'
import Loading, { EmptyState } from '../components/common/Loading'
import ModelConfigForm from '../components/models/ModelConfigForm'
import { useModels } from '../hooks/useModels'
import { useToast } from '../hooks/useToast'

export default function ModelsPage() {
  const toast = useToast()
  const { models, loading, add, remove } = useModels()
  const [showAdd, setShowAdd] = useState(false)
  const [addMode, setAddMode] = useState('model') // 'model' | 'agent'

  const presets = models.filter(m => m.model_type === 'preset')
  const customModels = models.filter(m => m.model_type === 'custom' && !m.is_agent)
  const agents = models.filter(m => m.model_type === 'custom' && m.is_agent)

  const openAdd = (mode) => {
    setAddMode(mode)
    setShowAdd(true)
  }

  const handleAdd = async (data) => {
    try {
      await add(data)
      setShowAdd(false)
      toast.success(data.is_agent ? '智能体添加成功' : '模型添加成功')
    } catch (e) {
      toast.error(e.message)
    }
  }

  const handleDelete = async (id, name, isAgent) => {
    if (!confirm(`确认删除${isAgent ? '智能体' : '模型'} "${name}"？`)) return
    try {
      await remove(id)
      toast.success(isAgent ? '智能体已删除' : '模型已删除')
    } catch (e) {
      toast.error(e.message)
    }
  }

  if (loading) return <><Header title="模型与智能体" /><Loading /></>

  return (
    <>
      <Header
        title="模型与智能体"
        subtitle={`${presets.length + customModels.length} 个模型 · ${agents.length} 个智能体`}
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => openAdd('agent')}>添加智能体</Button>
            <Button onClick={() => openAdd('model')}>添加模型</Button>
          </div>
        }
      />
      <div className="flex-1 overflow-y-auto custom-scroll p-6">
        {/* Preset models */}
        <h3 className="text-sm font-medium text-slate-600 mb-3">预置模型</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8">
          {presets.map(m => (
            <Card key={m.id} className="p-4 border-l-4 border-l-blue-400">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-slate-800">{m.name}</span>
                    <Badge color="blue">预置</Badge>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{m.provider}</p>
                  <p className="text-xs text-slate-400 mt-0.5 font-mono">{m.model_id}</p>
                  {m.description && (
                    <p className="text-xs text-slate-500 mt-1">{m.description}</p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Custom models */}
        <h3 className="text-sm font-medium text-slate-600 mb-3">自定义模型</h3>
        {customModels.length === 0 ? (
          <EmptyState
            icon={<Settings size={48} />}
            title="暂无自定义模型"
            description="添加您自己的模型配置来进行评测"
            action={<Button onClick={() => openAdd('model')}>添加模型</Button>}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {customModels.map(m => (
              <Card key={m.id} className="p-4 border-l-4 border-l-purple-400">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-800">{m.name}</span>
                      <Badge color="purple">自定义</Badge>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{m.provider}</p>
                    <p className="text-xs text-slate-400 mt-0.5 font-mono truncate">{m.model_id}</p>
                    {m.api_base && (
                      <p className="text-xs text-slate-400 mt-0.5 truncate">{m.api_base}</p>
                    )}
                    {m.description && (
                      <p className="text-xs text-slate-500 mt-1">{m.description}</p>
                    )}
                  </div>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(m.id, m.name, false)}
                  >
                    删除
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Agents */}
        <h3 className="text-sm font-medium text-slate-600 mb-3 mt-8">智能体</h3>
        {agents.length === 0 ? (
          <EmptyState
            icon={<Bot size={48} />}
            title="暂无智能体"
            description="添加您的智能体（如带 RAG、工具调用的 Agent）来进行安全评测"
            action={<Button onClick={() => openAdd('agent')}>添加智能体</Button>}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {agents.map(m => (
              <Card key={m.id} className="p-4 border-l-4 border-l-emerald-400">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-800">{m.name}</span>
                      <Badge color="emerald">智能体</Badge>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{m.provider}</p>
                    <p className="text-xs text-slate-400 mt-0.5 font-mono truncate">{m.model_id}</p>
                    {m.api_base && (
                      <p className="text-xs text-emerald-600 mt-0.5 truncate">{m.api_base}</p>
                    )}
                    {m.description && (
                      <p className="text-xs text-slate-500 mt-1">{m.description}</p>
                    )}
                  </div>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(m.id, m.name, true)}
                  >
                    删除
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Modal
        open={showAdd}
        onClose={() => setShowAdd(false)}
        title={addMode === 'agent' ? '添加智能体' : '添加自定义模型'}
      >
        <ModelConfigForm
          mode={addMode}
          onSubmit={handleAdd}
          onCancel={() => setShowAdd(false)}
        />
      </Modal>
    </>
  )
}
