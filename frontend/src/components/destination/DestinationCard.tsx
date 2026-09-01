import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Heart, MapPin, DollarSign, Star, Clock, Bookmark, CheckCircle2, ChevronDown } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { Destination } from '@/types/destination'
import type { Review } from '@/types/review'
import { TRAVEL_TYPE_COLORS, DEFAULT_TRAVEL_TYPE_COLOR } from '@/types/destination'
import { getReviews } from '@/services/reviews'
import { useAuth } from '@/hooks/useAuth'
import { useTravelCategories } from '@/hooks/useTaxonomy'
import { translateOrFallback } from '@/utils/translateOrFallback'
import { localizedName, localizedCountry } from '@/utils/localizedDestination'
import ReviewList from '@/components/reviews/ReviewList'
import ReviewForm from '@/components/reviews/ReviewForm'

const FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&auto=format&fit=crop&q=80'

interface Props {
  destination: Destination
  isFavorite?: boolean
  onFavoriteToggle?: (id: number) => void
  isWishlisted?: boolean
  onWishlistToggle?: (id: number) => void
  isVisited?: boolean
  onVisitedToggle?: (id: number) => void
  showScore?: boolean
  score?: number
}

export default function DestinationCard({
  destination,
  isFavorite,
  onFavoriteToggle,
  isWishlisted,
  onWishlistToggle,
  isVisited,
  onVisitedToggle,
  showScore,
  score,
}: Props) {
  const { t, i18n } = useTranslation()
  const { isAuthenticated } = useAuth()
  const { categories } = useTravelCategories()
  const image = destination.images?.[0] || destination.image_url || FALLBACK_IMAGE
  const displayName = localizedName(destination, i18n.language)
  const travelTypeCategory = categories.find((c) => c.slug === destination.travel_type)
  const travelTypeLabel = translateOrFallback(
    t,
    `travelType.${destination.travel_type}`,
    i18n.language === 'mk' && travelTypeCategory?.name_mk ? travelTypeCategory.name_mk : travelTypeCategory?.name || destination.travel_type,
  )

  const [showReviews, setShowReviews] = useState(false)
  const [reviews, setReviews] = useState<Review[]>([])
  const [reviewsLoading, setReviewsLoading] = useState(false)
  const [fetched, setFetched] = useState(false)
  const [reviewCount, setReviewCount] = useState(destination.review_count ?? 0)

  const toggleReviews = async () => {
    if (!showReviews && !fetched) {
      setReviewsLoading(true)
      try {
        const data = await getReviews(destination.id)
        setReviews(data)
        setFetched(true)
      } catch {}
      finally { setReviewsLoading(false) }
    }
    setShowReviews((v) => !v)
  }

  const handleReviewSuccess = (r: Review) => {
    setReviews((prev) => [r, ...prev])
    setReviewCount((c) => c + 1)
  }

  return (
    <motion.div
      whileHover={{ y: showReviews ? 0 : -6 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="group relative rounded-2xl overflow-hidden bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 shadow-sm hover:shadow-xl hover:shadow-slate-200/50 dark:hover:shadow-slate-900/50 transition-shadow duration-300"
    >
      {/* Image */}
      <Link to={`/destination/${destination.slug}`} className="block relative overflow-hidden">
        <div className="aspect-[4/3] overflow-hidden">
          <img
            src={image}
            alt={displayName}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
            onError={(e) => { e.currentTarget.src = FALLBACK_IMAGE }}
          />
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {showScore && score !== undefined && (
          <div className="absolute top-3 left-3 bg-primary-600 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow z-10">
            {t('common.matchBadge', { value: Math.round(score * 100) })}
          </div>
        )}

        <div className={`absolute top-3 ${showScore && score !== undefined ? 'left-28' : 'left-3'} text-xs font-medium px-2.5 py-1 rounded-full z-10 ${TRAVEL_TYPE_COLORS[destination.travel_type as keyof typeof TRAVEL_TYPE_COLORS] || DEFAULT_TRAVEL_TYPE_COLOR}`}>
          {travelTypeLabel}
        </div>

        {isVisited && (
          <div className="absolute bottom-3 left-3 flex items-center gap-1 bg-emerald-600 text-white text-xs font-medium px-2.5 py-1 rounded-full z-10">
            <CheckCircle2 className="w-3 h-3" /> {t('visited.visitedBadge')}
          </div>
        )}
      </Link>

      {/* Action buttons */}
      <div className="absolute top-3 right-3 z-10 flex flex-col gap-1.5">
        <button
          type="button"
          onClick={() => onFavoriteToggle?.(destination.id)}
          className="w-8 h-8 bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow hover:scale-110 transition-transform"
          title={isFavorite ? t('destination.removeFromFavorites') : t('destination.saveToFavorites')}
        >
          <Heart className={`w-4 h-4 transition-all duration-200 ${isFavorite ? 'fill-rose-500 text-rose-500' : 'text-slate-400 hover:text-rose-400'}`} />
        </button>
        {onWishlistToggle && (
          <button
            type="button"
            onClick={() => onWishlistToggle(destination.id)}
            className="w-8 h-8 bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow hover:scale-110 transition-transform"
            title={isWishlisted ? t('destination.removeFromWishlist') : t('destination.addToWishlist')}
          >
            <Bookmark className={`w-4 h-4 transition-all duration-200 ${isWishlisted ? 'fill-violet-500 text-violet-500' : 'text-slate-400 hover:text-violet-400'}`} />
          </button>
        )}
      </div>

      {/* Content */}
      <Link to={`/destination/${destination.slug}`} className="block p-4">
        <h3 className="font-semibold text-slate-900 dark:text-white text-base leading-tight mb-0.5 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
          {displayName}
        </h3>
        <p className="flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400 mb-3">
          <MapPin className="w-3.5 h-3.5 shrink-0" />
          {destination.city ? `${destination.city}, ${localizedCountry(destination, i18n.language)}` : localizedCountry(destination, i18n.language)}
        </p>

        <div className="flex items-center justify-between text-sm">
          <span className="flex items-center gap-1 font-medium text-slate-900 dark:text-white">
            <DollarSign className="w-3.5 h-3.5 text-emerald-500" />
            €{Number(destination.estimated_cost).toLocaleString()}
          </span>
          <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400">
            {destination.trip_duration_min > 0 && (
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {destination.trip_duration_min}–{destination.trip_duration_max}d
              </span>
            )}
            <span className="flex items-center gap-1">
              <Star className={`w-3.5 h-3.5 ${destination.average_rating ? 'fill-amber-400 text-amber-400' : 'text-slate-300 dark:text-slate-600'}`} />
              {destination.average_rating
                ? `${destination.average_rating} (${reviewCount})`
                : `${reviewCount} reviews`}
            </span>
          </div>
        </div>
      </Link>

      {/* Reviews toggle */}
      <button
        type="button"
        onClick={toggleReviews}
        className="w-full flex items-center justify-center gap-1.5 border-t border-slate-100 dark:border-slate-700/50 px-4 py-2.5 text-xs text-primary-600 dark:text-primary-400 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors font-medium"
      >
        <Star className="w-3 h-3" />
        {reviewCount > 0 ? t('destination.reviewsCount', { count: reviewCount }) : t('destination.beFirstToReview')}
        <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${showReviews ? 'rotate-180' : ''}`} />
      </button>

      {/* Inline review panel */}
      <AnimatePresence>
        {showReviews && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden border-t border-slate-100 dark:border-slate-700/50"
          >
            <div className="p-4 space-y-4">
              <ReviewList reviews={reviews} isLoading={reviewsLoading} />
              {isAuthenticated ? (
                <ReviewForm destinationId={destination.id} onSuccess={handleReviewSuccess} />
              ) : (
                <p className="text-xs text-center text-slate-500 dark:text-slate-400 py-2">
                  <Link to="/login" className="text-primary-600 dark:text-primary-400 hover:underline font-medium">{t('destination.signIn')}</Link>
                  {' '}{t('destination.signInToReview')}
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
