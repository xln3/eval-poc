import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Zap, BarChart3, Bot } from 'lucide-react'

const navItems = [
  { path: '/', label: '控制面板', icon: LayoutDashboard },
  { path: '/evaluations/new', label: '新建评测', icon: Zap },
  { path: '/results', label: '评测结果', icon: BarChart3 },
  { path: '/models', label: '模型与智能体', icon: Bot },
]

export default function Sidebar() {
  return (
    <aside className="w-60 bg-slate-100 border-r border-slate-200 flex flex-col shrink-0">
      {/* Logo */}
      <div className="h-16 flex items-center px-5 border-b border-slate-200">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-xs shadow-sm">
            AI
          </div>
          <div>
            <div className="text-sm font-semibold text-slate-800">智能体安全评测</div>
            <div className="text-[11px] text-slate-400">Eval Platform</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3">
        <div className="space-y-1">
          {navItems.map(item => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'bg-white text-blue-600 font-medium shadow-sm'
                      : 'text-slate-700 hover:bg-white/60 hover:text-slate-900'
                  }`
                }
              >
                <Icon size={18} strokeWidth={1.5} />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-200">
        <div className="text-xs text-slate-500">
          Eval Platform
        </div>
        <div className="text-xs text-slate-400 mt-1">v1.0.0</div>
      </div>
    </aside>
  )
}
