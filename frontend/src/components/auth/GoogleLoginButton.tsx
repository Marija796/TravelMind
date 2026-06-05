import { useGoogleLogin } from '@react-oauth/google'
import { useNavigate } from 'react-router-dom'
import { googleAuth } from '@/services/users'
import { useAuth } from '@/hooks/useAuth'
import toast from 'react-hot-toast'
import { useState } from 'react'

interface Props {
  redirectTo?: string
}

export default function GoogleLoginButton({ redirectTo = '/' }: Props) {
  const { loginWithTokens } = useAuth()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)

  const login = useGoogleLogin({
    flow: 'auth-code',
    scope: 'openid email profile',
    onSuccess: async (codeResponse) => {
      setIsLoading(true)
      try {
        const data = await googleAuth({ code: codeResponse.code })
        await loginWithTokens(data.access, data.refresh)
        toast.success('Signed in with Google!')
        navigate(redirectTo, { replace: true })
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        const msg = axiosErr?.response?.data?.error || (err instanceof Error ? err.message : '') || 'Google sign-in failed. Please try again.'
        console.error('Google sign-in error:', err)
        toast.error(msg)
      } finally {
        setIsLoading(false)
      }
    },
    onError: (error) => {
      console.error('Google OAuth error:', error)
      const code = error.error as string | undefined
      if (code === 'popup_blocked_by_browser') {
        toast.error('Popup blocked — please allow popups for this site.')
      } else if (code === 'access_denied') {
        toast.error('Access denied. Please allow the required permissions.')
      } else if (code === 'redirect_uri_mismatch' || code === 'invalid_client') {
        toast.error('Google sign-in is misconfigured. Add http://localhost:5173 to Authorized JavaScript Origins in Google Cloud Console.')
      } else {
        toast.error(`Google sign-in failed${code ? ` (${code})` : ''}. Please try again.`)
      }
    },
  })

  return (
    <button
      type="button"
      onClick={() => login()}
      disabled={isLoading}
      className="w-full flex items-center justify-center gap-3 h-10 px-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
    >
      {isLoading ? (
        <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
      ) : (
        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
        </svg>
      )}
      {isLoading ? 'Signing in…' : 'Continue with Google'}
    </button>
  )
}