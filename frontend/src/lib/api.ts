const ACCESS = 'cinepulse.access'
const REFRESH = 'cinepulse.refresh'

export const getAccessToken = () => localStorage.getItem(ACCESS)

export function setSession(access: string, refresh: string) {
  localStorage.setItem(ACCESS, access)
  localStorage.setItem(REFRESH, refresh)
}

export function clearSession() {
  localStorage.removeItem(ACCESS)
  localStorage.removeItem(REFRESH)
}

async function refreshAccess() {
  const refresh = localStorage.getItem(REFRESH)
  if (!refresh) return null
  const res = await fetch('/api/auth/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
  if (!res.ok) return null
  const data = await res.json()
  localStorage.setItem(ACCESS, data.access)
  if (data.refresh) localStorage.setItem(REFRESH, data.refresh)
  return data.access as string
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  if (!headers.has('Content-Type') && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let res = await fetch(path, { ...init, headers })
  if (res.status === 401 && token) {
    const next = await refreshAccess()
    if (next) {
      headers.set('Authorization', `Bearer ${next}`)
      res = await fetch(path, { ...init, headers })
    }
  }
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || JSON.stringify(body)
    } catch {
      /* keep */
    }
    throw new Error(detail)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const unwrap = <T,>(data: T[] | { results: T[] }) => (Array.isArray(data) ? data : data.results || [])
