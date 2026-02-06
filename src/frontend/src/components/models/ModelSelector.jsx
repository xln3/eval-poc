import { Server, Bot, Plus, Check } from 'lucide-react'
import Card from '../common/Card'
import Badge from '../common/Badge'

export default function ModelSelector({ models, selected, onSelect, onAddCustom, onAddAgent }) {
  const presets = models.filter(m => m.model_type === 'preset')
  const customModels = models.filter(m => m.model_type === 'custom' && !m.is_agent)
  const agents = models.filter(m => m.model_type === 'custom' && m.is_agent)

  return (
    <div>
      <h3 className="text-sm font-medium text-slate-600 mb-3">预置模型</h3>
      <div className="grid grid-cols-2 gap-3 mb-6">
        {presets.map(model => (
          <ModelCard
            key={model.id}
            model={model}
            isSelected={selected === model.id}
            onSelect={() => onSelect(model.id)}
          />
        ))}
      </div>

      {customModels.length > 0 && (
        <>
          <h3 className="text-sm font-medium text-slate-600 mb-3">自定义模型</h3>
          <div className="grid grid-cols-2 gap-3 mb-6">
            {customModels.map(model => (
              <ModelCard
                key={model.id}
                model={model}
                isSelected={selected === model.id}
                onSelect={() => onSelect(model.id)}
              />
            ))}
          </div>
        </>
      )}

      {agents.length > 0 && (
        <>
          <h3 className="text-sm font-medium text-slate-600 mb-3">智能体</h3>
          <div className="grid grid-cols-2 gap-3 mb-6">
            {agents.map(model => (
              <ModelCard
                key={model.id}
                model={model}
                isSelected={selected === model.id}
                onSelect={() => onSelect(model.id)}
              />
            ))}
          </div>
        </>
      )}

      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={onAddCustom}
          className="border-2 border-dashed border-slate-200 hover:border-blue-400 rounded-xl py-4 text-sm text-slate-500 hover:text-blue-600 transition-all flex items-center justify-center gap-2"
        >
          <Plus size={16} />
          添加自定义模型
        </button>
        <button
          onClick={onAddAgent}
          className="border-2 border-dashed border-slate-200 hover:border-emerald-400 rounded-xl py-4 text-sm text-slate-500 hover:text-emerald-600 transition-all flex items-center justify-center gap-2"
        >
          <Plus size={16} />
          添加智能体
        </button>
      </div>
    </div>
  )
}

function ModelCard({ model, isSelected, onSelect }) {
  const isAgent = model.is_agent
  return (
    <Card
      hover
      onClick={onSelect}
      className={`p-4 ${isSelected ? 'border-blue-500 bg-blue-50/50' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <div className={`p-1 rounded ${isAgent ? 'text-emerald-500' : 'text-slate-400'}`}>
              {isAgent ? <Bot size={14} /> : <Server size={14} />}
            </div>
            <span className="text-sm font-medium text-slate-800 truncate">{model.name}</span>
            <Badge color={model.model_type === 'preset' ? 'blue' : isAgent ? 'emerald' : 'purple'}>
              {model.model_type === 'preset' ? '预置' : isAgent ? '智能体' : '自定义'}
            </Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">{model.provider}</p>
          <p className="text-xs text-slate-400 mt-1 truncate">{model.model_id}</p>
        </div>
        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ml-2 ${
          isSelected ? 'border-blue-500 bg-blue-500' : 'border-slate-300'
        }`}>
          {isSelected && <Check size={12} className="text-white" />}
        </div>
      </div>
    </Card>
  )
}
