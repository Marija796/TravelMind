import { useTranslation } from 'react-i18next'
import StarRating from '@/components/common/StarRating'
import { formatDate } from '@/utils/formatDate'

export interface ReviewLike {
  username: string
  profile_image?: string | null
  rating: number
  comment: string
  created_at: string
}

interface Props {
  review: ReviewLike
  highlight?: boolean
}

export default function ReviewCard({ review, highlight }: Props) {
  const { t } = useTranslation()
  const initials = review.username.slice(0, 2).toUpperCase()
  const date = formatDate(review.created_at)

  return (
    <div
      className={`flex gap-4 py-5 border-b border-slate-100 dark:border-slate-700 last:border-0 ${
        highlight ? 'bg-primary-50/60 dark:bg-primary-900/10 -mx-4 px-4 rounded-xl border-0' : ''
      }`}
    >
      {review.profile_image ? (
        <img
          src={review.profile_image}
          alt={review.username}
          className="w-10 h-10 rounded-full object-cover shrink-0"
        />
      ) : (
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white text-sm font-semibold shrink-0">
          {initials}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <div>
            <span className="font-medium text-slate-900 dark:text-white text-sm">{review.username}</span>
            {highlight && (
              <span className="ml-2 text-[10px] uppercase tracking-wide font-semibold text-primary-600 bg-primary-100 dark:bg-primary-900/40 px-1.5 py-0.5 rounded">
                {t('appReviews.yourReview')}
              </span>
            )}
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
