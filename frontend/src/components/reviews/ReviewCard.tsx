import { useTranslation } from 'react-i18next'
import type { Review } from '@/types/review'
import StarRating from '@/components/common/StarRating'

interface Props { review: Review }

export default function ReviewCard({ review }: Props) {
  const { i18n } = useTranslation()
  const initials = review.username.slice(0, 2).toUpperCase()
  const locale = i18n.language === 'mk' ? 'mk-MK' : 'en-US'
  const date = new Date(review.created_at).toLocaleDateString(locale, { year: 'numeric', month: 'short', day: 'numeric' })

  return (
    <div className="flex gap-4 py-5 border-b border-slate-100 dark:border-slate-700 last:border-0">
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white text-sm font-semibold shrink-0">
        {initials}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <div>
            <span className="font-medium text-slate-900 dark:text-white text-sm">{review.username}</span>
            <span className="text-xs text-slate-400 ml-2">{date}</span>
          </div>
          <StarRating value={review.rating} size="sm" />
        </div>
        {review.comment && (
          <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{review.comment}</p>
        )}
      </div>
    </div>
  )
}
