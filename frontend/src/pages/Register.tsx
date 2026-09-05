import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { UserPlus, Mail, Lock, User, Compass, CheckCircle } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { register as registerUser, resendVerificationEmail } from '@/services/users'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import GoogleLoginButton from '@/components/auth/GoogleLoginButton'
import toast from 'react-hot-toast'

export default function Register() {
  const { t } = useTranslation()
  const [registeredEmail, setRegisteredEmail] = useState('')

  // zod schemas are usually module-scope, but validation messages need t(),
  // which is only available inside the component - recompute only when the
  // language changes, not on every render.
  const schema = useMemo(() => z.object({
    username: z.string().min(3, t('auth.usernameMinChars')).max(30, t('auth.usernameMaxChars')),
    email: z.string().email(t('auth.invalidEmail')),
    password: z.string().min(8, t('auth.passwordMinChars')),
    password2: z.string().min(1, t('auth.confirmPasswordRequired')),
  }).refine((d) => d.password === d.password2, {
    message: t('auth.passwordsDontMatch'),
    path: ['password2'],
  }), [t])

  type FormData = z.infer<typeof schema>

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await registerUser(data)
      // Registration no longer auto-logs the user in - a brand new account
      // is unverified, so an immediate login attempt would just fail with
      // "email not verified". Show the check-your-inbox state directly
      // instead of surfacing that as an error right after a successful signup.
      setRegisteredEmail(data.email)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: Record<string, string[]> } }
      const msg = Object.values(axiosErr?.response?.data || {}).flat().join(' ') || t('auth.registrationFailed')
      toast.error(msg)
    }
  }

  const handleResend = async () => {
    try {
      await resendVerificationEmail({ email: registeredEmail })
      toast.success(t('auth.resendVerificationSent'))
    } catch {
      toast.error(t('auth.somethingWentWrong'))
    }
  }

  if (registeredEmail) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="w-full max-w-md text-center">
          <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t('auth.checkYourInbox')}</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-2">
            {t('auth.registerCheckInboxBody', { email: registeredEmail })}
          </p>
          <p className="text-sm text-slate-400 dark:text-slate-500 mb-8">
            {t('auth.registerCheckInboxHint')}
          </p>
          <div className="flex flex-col gap-3">
            <Button onClick={handleResend} variant="secondary" fullWidth>
              {t('auth.resendVerificationEmail')}
            </Button>
            <Link to="/login">
              <Button fullWidth>{t('auth.backToLogin')}</Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-accent-600 via-accent-700 to-primary-700">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200&auto=format')] bg-cover bg-center opacity-20" />
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
              <Compass className="w-6 h-6" />
            </div>
            <span className="text-2xl font-bold">TravelMind</span>
          </div>
          <h2 className="text-4xl font-bold leading-tight mb-4">
            {t('auth.registerHeroTitle').split('\n').map((line, i) => (
              <span key={i}>{line}{i === 0 && <br />}</span>
            ))}
          </h2>
          <p className="text-white/70 text-lg max-w-sm">
            {t('auth.registerHeroCopy')}
          </p>
          <div className="mt-10 space-y-3">
            {[t('auth.featureAI'), t('auth.featureSave'), t('auth.featureReviews')].map((f) => (
              <div key={f} className="flex items-center gap-2 text-white/80">
                <div className="w-1.5 h-1.5 bg-white rounded-full" />
                <span>{f}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50 dark:bg-slate-950">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">{t('auth.registerTitle')}</h1>
            <p className="text-slate-500 dark:text-slate-400">{t('auth.startJourney')}</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label={t('auth.username')}
              placeholder={t('auth.usernamePlaceholder')}
              leftIcon={<User className="w-4 h-4" />}
              error={errors.username?.message}
              {...register('username')}
            />
            <Input
              label={t('auth.email')}
              type="email"
              placeholder={t('auth.emailPlaceholder')}
              leftIcon={<Mail className="w-4 h-4" />}
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              label={t('auth.password')}
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.password?.message}
              helperText={t('auth.minPasswordChars')}
              {...register('password')}
            />
            <Input
              label={t('auth.confirmPassword')}
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.password2?.message}
              {...register('password2')}
            />

            <Button type="submit" fullWidth isLoading={isSubmitting} leftIcon={<UserPlus className="w-4 h-4" />} size="lg" className="mt-2">
              {t('auth.registerButton')}
            </Button>
          </form>

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
            <GoogleLoginButton />
          </div>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            {t('auth.alreadyHaveAccount')}{' '}
            <Link to="/login" className="text-primary-600 font-medium hover:underline">
              {t('auth.signIn')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
