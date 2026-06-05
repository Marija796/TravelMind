import { X } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

const cn = (...inputs: Parameters<typeof clsx>) => twMerge(clsx(inputs))

const colors = {
  blue: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  teal: 'bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
  rose: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300',
  emerald: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
  slate: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
  purple: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  orange: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
}

const sizes = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-sm px-2.5 py-1',
}

interface BadgeProps {
  label: string
  color?: keyof typeof colors
  size?: keyof typeof sizes
  removable?: boolean
  onRemove?: () => void
  className?: string
}

export default function Badge({ label, color = 'slate', size = 'sm', removable, onRemove, className }: BadgeProps) {
  return (
    <span className={cn('inline-flex items-center gap-1 font-medium rounded-full', colors[color], sizes[size], className)}>
      {label}
      {removable && (
        <button onClick={onRemove} className="hover:opacity-70 transition-opacity">
          <X className="h-3 w-3" />
        </button>
      )}
    </span>
  )
}
