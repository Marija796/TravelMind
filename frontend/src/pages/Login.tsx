import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { LogIn, Mail, Lock, Compass, User as UserIcon, ShieldCheck, ArrowLeft } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '@/hooks/useAuth'
import { resendVerificationEmail } from '@/services/users'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import GoogleLoginButton from '@/components/auth/GoogleLoginButton'
import toast from 'react-hot-toast'

type LoginMode = 'user' | 'admin'

// The single Login page for both account types. A visible User/Administrator
// selector always sits above the form (never hidden behind a route, menu,
// or query string) - it only decides which form/copy is shown and which
// endpoint is called. It is a UI convenience, never the security boundary:
// the User path hits the regular login endpoint (which accepts any account,
// admins included - this component still redirects an admin account to
// /admin afterwards); the Administrator path hits the separate admin-only
// endpoint (AdminTokenObtainPairSerializer), which rejects a non-admin
// account server-side with the same generic error a wrong password gets.
export default function Login() {
  const { t } = useTranslation()
  const { login, adminLogin } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  // Deliberately left undefined (not defaulted to '/') when there's no
  // deep-link target, so onSubmit can fall through to the role-based
  // redirect below - defaulting this to '/' would make `from` always
  // truthy and permanently short-circuit that fallback. Reads pathname
  // *and* search (not just pathname) - now that browsing itself requires
  // login, "search from the home page" -> redirected to /login -> back to
  // /explore?search=... is a normal path, and dropping the query string
  // would silently lose the user's search term.
  const state = location.state as { from?: { pathname: string; search?: string }; adminIntent?: boolean } | null
  const fromLocation = state?.from
  const from = fromLocation ? `${fromLocation.pathname}${fromLocation.search || ''}` : undefined

  // AdminRoute redirects an unauthenticated visit to a protected /admin/*
  // page here with adminIntent - it just pre-selects the Administrator
  // card as a convenience, the selection stays fully visible and switchable.
  const [mode, setMode] = useState<LoginMode>(state?.adminIntent ? 'admin' : 'user')
  const [unverifiedEmail, setUnverifiedEmail] = useState<string | null>(null)

  const schema = useMemo(() => z.object({
    username: z.string().min(1, t('auth.usernameRequired')),
    password: z.string().min(1, t('auth.passwordRequired')),
  }), [t])

  type FormData = z.infer<typeof schema>

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const switchMode = (next: LoginMode) => {
    setMode(next)
    reset()
  }

  const onSubmit = async (data: FormData) => {
    setUnverifiedEmail(null)
    if (mode === 'admin') {
      try {
        await adminLogin(data)
        toast.success(t('adminAuth.welcomeToast'))
        navigate('/admin', { replace: true })
      } catch {
        toast.error(t('adminAuth.invalidCredentials'))
      }
      return
    }
    try {
      const profile = await login(data)
      toast.success(t('auth.welcomeBackToast'))
      const destination = from || (profile.role === 'admin' ? '/admin' : '/')
      navigate(destination, { replace: true })
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { code?: string } } }
      if (axiosErr?.response?.data?.code === 'email_not_verified') {
        toast.error(t('auth.emailNotVerifiedToast'))
        // data.username may be an email (the field accepts either) - the
        // resend endpoint no-ops harmlessly if it isn't, so this is safe
        // to offer regardless of which one the user actually typed.
        setUnverifiedEmail(data.username)
      } else {
        toast.error(t('auth.invalidCredentials'))
      }
    }
  }

  const handleResendVerification = async () => {
    if (!unverifiedEmail) return
    try {
      await resendVerificationEmail({ email: unverifiedEmail })
      toast.success(t('auth.resendVerificationSent'))
    } catch {
      toast.error(t('auth.somethingWentWrong'))
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-accent-700">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1488085061387-422e29b40080?w=1200&auto=format')] bg-cover bg-center opacity-20" />
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
              <Compass className="w-6 h-6" />
            </div>
            <span className="text-2xl font-bold">TravelMind</span>
          </div>
          <h2 className="text-4xl font-bold leading-tight mb-4">
            Your next adventure<br />starts here
          </h2>
          <p className="text-white/70 text-lg max-w-sm">
            Personalized destination recommendations tailored to your travel style, budget, and interests.
          </p>
          <div className="flex gap-6 mt-10">
            {[['100+', 'Destinations'], ['7', 'Travel Types'], ['∞', 'Memories']].map(([num, label]) => (
              <div key={label}>
                <p className="text-3xl font-bold">{num}</p>
                <p className="text-white/60 text-sm">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50 dark:bg-slate-950">
        <div className="w-full max-w-md">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              {mode === 'admin' ? t('adminAuth.title') : t('auth.welcomeBack')}
            </h1>
            <p className="text-slate-500 dark:text-slate-400">
              {mode === 'admin' ? t('adminAuth.subtitle') : t('auth.signInToContinue')}
            </p>
          </div>

          {/* Visible User / Administrator account-type selection - always
              shown directly on this page, above the form, never hidden
              behind a route, menu, or link. */}
          <p className="text-sm font-medium text-slate-600 dark:text-slate-300 mb-3">
            {t('auth.chooseLoginType')}
          </p>
          <div className="grid grid-cols-2 gap-3 mb-6">
            <button
              type="button"
              onClick={() => switchMode('user')}
              aria-pressed={mode === 'user'}
              className={`flex flex-col items-center gap-2 rounded-2xl border-2 px-4 py-5 text-center transition-colors ${
                mode === 'user'
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
              }`}
            >
              <UserIcon className={`w-6 h-6 ${mode === 'user' ? 'text-primary-600 dark:text-primary-400' : 'text-slate-400'}`} />
              <span className={`text-sm font-semibold ${mode === 'user' ? 'text-primary-700 dark:text-primary-300' : 'text-slate-600 dark:text-slate-300'}`}>
                {t('auth.loginAsUser')}
              </span>
            </button>
            <button
              type="button"
              onClick={() => switchMode('admin')}
              aria-pressed={mode === 'admin'}
              className={`flex flex-col items-center gap-2 rounded-2xl border-2 px-4 py-5 text-center transition-colors ${
                mode === 'admin'
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
              }`}
            >
              <ShieldCheck className={`w-6 h-6 ${mode === 'admin' ? 'text-primary-600 dark:text-primary-400' : 'text-slate-400'}`} />
              <span className={`text-sm font-semibold ${mode === 'admin' ? 'text-primary-700 dark:text-primary-300' : 'text-slate-600 dark:text-slate-300'}`}>
                {t('auth.loginAsAdministrator')}
              </span>
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label={mode === 'admin' ? t('adminAuth.email') : t('auth.usernameOrEmail')}
              placeholder={mode === 'admin' ? t('adminAuth.emailPlaceholder') : t('auth.usernameOrEmailPlaceholder')}
              leftIcon={<Mail className="w-4 h-4" />}
              error={errors.username?.message}
              {...register('username')}
            />
            <div>
              <Input
                label={t('auth.password')}
                type="password"
                placeholder="••••••••"
                leftIcon={<Lock className="w-4 h-4" />}
                error={errors.password?.message}
                {...register('password')}
              />
              {mode === 'user' && (
                <div className="flex justify-end mt-1.5">
                  <Link
                    to="/forgot-password"
                    className="text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline transition-colors"
                  >
                    {t('auth.forgotPassword')}
                  </Link>
                </div>
              )}
            </div>

            <Button type="submit" fullWidth isLoading={isSubmitting} leftIcon={<LogIn className="w-4 h-4" />} size="lg">
              {mode === 'admin' ? t('adminAuth.loginButton') : t('auth.signIn')}
            </Button>
          </form>

          {mode === 'user' && unverifiedEmail && (
            <button
              type="button"
              onClick={handleResendVerification}
              className="mt-3 text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline"
            >
              {t('auth.resendVerificationEmail')}
            </button>
          )}

          {mode === 'user' ? (
            <>
              {/* Divider */}
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200 dark:border-slate-700" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-slate-50 dark:bg-slate-950 px-3 text-slate-400 font-medium tracking-wide">
                    {t('auth.orContinueWith')}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <GoogleLoginButton redirectTo={from} />
              </div>

              <p className="mt-4 text-center text-sm text-slate-500 dark:text-slate-400">
                {t('auth.dontHaveAccount')}{' '}
                <Link to="/register" className="text-primary-600 font-medium hover:underline">
                  {t('auth.createOne')}
                </Link>
              </p>
            </>
          ) : (
            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={() => switchMode('user')}
                className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                {t('auth.backToUserLogin')}
              </button>
              <p className="mt-3 text-xs text-slate-400 dark:text-slate-500">{t('adminAuth.footerHint')}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
