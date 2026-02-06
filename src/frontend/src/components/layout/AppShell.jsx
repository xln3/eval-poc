import Sidebar from './Sidebar'

export default function AppShell({ children }) {
  return (
    <div className="h-full flex bg-slate-50">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        {children}
      </main>
    </div>
  )
}
