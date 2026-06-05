import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { LogIn, Mail, Lock, Compass } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '@/hooks/useAuth'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import GoogleLoginButton from '@/components/auth/GoogleLoginButton'
import toast from 'react-hot-toast'

const schema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
})

type FormData = z.infer<typeof schema>

export default function Login() {
  const { t } = useTranslation()
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/'

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await login(data)
      toast.success('Welcome back!')
      navigate(from, { replace: true })
    } catch {
      toast.error('Invalid username or password')
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
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">{t('auth.welcomeBack')}</h1>
            <p className="text-slate-500 dark:text-slate-400">{t('auth.signInToContinue')}</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label={t('auth.username')}
              placeholder={t('auth.usernamePlaceholder')}
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
              <div className="flex justify-end mt-1.5">
                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline transition-colors"
                >
                  {t('auth.forgotPassword')}
                </Link>
              </div>
            </div>

            <Button type="submit" fullWidth isLoading={isSubmitting} leftIcon={<LogIn className="w-4 h-4" />} size="lg">
              {t('auth.signIn')}
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
            <GoogleLoginButton redirectTo={from} />
          </div>

          {/* Continue as Guest */}
          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-slate-50 dark:bg-slate-950 px-3 text-slate-400 font-medium tracking-wide">
                {t('auth.or')}
              </span>
            </div>
          </div>

          <Button
            type="button"
            variant="ghost"
            fullWidth
            size="lg"
            className="border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            onClick={() => navigate('/explore')}
          >
            {t('auth.continueAsGuest')}
          </Button>
          <p className="text-center text-xs text-slate-400 dark:text-slate-500">
            {t('auth.guestHint')}
          </p>

          <p className="mt-4 text-center text-sm text-slate-500 dark:text-slate-400">
            {t('auth.dontHaveAccount')}{' '}
            <Link to="/register" className="text-primary-600 font-medium hover:underline">
              {t('auth.createOne')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
