import { useState, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { Mail, ArrowLeft, CheckCircle, Compass } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { requestPasswordReset } from '@/services/users'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import toast from 'react-hot-toast'

export default function ForgotPassword() {
  const { t } = useTranslation()
  const [submitted, setSubmitted] = useState(false)
  const [submittedEmail, setSubmittedEmail] = useState('')

  const schema = useMemo(() => z.object({
    email: z.string().email(t('auth.pleaseEnterValidEmail')),
  }), [t])

  type FormData = z.infer<typeof schema>

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await requestPasswordReset({ email: data.email })
      setSubmittedEmail(data.email)
      setSubmitted(true)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: string } } }
      const msg = axiosErr?.response?.data?.error || t('auth.somethingWentWrong')
      toast.error(msg)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-accent-600 via-primary-700 to-primary-800">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200&auto=format')] bg-cover bg-center opacity-15" />
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
              <Compass className="w-6 h-6" />
            </div>
            <span className="text-2xl font-bold">TravelMind</span>
          </div>
          <h2 className="text-4xl font-bold leading-tight mb-4">
            {t('auth.forgotHeroTitle').split('\n').map((line, i) => (
              <span key={i}>{line}{i === 0 && <br />}</span>
            ))}
          </h2>
          <p className="text-white/70 text-lg max-w-sm">
            {t('auth.forgotHeroCopy')}
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50 dark:bg-slate-950">
        <div className="w-full max-w-md">
          <Link
            to="/login"
            className="inline-flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            {t('auth.backToLogin')}
          </Link>

          {submitted ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
              </div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t('auth.checkYourInbox')}</h1>
              <p className="text-slate-500 dark:text-slate-400 mb-2">
                {t('auth.checkInboxBody', { email: submittedEmail })}
              </p>
              <p className="text-sm text-slate-400 dark:text-slate-500 mb-8">
                {t('auth.checkInboxHint')}
              </p>
              <div className="flex flex-col gap-3">
                <Button onClick={() => setSubmitted(false)} variant="secondary" fullWidth>
                  {t('auth.tryDifferentEmail')}
                </Button>
                <Link to="/login">
                  <Button fullWidth>{t('auth.backToLogin')}</Button>
                </Link>
              </div>
            </div>
          ) : (
            <>
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">{t('auth.forgotPasswordTitle')}</h1>
                <p className="text-slate-500 dark:text-slate-400">
                  {t('auth.forgotPasswordSubtitle')}
                </p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <Input
                  label={t('auth.email')}
                  type="email"
                  placeholder={t('auth.emailPlaceholder')}
                  leftIcon={<Mail className="w-4 h-4" />}
                  error={errors.email?.message}
                  {...register('email')}
                />
                <Button type="submit" fullWidth isLoading={isSubmitting} leftIcon={<Mail className="w-4 h-4" />} size="lg">
                  {t('auth.sendResetLink')}
                </Button>
              </form>

              <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
                {t('auth.rememberedIt')}{' '}
                <Link to="/login" className="text-primary-600 font-medium hover:underline">
                  {t('auth.signIn')}
                </Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
