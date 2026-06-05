import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowLeft, MapPin, DollarSign, Compass, Sun, Clock, BarChart2, Heart, Bookmark, CheckCircle2 } from 'lucide-react'
import type { Destination } from '@/types/destination'
import type { Review } from '@/types/review'
import { getDestinationBySlug } from '@/services/destinations'
import { getReviews } from '@/services/reviews'
import { addFavorite, removeFavorite } from '@/services/favorites'
import { addToWishlist, removeFromWishlist } from '@/services/wishlist'
import { markVisited, removeFromVisited } from '@/services/visited'
import { useAuth } from '@/hooks/useAuth'
import { TRAVEL_TYPE_COLORS } from '@/types/destination'
import ActivityChip from '@/components/destination/ActivityChip'
import RelatedDestinations from '@/components/destination/RelatedDestinations'
import ReviewList from '@/components/reviews/ReviewList'
import ReviewForm from '@/components/reviews/ReviewForm'
import StarRating from '@/components/common/StarRating'
import Skeleton from '@/components/ui/Skeleton'
import Button from '@/components/ui/Button'
import toast from 'react-hot-toast'

const FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200&auto=format&fit=crop&q=80'

export default function DestinationDetail() {
  const { t, i18n } = useTranslation()
  const { slug } = useParams<{ slug: string }>()
  const { isAuthenticated, user } = useAuth()
  const [destination, setDestination] = useState<Destination | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [loadingDest, setLoadingDest] = useState(true)
  const [loadingReviews, setLoadingReviews] = useState(false)
  const [loadError, setLoadError] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [isFav, setIsFav] = useState(false)
  const [favLoading, setFavLoading] = useState(false)
  const [isWishlisted, setIsWishlisted] = useState(false)
  const [wishlistLoading, setWishlistLoading] = useState(false)
  const [isVisited, setIsVisited] = useState(false)
  const [visitedLoading, setVisitedLoading] = useState(false)
  const [activeImage, setActiveImage] = useState(0)

  useEffect(() => {
    if (!slug) return
    let cancelled = false
    setLoadingDest(true)
    setLoadError(false)
    setErrorMsg('')
    setDestination(null)
    setReviews([])
    getDestinationBySlug(slug)
      .then((d) => {
        if (cancelled) return
        setDestination(d)
        setIsFav(d.is_favorited || (user?.favorite_destination_ids?.includes(d.id) ?? false))
        setIsWishlisted(d.is_wishlisted || (user?.wishlist_destination_ids?.includes(d.id) ?? false))
        setIsVisited(d.is_visited || (user?.visited_destination_ids?.includes(d.id) ?? false))
        setLoadingReviews(true)
        getReviews(d.id)
          .then((r) => { if (!cancelled) setReviews(r) })
          .catch(() => {})
          .finally(() => { if (!cancelled) setLoadingReviews(false) })
      })
      .catch((err) => {
        if (cancelled) return
        const status = err?.response?.status
        if (status === 404) {
          setErrorMsg('This destination does not exist.')
        } else if (!status) {
          setErrorMsg('Cannot connect to the server. Make sure Django is running on port 8000.')
        } else {
          setErrorMsg(`Server error (${status}). Please try again.`)
        }
        setLoadError(true)
      })
      .finally(() => { if (!cancelled) setLoadingDest(false) })
    return () => { cancelled = true }
  }, [slug, user])

  const toggleFav = async () => {
    if (!isAuthenticated) { toast.error('Please log in to save favorites'); return }
    if (!destination) return
    setFavLoading(true)
    try {
      if (isFav) { await removeFavorite(destination.id); toast.success('Removed from favorites') }
      else { await addFavorite(destination.id); toast.success('Saved to favorites') }
      setIsFav(!isFav)
    } catch { toast.error('Failed to update') }
    finally { setFavLoading(false) }
  }

  const toggleWishlist = async () => {
    if (!isAuthenticated) { toast.error('Please log in to use wishlist'); return }
    if (!destination) return
    setWishlistLoading(true)
    try {
      if (isWishlisted) { await removeFromWishlist(destination.id); toast.success('Removed from wishlist') }
      else { await addToWishlist(destination.id); toast.success('Added to wishlist') }
      setIsWishlisted(!isWishlisted)
    } catch { toast.error('Failed to update wishlist') }
    finally { setWishlistLoading(false) }
  }

  const toggleVisited = async () => {
    if (!isAuthenticated) { toast.error('Please log in to mark visited'); return }
    if (!destination) return
    setVisitedLoading(true)
    try {
      if (isVisited) { await removeFromVisited(destination.id); toast.success('Removed from visited') }
      else { await markVisited(destination.id); toast.success('Marked as visited!') }
      setIsVisited(!isVisited)
    } catch { toast.error('Failed to update') }
    finally { setVisitedLoading(false) }
  }

  const images = destination
    ? (destination.images?.length ? destination.images : destination.image_url ? [destination.image_url] : [])
    : []

  if (loadingDest) {
    return (
      <div className="pt-16">
        <Skeleton className="w-full h-96" />
        <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
          <Skeleton variant="text" className="w-1/2 h-10" />
          <Skeleton variant="text" className="w-1/3 h-6" />
          <Skeleton className="h-40" />
        </div>
      </div>
    )
  }

  if (!destination || loadError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 text-center bg-slate-50 dark:bg-slate-950">
        <div className="max-w-md">
          <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
            <MapPin className="w-10 h-10 text-slate-400" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">
            {t('destination.notFound')}
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mb-4 text-base leading-relaxed">
            {errorMsg || t('destination.notFoundHint')}
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/explore">
              <Button>{t('destination.exploreAllBtn')}</Button>
            </Link>
            <Link to="/">
              <Button variant="secondary">{t('destination.goHome')}</Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const heroImage = images[activeImage] || FALLBACK_IMAGE

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <div className="relative h-[55vh] min-h-[380px] overflow-hidden">
        <img src={heroImage} alt={destination.name} className="w-full h-full object-cover" onError={(e) => { e.currentTarget.src = FALLBACK_IMAGE }} />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />

        {/* Back button */}
        <Link to="/explore" className="absolute top-20 left-6 flex items-center gap-2 text-white/90 hover:text-white bg-black/20 backdrop-blur-sm px-3 py-2 rounded-xl text-sm font-medium transition-colors">
          <ArrowLeft className="w-4 h-4" /> {t('destination.backToExplore')}
        </Link>

        {/* Thumbnail strip */}
        {images.length > 1 && (
          <div className="absolute bottom-20 right-6 flex gap-1.5">
            {images.slice(0, 4).map((img, i) => (
              <button
                key={i}
                onClick={() => setActiveImage(i)}
                className={`w-12 h-9 rounded-lg overflow-hidden border-2 transition-all ${
                  i === activeImage ? 'border-white' : 'border-transparent opacity-70'
                }`}
              >
                <img src={img} className="w-full h-full object-cover" onError={(e) => { e.currentTarget.src = FALLBACK_IMAGE }} />
              </button>
            ))}
          </div>
        )}

        {/* Title overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-10">
          <div className="max-w-5xl mx-auto">
            <div className={`inline-flex text-xs font-medium px-2.5 py-1 rounded-full mb-3 ${TRAVEL_TYPE_COLORS[destination.travel_type]}`}>
              {t(`travelType.${destination.travel_type}`)}
            </div>
            <h1 className="text-3xl sm:text-5xl font-bold text-white mb-1">{destination.name}</h1>
            <p className="flex items-center gap-1.5 text-white/80 text-lg">
              <MapPin className="w-4 h-4" /> {destination.country}
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Info grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          {[
            { icon: <DollarSign className="w-5 h-5 text-emerald-500" />, label: t('destination.estimatedCost'), value: `€${Number(destination.estimated_cost).toLocaleString()}` },
            { icon: <Sun className="w-5 h-5 text-amber-500" />, label: t('destination.bestSeason'), value: destination.best_season ? t(`season.${destination.best_season}`) : '—' },
            { icon: <Clock className="w-5 h-5 text-blue-500" />, label: t('destination.duration'), value: `${destination.trip_duration_min}–${destination.trip_duration_max} ${t('destination.days')}` },
            { icon: <BarChart2 className="w-5 h-5 text-purple-500" />, label: t('destination.difficulty'), value: t(`filter.${destination.difficulty_level}`) },
          ].map((item) => (
            <div key={item.label} className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-4 text-center">
              <div className="flex justify-center mb-2">{item.icon}</div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-0.5">{item.label}</p>
              <p className="font-semibold text-slate-900 dark:text-white text-sm">{item.value}</p>
            </div>
          ))}
        </div>

        {/* Price breakdown from Macedonia */}
        {destination.cost_breakdown && (
          <div className="mb-8 bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-5">
            <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-emerald-500" />
              {t('destination.priceFromSkopje')}
            </h2>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{t('destination.returnFlight')}</p>
                <p className="font-semibold text-slate-900 dark:text-white">€{destination.cost_breakdown.flight.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{t('destination.accommodationNights', { nights: destination.cost_breakdown.nights })}</p>
                <p className="font-semibold text-slate-900 dark:text-white">€{destination.cost_breakdown.accommodation.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{t('destination.foodActivities', { nights: destination.cost_breakdown.nights })}</p>
                <p className="font-semibold text-slate-900 dark:text-white">€{destination.cost_breakdown.daily_expenses.toLocaleString()}</p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 flex justify-between items-center">
              <span className="text-xs text-slate-400 dark:text-slate-500">{t('destination.priceNote')}</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400 text-base">
                {t('destination.totalApprox')} €{Number(destination.estimated_cost).toLocaleString()}
              </span>
            </div>
          </div>
        )}

        {/* Rating + Actions */}
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <StarRating value={destination.average_rating || 0} size="lg" showLabel />
            <span className="text-sm text-slate-500 dark:text-slate-400">
              {destination.review_count} review{destination.review_count !== 1 ? 's' : ''}
            </span>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              variant={isFav ? 'danger' : 'secondary'}
              leftIcon={<Heart className={`w-4 h-4 ${isFav ? 'fill-white' : ''}`} />}
              onClick={toggleFav}
              isLoading={favLoading}
            >
              {isFav ? t('destination.saved') : t('destination.saveToFavorites')}
            </Button>
            <Button
              variant="secondary"
              leftIcon={<Bookmark className={`w-4 h-4 ${isWishlisted ? 'fill-violet-500 text-violet-500' : ''}`} />}
              onClick={toggleWishlist}
              isLoading={wishlistLoading}
            >
              {isWishlisted ? t('destination.wishlisted') : t('destination.addToWishlist')}
            </Button>
            <Button
              variant="secondary"
              leftIcon={<CheckCircle2 className={`w-4 h-4 ${isVisited ? 'text-emerald-500' : ''}`} />}
              onClick={toggleVisited}
              isLoading={visitedLoading}
            >
              {isVisited ? t('destination.visitedCheck') : t('destination.markVisited')}
            </Button>
          </div>
        </div>

        {/* Description */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{t('destination.about')}</h2>
          <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-base">
            {i18n.language === 'mk' && destination.description_mk ? destination.description_mk : destination.description}
          </p>
        </div>

        {/* Activities */}
        {destination.activities?.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <Compass className="w-5 h-5 text-primary-500" /> {t('destination.activities')}
            </h2>
            <div className="flex flex-wrap gap-2">
              {destination.activities.map((a) => <ActivityChip key={a} label={a} />)}
            </div>
          </div>
        )}

        {/* Attractions */}
        {destination.attractions && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{t('destination.attractions')}</h2>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{destination.attractions}</p>
          </div>
        )}

        {/* Travel Tips */}
        {destination.travel_tips && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <span className="text-amber-500">💡</span> {t('destination.travelTips')}
            </h2>
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40 rounded-2xl p-5">
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{destination.travel_tips}</p>
            </div>
          </div>
        )}

        {/* Reviews */}
        <div id="reviews" className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">{t('destination.reviews')}</h2>
          <ReviewList reviews={reviews} isLoading={loadingReviews} />
          {isAuthenticated && (
            <div className="mt-6">
              <ReviewForm
                destinationId={destination.id}
                onSuccess={(r) => setReviews((prev) => [r, ...prev])}
              />
            </div>
          )}
          {!isAuthenticated && (
            <p className="mt-4 text-sm text-slate-500 dark:text-slate-400 text-center py-4">
              <Link to="/login" className="text-primary-600 hover:underline font-medium">{t('destination.signIn')}</Link>{' '}{t('destination.signInToReview')}
            </p>
          )}
        </div>

        {/* Related destinations */}
        <RelatedDestinations travelType={destination.travel_type} excludeId={destination.id} />
      </div>
    </div>
  )
}
