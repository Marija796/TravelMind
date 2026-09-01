import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { MessageSquare, Pencil, Trash2 } from 'lucide-react'
import { getAppReviews, getMyAppReview, deleteAppReview } from '@/services/appReviews'
import type { AppReview } from '@/types/review'
import { useAuth } from '@/hooks/useAuth'
import StarRating from '@/components/common/StarRating'
import ReviewList from '@/components/reviews/ReviewList'
import AppReviewForm from '@/components/reviews/AppReviewForm'
import Button from '@/components/ui/Button'
import toast from 'react-hot-toast'

export default function AppReviews() {
  const { t } = useTranslation()
  const { user } = useAuth()

  const [reviews, setReviews] = useState<AppReview[]>([])
  const [averageRating, setAverageRating] = useState<number | null>(null)
  const [totalReviews, setTotalReviews] = useState(0)
  const [myReview, setMyReview] = useState<AppReview | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  const load = async () => {
    setIsLoading(true)
    try {
      const [list, mine] = await Promise.all([getAppReviews(), getMyAppReview()])
      setReviews(list.results)
      setAverageRating(list.average_rating)
      setTotalReviews(list.total_reviews)
      setMyReview(mine)
    } catch {
      toast.error(t('appReviews.loadFailed'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleSuccess = () => {
    setShowForm(false)
    load()
  }

  const handleDelete = async () => {
    if (!window.confirm(t('appReviews.confirmDelete'))) return
    try {
      await deleteAppReview()
      setMyReview(null)
      toast.success(t('appReviews.deleted'))
      load()
    } catch {
      toast.error(t('appReviews.deleteFailed'))
    }
  }

  const otherReviews = reviews.filter((r) => !myReview || r.id !== myReview.id)
  const listItems = myReview ? [myReview, ...otherReviews] : otherReviews

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mb-2">
          <MessageSquare className="w-6 h-6 text-primary-500" />
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('appReviews.title')}</h1>
        </div>
        <p className="text-slate-500 dark:text-slate-400 mb-6">{t('appReviews.subtitle')}</p>

        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6 mb-8 flex items-center gap-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-slate-900 dark:text-white">
              {averageRating !== null ? averageRating.toFixed(1) : '—'}
            </p>
            <StarRating value={averageRating || 0} size="sm" />
          </div>
          <div className="text-sm text-slate-500 dark:text-slate-400">
            {t('appReviews.totalReviews', { count: totalReviews })}
          </div>
        </div>

        {myReview && !showForm && (
          <div className="mb-6 flex justify-end">
            <div className="flex gap-2">
              <Button variant="outline" size="sm" leftIcon={<Pencil className="w-3.5 h-3.5" />} onClick={() => setShowForm(true)}>
                {t('appReviews.editReview')}
              </Button>
              <Button variant="danger" size="sm" leftIcon={<Trash2 className="w-3.5 h-3.5" />} onClick={handleDelete}>
                {t('appReviews.deleteReview')}
              </Button>
            </div>
          </div>
        )}

        {(!myReview || showForm) && (
          <div className="mb-8">
            <AppReviewForm existingReview={myReview} onSuccess={handleSuccess} />
          </div>
        )}

        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 px-6">
          <ReviewList
            reviews={listItems}
            isLoading={isLoading}
            emptyMessage={t('appReviews.noReviews')}
            highlightUsername={myReview ? user?.username : undefined}
          />
        </div>
      </div>
    </div>
  )
}
