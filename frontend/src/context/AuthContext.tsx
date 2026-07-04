import { createContext, useCallback, useEffect, useState } from 'react'
import type { User, LoginPayload } from '@/types/user'
import { getProfile, login as loginApi } from '@/services/users'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<void>
  loginWithTokens: (access: string, refresh: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  loginWithTokens: async () => {},
  logout: () => {},
  refreshUser: async () => {},
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }, [])

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setIsLoading(false)
      return
    }
    getProfile()
      .then(setUser)
      .catch(logout)
      .finally(() => setIsLoading(false))
  }, [logout])

  useEffect(() => {
    const handle = () => logout()
    window.addEventListener('auth:logout', handle)
    return () => window.removeEventListener('auth:logout', handle)
  }, [logout])

  const login = async (payload: LoginPayload) => {
    const { access, refresh } = await loginApi(payload)
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    const profile = await getProfile()
    setUser(profile)
  }

  const loginWithTokens = useCallback(async (access: string, refresh: string) => {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    const profile = await getProfile()
    setUser(profile)
  }, [])

  const refreshUser = useCallback(async () => {
    const profile = await getProfile()
    setUser(profile)
  }, [])

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, isLoading, login, loginWithTokens, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  )
}
