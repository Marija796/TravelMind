import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

const cn = (...inputs: Parameters<typeof clsx>) => twMerge(clsx(inputs))

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'rectangular' | 'circular'
}

export default function Skeleton({ className, variant = 'rectangular' }: SkeletonProps) {
  return (
    <div
      className={cn(
        'relative overflow-hidden bg-slate-200 dark:bg-slate-700',
        variant === 'text' && 'rounded h-4',
        variant === 'rectangular' && 'rounded-xl',
        variant === 'circular' && 'rounded-full',
        className
      )}
    >
      <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/30 dark:via-white/10 to-transparent" />
    </div>
  )
}
