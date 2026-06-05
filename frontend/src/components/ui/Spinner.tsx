import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

const cn = (...inputs: Parameters<typeof clsx>) => twMerge(clsx(inputs))

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }

export default function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <div
      className={cn(
        'border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin',
        sizes[size],
        className
      )}
    />
  )
}
