import { useState, useEffect, useRef, useCallback } from 'react'

export function usePolling(fetchFn, interval = 5000, enabled = true) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const timerRef = useRef(null)

  const poll = useCallback(async () => {
    try {
      const result = await fetchFn()
      setData(result)
      setError(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [fetchFn])

  useEffect(() => {
    if (!enabled) return

    poll()
    timerRef.current = setInterval(poll, interval)

    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [poll, interval, enabled])

  return { data, loading, error, refresh: poll }
}
