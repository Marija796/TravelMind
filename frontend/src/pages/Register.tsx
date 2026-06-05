import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Mail, Lock, User, Compass } from 'lucide-react'
import { register as registerUser } from '@/services/users'
import { useAuth } from '@/hooks/useAuth'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import GoogleLoginButton from '@/components/auth/GoogleLoginButton'
import toast from 'react-hot-toast'

const schema = z.object({
  username: z.string().min(3, 'At least 3 characters').max(30, 'Max 30 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'At least 8 characters'),
  password2: z.string().min(1, 'Please confirm your password'),
}).refine((d) => d.password === d.password2, {
  message: 'Passwords do not match',
  path: ['password2'],
})

type FormData = z.infer<typeof schema>

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await registerUser(data)
      await login({ username: data.username, password: data.password })
      toast.success('Account created! Welcome to TravelMind 🎉')
      navigate('/')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: Record<string, string[]> } }
      const msg = Object.values(axiosErr?.response?.data || {}).flat().join(' ') || 'Registration failed'
      toast.error(msg)
    }
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
            Join thousands of<br />smart travellers
          </h2>
          <p className="text-white/70 text-lg max-w-sm">
            Get personalized recommendations, save your favorite destinations, and plan your perfect trip.
          </p>
          <div className="mt-10 space-y-3">
            {['AI-powered destination matching', 'Save & organize favorites', 'Read & write travel reviews'].map((f) => (
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
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Create account</h1>
            <p className="text-slate-500 dark:text-slate-400">Start your travel journey today</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Username"
              placeholder="traveller_jane"
              leftIcon={<User className="w-4 h-4" />}
              error={errors.username?.message}
              {...register('username')}
            />
            <Input
              label="Email"
              type="email"
              placeholder="you@example.com"
              leftIcon={<Mail className="w-4 h-4" />}
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.password?.message}
              helperText="Minimum 8 characters"
              {...register('password')}
            />
            <Input
              label="Confirm Password"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.password2?.message}
              {...register('password2')}
            />

            <Button type="submit" fullWidth isLoading={isSubmitting} leftIcon={<UserPlus className="w-4 h-4" />} size="lg" className="mt-2">
              Create account
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-slate-50 dark:bg-slate-950 px-3 text-slate-400 font-medium tracking-wide">
                Or sign up with
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <GoogleLoginButton />
          </div>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
