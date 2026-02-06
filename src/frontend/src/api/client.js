const BASE_URL = ''

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  }

  const res = await fetch(url, config)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `请求失败: ${res.status}`)
  }
  return res.json()
}

export function get(path) {
  return request(path)
}

export function post(path, data) {
  return request(path, { method: 'POST', body: JSON.stringify(data) })
}

export function del(path) {
  return request(path, { method: 'DELETE' })
}
