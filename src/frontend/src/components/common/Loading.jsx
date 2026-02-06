import { Inbox } from 'lucide-react'

export default function Loading({ text = '加载中...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      <p className="text-sm text-slate-400 mt-3">{text}</p>
    </div>
  )
}

export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      {typeof icon === 'string' ? (
        <span className="text-4xl mb-4">{icon}</span>
      ) : icon ? (
        <div className="mb-4 text-slate-300">{icon}</div>
      ) : (
        <Inbox size={48} className="mb-4 text-slate-300" />
      )}
      <h3 className="text-lg font-medium text-slate-700">{title}</h3>
      {description && <p className="text-sm text-slate-500 mt-1">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
