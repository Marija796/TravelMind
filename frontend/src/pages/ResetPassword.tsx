import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useSearchParams } from 'react-router-dom'
import { Lock, CheckCircle, AlertTriangle, Compass } from 'lucide-react'
import { confirmPasswordReset } from '@/services/users'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import toast from 'react-hot-toast'

const schema = z.object({
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  new_password2: z.string().min(1, 'Please confirm your password'),
}).refine((d) => d.new_password === d.new_password2, {
  message: 'Passwords do not match',
  path: ['new_password2'],
})

type FormData = z.infer<typeof schema>

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') || ''
  const token = searchParams.get('token') || ''
  const [success, setSuccess] = useState(false)

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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">Invalid Reset Link</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-8">
            This password reset link is missing required information. Please request a new one.
          </p>
          <Link to="/forgot-password">
            <Button fullWidth>Request new link</Button>
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">Password reset!</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-8">
            Your password has been successfully updated. You can now sign in with your new password.
          </p>
          <Link to="/login">
            <Button fullWidth>Sign in now</Button>
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
      const msg = axiosErr?.response?.data?.error || 'Reset link is invalid or has expired.'
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
            Almost there —<br />set your new password
          </h2>
          <p className="text-white/70 text-lg max-w-sm">
            Choose a strong password to keep your travel plans and saved destinations secure.
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50 dark:bg-slate-950">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Set new password</h1>
            <p className="text-slate-500 dark:text-slate-400">
              Choose a strong password of at least 8 characters.
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="New password"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.new_password?.message}
              helperText="Minimum 8 characters"
              {...register('new_password')}
            />
            <Input
              label="Confirm new password"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.new_password2?.message}
              {...register('new_password2')}
            />
            <Button type="submit" fullWidth isLoading={isSubmitting} size="lg">
              Reset password
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            Remembered it?{' '}
            <Link to="/login" className="text-primary-600 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
