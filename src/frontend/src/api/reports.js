import { post } from './client'

export function generateReport(model) {
  return post('/api/reports/generate', { model })
}
