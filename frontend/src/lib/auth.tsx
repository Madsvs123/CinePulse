import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api, clearSession, setSession } from './api'
import type { User } from './types'

interface AuthState {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (payload: Record<string, string>) => Promise<void>
  logout: () => void
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    try {
      setUser(await api<User>('/api/auth/me/'))
    } catch {
      setUser(null)
      clearSession()
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (localStorage.getItem('cinepulse.access')) refresh()
    else setLoading(false)
  }, [])

  const value = useMemo<AuthState>(
    () => ({
      user,
      loading,
      async login(email, password) {
        const tokens = await api<{ access: string; refresh: string }>('/api/auth/login/', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        })
        setSession(tokens.access, tokens.refresh)
        await refresh()
      },
      async register(payload) {
        const data = await api<User & { access: string; refresh: string }>('/api/auth/register/', {
          method: 'POST',
          body: JSON.stringify(payload),
        })
        setSession(data.access, data.refresh)
        setUser(data)
      },
      logout() {
        clearSession()
        setUser(null)
      },
      refresh,
    }),
    [user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('AuthProvider required')
  return ctx
}
