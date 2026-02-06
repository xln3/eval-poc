import { Routes, Route } from 'react-router-dom'
import { ToastProvider } from './hooks/useToast'
import AppShell from './components/layout/AppShell'
import DashboardPage from './pages/DashboardPage'
import NewEvalPage from './pages/NewEvalPage'
import EvalStatusPage from './pages/EvalStatusPage'
import ResultsPage from './pages/ResultsPage'
import ResultDetailPage from './pages/ResultDetailPage'
import ModelsPage from './pages/ModelsPage'

export default function App() {
  return (
    <ToastProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/evaluations/new" element={<NewEvalPage />} />
          <Route path="/evaluations/:id" element={<EvalStatusPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/results/:model" element={<ResultDetailPage />} />
          <Route path="/models" element={<ModelsPage />} />
        </Routes>
      </AppShell>
    </ToastProvider>
  )
}
