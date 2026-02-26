import { post } from './client'

export function generateReport(model) {
  return post('/api/reports/generate', { model })
}

export function generateDatasetDescription(benchmarks) {
  return post('/api/reports/dataset-description', { benchmarks })
}
