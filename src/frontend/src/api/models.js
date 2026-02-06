import { get, post, del } from './client'

export function fetchModels() {
  return get('/api/models')
}

export function createModel(data) {
  return post('/api/models', data)
}

export function deleteModel(id) {
  return del(`/api/models/${id}`)
}
