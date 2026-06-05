import { useState } from 'react'
import { Star } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

const cn = (...inputs: Parameters<typeof clsx>) => twMerge(clsx(inputs))

const sizes = { sm: 'w-3.5 h-3.5', md: 'w-5 h-5', lg: 'w-6 h-6' }

interface StarRatingProps {
  value: number
  onChange?: (value: number) => void
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export default function StarRating({ value, onChange, size = 'md', showLabel }: StarRatingProps) {
  const [hovered, setHovered] = useState(0)
  const interactive = !!onChange
  const display = hovered || value

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={!interactive}
          onClick={() => onChange?.(star)}
          onMouseEnter={() => interactive && setHovered(star)}
          onMouseLeave={() => interactive && setHovered(0)}
          className={cn(
            'transition-all duration-100',
            interactive && 'hover:scale-110 cursor-pointer',
            !interactive && 'cursor-default'
          )}
        >
          <Star
            className={cn(
              sizes[size],
              display >= star
                ? 'fill-amber-400 text-amber-400'
                : 'text-slate-300 dark:text-slate-600'
            )}
          />
        </button>
      ))}
      {showLabel && (
        <span className="ml-1 text-sm text-slate-500 dark:text-slate-400">
          {value > 0 ? value.toFixed(1) : '—'}
        </span>
      )}
    </div>
  )
}
