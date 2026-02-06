import { useState, useEffect, useCallback } from 'react'
import { fetchModels, createModel, deleteModel } from '../api/models'

export function useModels() {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    try {
      setLoading(true)
      const data = await fetchModels()
      setModels(data)
      setError(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const add = async (modelData) => {
    const created = await createModel(modelData)
    await load()
    return created
  }

  const remove = async (id) => {
    await deleteModel(id)
    await load()
  }

  return { models, loading, error, refresh: load, add, remove }
}
