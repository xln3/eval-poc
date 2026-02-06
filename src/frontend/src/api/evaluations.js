import { get, post } from './client'

export function fetchEvaluations() {
  return get('/api/evaluations')
}

export function fetchEvaluation(id) {
  return get(`/api/evaluations/${id}`)
}

export function startEvaluation(data) {
  return post('/api/evaluations', data)
}
