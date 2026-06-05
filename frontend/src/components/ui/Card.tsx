import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

const cn = (...inputs: Parameters<typeof clsx>) => twMerge(clsx(inputs))

const padding = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

interface CardProps {
  glass?: boolean
  hover?: boolean
  padding?: keyof typeof padding
  children: React.ReactNode
  className?: string
  onClick?: () => void
}

export default function Card({ glass, hover, padding: p = 'md', children, className, onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'rounded-2xl transition-all duration-300',
        glass
          ? 'glass'
          : 'bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 shadow-sm',
        hover && 'hover:-translate-y-1 hover:shadow-xl cursor-pointer',
        padding[p],
        className
      )}
    >
      {children}
    </div>
  )
}
