import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { Mail, ArrowLeft, CheckCircle, Compass } from 'lucide-react'
import { requestPasswordReset } from '@/services/users'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import toast from 'react-hot-toast'

const schema = z.object({
  email: z.string().email('Please enter a valid email address'),
})

type FormData = z.infer<typeof schema>

export default function ForgotPassword() {
  const [submitted, setSubmitted] = useState(false)
  const [submittedEmail, setSubmittedEmail] = useState('')

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
      const msg = axiosErr?.response?.data?.error || 'Something went wrong. Please try again.'
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
            Don't worry,<br />we've got you
          </h2>
          <p className="text-white/70 text-lg max-w-sm">
            Enter your email address and we'll send you a link to reset your password and get back on track.
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
            Back to login
          </Link>

          {submitted ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
              </div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">Check your inbox</h1>
              <p className="text-slate-500 dark:text-slate-400 mb-2">
                If <span className="font-medium text-slate-700 dark:text-slate-300">{submittedEmail}</span> is registered,
                a password reset link is on its way.
              </p>
              <p className="text-sm text-slate-400 dark:text-slate-500 mb-8">
                Didn't receive it? Check your spam folder or try again in a few minutes.
              </p>
              <div className="flex flex-col gap-3">
                <Button onClick={() => setSubmitted(false)} variant="secondary" fullWidth>
                  Try a different email
                </Button>
                <Link to="/login">
                  <Button fullWidth>Back to login</Button>
                </Link>
              </div>
            </div>
          ) : (
            <>
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Forgot password?</h1>
                <p className="text-slate-500 dark:text-slate-400">
                  Enter your email and we'll send you a reset link.
                </p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <Input
                  label="Email address"
                  type="email"
                  placeholder="you@example.com"
                  leftIcon={<Mail className="w-4 h-4" />}
                  error={errors.email?.message}
                  {...register('email')}
                />
                <Button type="submit" fullWidth isLoading={isSubmitting} leftIcon={<Mail className="w-4 h-4" />} size="lg">
                  Send reset link
                </Button>
              </form>

              <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
                Remembered it?{' '}
                <Link to="/login" className="text-primary-600 font-medium hover:underline">
                  Sign in
                </Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
