import { createContext, useCallback, useEffect, useState } from 'react'
import type { User, LoginPayload } from '@/types/user'
import { getProfile, login as loginApi } from '@/services/users'
import { adminLogin as adminLoginApi } from '@/services/adminAuth'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<User>
  adminLogin: (payload: LoginPayload) => Promise<User>
  loginWithTokens: (access: string, refresh: string) => Promise<User>
  logout: () => void
  refreshUser: () => Promise<void>
}

const notImplemented = async (): Promise<User> => {
  throw new Error('AuthContext used outside of AuthProvider')
}

export const AuthContext = createContext<AuthContextValue>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: notImplemented,
  adminLogin: notImplemented,
  loginWithTokens: notImplemented,
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
    return profile
  }

  const loginWithTokens = useCallback(async (access: string, refresh: string) => {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    const profile = await getProfile()
    setUser(profile)
    return profile
  }, [])

  // Hits the separate admin-only endpoint (rejects a non-admin account
  // server-side even with a correct password - see services/adminAuth.ts),
  // then reuses the same token-storage/profile-fetch flow as every other
  // login path once a token pair is actually issued.
  const adminLogin = useCallback(async (payload: LoginPayload) => {
    const { access, refresh } = await adminLoginApi(payload)
    return loginWithTokens(access, refresh)
  }, [loginWithTokens])

  const refreshUser = useCallback(async () => {
    const profile = await getProfile()
    setUser(profile)
  }, [])

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, isLoading, login, adminLogin, loginWithTokens, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  )
}
