import { useTranslation } from 'react-i18next'
import type { Review } from '@/types/review'
import ReviewCard from './ReviewCard'
import Skeleton from '@/components/ui/Skeleton'

interface Props {
  reviews: Review[]
  isLoading?: boolean
}

export default function ReviewList({ reviews, isLoading }: Props) {
  const { t } = useTranslation()

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-4 py-4">
            <Skeleton variant="circular" className="w-10 h-10 shrink-0" />
            <div className="flex-1 space-y-2">
              <Skeleton variant="text" className="w-1/3 h-4" />
              <Skeleton variant="text" className="w-full h-3" />
              <Skeleton variant="text" className="w-2/3 h-3" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (reviews.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400 py-6 text-center">
        {t('review.noReviews')}
      </p>
    )
  }

  return (
    <div>
      {reviews.map((r) => <ReviewCard key={r.id} review={r} />)}
    </div>
  )
}
