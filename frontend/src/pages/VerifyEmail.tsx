import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { CheckCircle, AlertTriangle, Compass } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { verifyEmail, resendVerificationEmail } from '@/services/users'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import toast from 'react-hot-toast'

type Status = 'verifying' | 'success' | 'error'

export default function VerifyEmail() {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') || ''
  const token = searchParams.get('token') || ''
  const [status, setStatus] = useState<Status>('verifying')
  const [errorMessage, setErrorMessage] = useState('')
  const [resendEmail, setResendEmail] = useState('')
  const [isResending, setIsResending] = useState(false)

  useEffect(() => {
    if (!uid || !token) return
    verifyEmail({ uid, token })
      .then(() => setStatus('success'))
      .catch((err: unknown) => {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        setErrorMessage(axiosErr?.response?.data?.error || t('auth.verificationFailedBody'))
        setStatus('error')
      })
    // uid/token come from the URL and don't change during this page's life.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid, token])

  const handleResend = async () => {
    if (!resendEmail) return
    setIsResending(true)
    try {
      await resendVerificationEmail({ email: resendEmail })
      toast.success(t('auth.resendVerificationSent'))
    } catch {
      toast.error(t('auth.somethingWentWrong'))
    } finally {
      setIsResending(false)
    }
  }

  if (!uid || !token) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="w-full max-w-md text-center">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t('auth.invalidVerificationLinkTitle')}</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-8">{t('auth.invalidVerificationLinkBody')}</p>
          <Link to="/register">
            <Button fullWidth>{t('auth.createOne')}</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="w-full max-w-md text-center">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center">
            <Compass className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <span className="text-xl font-bold text-slate-900 dark:text-white">TravelMind</span>
        </div>

        {status === 'verifying' && (
          <>
            <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-6" />
            <p className="text-slate-500 dark:text-slate-400">{t('auth.verifyingEmail')}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t('auth.emailVerifiedTitle')}</h1>
            <p className="text-slate-500 dark:text-slate-400 mb-8">{t('auth.emailVerifiedBody')}</p>
            <Link to="/login">
              <Button fullWidth>{t('auth.signInNow')}</Button>
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t('auth.verificationFailedTitle')}</h1>
            <p className="text-slate-500 dark:text-slate-400 mb-8">{errorMessage}</p>

            <div className="text-left space-y-3">
              <p className="text-sm font-medium text-slate-600 dark:text-slate-300">{t('auth.resendPrompt')}</p>
              <Input
                type="email"
                placeholder={t('auth.emailPlaceholder')}
                value={resendEmail}
                onChange={(e) => setResendEmail(e.target.value)}
              />
              <Button onClick={handleResend} isLoading={isResending} fullWidth>
                {t('auth.resendVerificationEmail')}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
