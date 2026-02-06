import { get } from './client'

export function fetchResults() {
  return get('/api/results')
}

export function fetchResultDetail(model) {
  return get(`/api/results/${encodeURIComponent(model)}`)
}
