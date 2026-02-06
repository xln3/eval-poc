import { useState } from 'react'
import Input from '../common/Input'
import Button from '../common/Button'

export default function ModelConfigForm({ mode = 'model', onSubmit, onCancel }) {
  const isAgent = mode === 'agent'

  const [form, setForm] = useState({
    name: '',
    provider: '',
    api_base: '',
    api_key: '',
    model_id: '',
    description: '',
    is_agent: isAgent,
  })

  const update = (field, value) => setForm(prev => ({ ...prev, [field]: value }))

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(form)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label={isAgent ? '智能体名称' : '模型名称'}
        placeholder={isAgent ? '例如: 安心银行客服Agent' : '例如: DeepSeek-V3'}
        value={form.name}
        onChange={e => update('name', e.target.value)}
        required
      />
      <Input
        label={isAgent ? '所属系统' : '供应商'}
        placeholder={isAgent ? '例如: 安心银行' : '例如: DeepSeek'}
        value={form.provider}
        onChange={e => update('provider', e.target.value)}
      />
      <Input
        label={isAgent ? '模型标识符' : '模型标识符'}
        placeholder={isAgent ? '例如: openai/mock-bank-agent' : '例如: deepseek/deepseek-chat'}
        value={form.model_id}
        onChange={e => update('model_id', e.target.value)}
        required
      />
      <Input
        label={isAgent ? '智能体端点（OpenAI 兼容）' : 'API 地址（OpenAI 兼容）'}
        placeholder={isAgent ? 'http://localhost:9000/v1' : 'https://api.deepseek.com/v1'}
        value={form.api_base}
        onChange={e => update('api_base', e.target.value)}
        required={isAgent}
      />
      <Input
        label="API Key"
        type="password"
        placeholder={isAgent ? '智能体未设鉴权可填任意值' : 'sk-...'}
        value={form.api_key}
        onChange={e => update('api_key', e.target.value)}
      />
      <Input
        label="描述"
        placeholder={isAgent ? '例如: 带 RAG 和 system prompt 的银行客服智能体' : '可选的模型描述'}
        value={form.description}
        onChange={e => update('description', e.target.value)}
      />
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" type="button" onClick={onCancel}>取消</Button>
        <Button type="submit">{isAgent ? '添加智能体' : '添加模型'}</Button>
      </div>
    </form>
  )
}
