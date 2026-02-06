import { get } from './client'

export function fetchBenchmarks() {
  return get('/api/benchmarks')
}

export function fetchTaskMeta() {
  return get('/api/benchmarks/task-meta')
}
