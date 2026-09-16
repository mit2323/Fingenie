import { createContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { authService } from '../services/authService'
import type { User } from '../types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (fullName: string, email: string, password: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!localStorage.getItem('fingenie_token')) {
      setLoading(false)
      return
    }
    authService.me().then(setUser).catch(() => localStorage.removeItem('fingenie_token')).finally(() => setLoading(false))
  }, [])

  const value = useMemo(() => ({
    user,
    loading,
    login: async (email: string, password: string) => {
      const token = await authService.login({ email, password })
      localStorage.setItem('fingenie_token', token.access_token)
      setUser(await authService.me())
    },
    register: async (fullName: string, email: string, password: string) => {
      await authService.register({ full_name: fullName, email, password })
      const token = await authService.login({ email, password })
      localStorage.setItem('fingenie_token', token.access_token)
      setUser(await authService.me())
    },
    logout: () => {
      localStorage.removeItem('fingenie_token')
      setUser(null)
    },
  }), [loading, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
