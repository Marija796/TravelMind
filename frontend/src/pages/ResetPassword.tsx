import { useState, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useSearchParams } from 'react-router-dom'
import { Lock, CheckCircle, AlertTriangle, Compass } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { confirmPasswordReset } from '@/services/users'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import toast from 'react-hot-toast'

export default function ResetPassword() {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') || ''
  const token = searchParams.get('token') || ''
  const [success, setSuccess] = useState(false)

  const schema = useMemo(() => z.object({
    new_password: z.string().min(8, t('auth.newPasswordMinChars')),
    new_password2: z.string().min(1, t('auth.confirmPasswordRequired')),
  }).refine((d) => d.new_password === d.new_password2, {
    message: t('auth.passwordsDontMatch'),
    path: ['new_password2'],
  }), [t])

  type FormData = z.infer<typeof schema>

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  if (!uid || !token) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="w-full max-w-md text-center">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t('auth.invalidResetLinkTitle')}</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-8">
            {t('auth.invalidResetLinkBody')}
          </p>
          <Link to="/forgot-password">
            <Button fullWidth>{t('auth.requestNewLink')}</Button>
          </Link>
        </div>
      </div>
    )
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="w-full max-w-md text-center">
          <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t('auth.passwordResetSuccessTitle')}</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-8">
            {t('auth.passwordResetSuccessBody')}
          </p>
          <Link to="/login">
            <Button fullWidth>{t('auth.signInNow')}</Button>
          </Link>
        </div>
      </div>
    )
  }

  const onSubmit = async (data: FormData) => {
    try {
      await confirmPasswordReset({ uid, token, new_password: data.new_password, new_password2: data.new_password2 })
      setSuccess(true)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: Record<string, string> } }
      const msg = axiosErr?.response?.data?.error || t('auth.invalidToken')
      toast.error(msg)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-primary-700 via-primary-800 to-accent-800">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1200&auto=format')] bg-cover bg-center opacity-15" />
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
              <Compass className="w-6 h-6" />
            </div>
            <span className="text-2xl font-bold">TravelMind</span>
          </div>
          <h2 className="text-4xl font-bold leading-tight mb-4">
            {t('auth.resetHeroTitle').split('\n').map((line, i) => (
              <span key={i}>{line}{i === 0 && <br />}</span>
            ))}
          </h2>
          <p className="text-white/70 text-lg max-w-sm">
            {t('auth.resetHeroCopy')}
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50 dark:bg-slate-950">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">{t('auth.resetPasswordTitle')}</h1>
            <p className="text-slate-500 dark:text-slate-400">
              {t('auth.resetPasswordSubtitle')}
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label={t('auth.newPassword')}
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.new_password?.message}
              helperText={t('auth.minPasswordChars')}
              {...register('new_password')}
            />
            <Input
              label={t('auth.confirmNewPassword')}
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.new_password2?.message}
              {...register('new_password2')}
            />
            <Button type="submit" fullWidth isLoading={isSubmitting} size="lg">
              {t('auth.resetPassword')}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            {t('auth.rememberedIt')}{' '}
            <Link to="/login" className="text-primary-600 font-medium hover:underline">
              {t('auth.signIn')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
