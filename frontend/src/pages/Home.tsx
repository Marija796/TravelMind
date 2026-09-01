import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { ArrowRight, Sparkles } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { Destination } from '@/types/destination'
import type { ScoredDestination } from '@/types/recommendation'
import { getFeaturedDestinations } from '@/services/destinations'
import { getRecommendations } from '@/services/recommendations'
import { useAuth } from '@/hooks/useAuth'
import { useFavorites } from '@/hooks/useFavorites'
import DestinationGrid from '@/components/destination/DestinationGrid'
import DestinationCard from '@/components/destination/DestinationCard'
import DestinationSkeleton from '@/components/destination/DestinationSkeleton'
import Button from '@/components/ui/Button'

function CountUp({ target, suffix = '' }: { target: number; suffix?: string }) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const inView = useInView(ref, { once: true })

  useEffect(() => {
    if (!inView) return
    let start = 0
    const step = Math.ceil(target / 40)
    const timer = setInterval(() => {
      start += step
      if (start >= target) { setCount(target); clearInterval(timer) }
      else setCount(start)
    }, 30)
    return () => clearInterval(timer)
  }, [inView, target])

  return <span ref={ref}>{count}{suffix}</span>
}

export default function Home() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuth()
  const { favoriteIds, toggle } = useFavorites(user?.favorite_destination_ids)
  const [featured, setFeatured] = useState<Destination[]>([])
  const [loading, setLoading] = useState(true)
  const [recommendations, setRecommendations] = useState<ScoredDestination[]>([])
  const [recsLoading, setRecsLoading] = useState(false)
  const [searchInput, setSearchInput] = useState('')

  const featuredRef = useRef(null)
  const featuredInView = useInView(featuredRef, { once: true, margin: '-100px' })

  useEffect(() => {
    // Destination browsing (like every other feature) requires an account
    // now that guest access has been removed - an unauthenticated visitor
    // would just get a 401 from this call, so skip it and let the section
    // below stay hidden for them instead.
    if (!isAuthenticated) { setLoading(false); return }
    getFeaturedDestinations()
      .then((d) => setFeatured(d.results.slice(0, 6)))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [isAuthenticated])

  useEffect(() => {
    if (!isAuthenticated || !user?.preferred_travel_type) return
    setRecsLoading(true)
    getRecommendations()
      .then((d) => setRecommendations(d.results.slice(0, 3)))
      .catch(() => {})
      .finally(() => setRecsLoading(false))
  }, [isAuthenticated, user?.preferred_travel_type])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    navigate(`/explore${searchInput ? `?search=${encodeURIComponent(searchInput)}` : ''}`)
  }

  return (
    <div className="overflow-x-hidden">
      {/* Hero */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-950 via-primary-900 to-accent-900 animate-gradient-shift bg-[length:300%_300%]" />
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1488085061387-422e29b40080?w=1600&auto=format')] bg-cover bg-center opacity-10" />

        {/* Floating orbs */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-accent-500/20 rounded-full blur-3xl animate-float [animation-delay:1.5s]" />

        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center pt-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: 'easeOut' }}
          >
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-4 py-2 text-white/80 text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4 text-amber-400" />
              {t('home.heroTag')}
            </div>
            <h1 className="text-5xl sm:text-7xl font-bold text-white leading-tight mb-6 text-balance">
              {t('home.heroTitle')}
              <br />
              <span className="bg-gradient-to-r from-amber-300 to-orange-400 bg-clip-text text-transparent">
                {t('home.heroTitleHighlight')}
              </span>
            </h1>
            <p className="text-white/70 text-lg sm:text-xl max-w-2xl mx-auto mb-10 text-balance">
              {t('home.heroSubtitle')}
            </p>
          </motion.div>

          {/* Search bar */}
          <motion.form
            onSubmit={handleSearch}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="flex gap-3 max-w-xl mx-auto mb-8"
          >
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder={t('home.searchPlaceholder')}
              className="flex-1 h-12 px-5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-white/30 text-sm"
            />
            <button
              type="submit"
              className="h-12 px-6 bg-white text-primary-800 font-semibold rounded-2xl hover:bg-white/90 transition-colors text-sm"
            >
              {t('home.searchButton')}
            </button>
          </motion.form>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="flex flex-wrap items-center justify-center gap-3"
          >
            <Button
              variant="primary"
              size="lg"
              rightIcon={<ArrowRight className="w-4 h-4" />}
              onClick={() => navigate('/explore')}
              className="bg-white/10 backdrop-blur border-white/20 hover:bg-white/20 border"
            >
              {t('home.exploreAll')}
            </Button>
            {isAuthenticated ? (
              <Button
                size="lg"
                rightIcon={<Sparkles className="w-4 h-4" />}
                onClick={() => navigate('/recommendations')}
              >
                {t('home.getMyPicks')}
              </Button>
            ) : (
              <Button size="lg" onClick={() => navigate('/register')}>
                {t('home.getStartedFree')}
              </Button>
            )}
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 w-6 h-10 border-2 border-white/30 rounded-full flex justify-center pt-2"
        >
          <div className="w-1 h-2 bg-white/50 rounded-full" />
        </motion.div>
      </section>

      {/* Stats */}
      <section className="py-16 bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
            {[
              { value: 100, suffix: '+', label: t('home.destinations') },
              { value: 7, suffix: '', label: t('home.travelTypes') },
              { value: 50, suffix: '+', label: t('home.countries') },
              { value: 5, suffix: '★', label: t('home.avgRating') },
            ].map(({ value, suffix, label }) => (
              <div key={label}>
                <p className="text-4xl font-bold gradient-text mb-1">
                  <CountUp target={value} suffix={suffix} />
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Destinations - requires an account, like all browsing now does */}
      {isAuthenticated && (
        <section ref={featuredRef} className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={featuredInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5 }}
              className="flex items-end justify-between mb-10 flex-wrap gap-4"
            >
              <div>
                <p className="text-sm font-medium text-primary-600 mb-1">{t('home.topPicks')}</p>
                <h2 className="text-3xl font-bold text-slate-900 dark:text-white">{t('home.trendingTitle')}</h2>
              </div>
              <Button variant="secondary" rightIcon={<ArrowRight className="w-4 h-4" />} onClick={() => navigate('/explore')}>
                {t('home.viewAll')}
              </Button>
            </motion.div>

            <DestinationGrid
              destinations={featured}
              isLoading={loading}
              skeletonCount={6}
              favoriteIds={favoriteIds}
              onFavoriteToggle={toggle}
            />
          </div>
        </section>
      )}

      {/* Personalized Recommendations — only for authenticated users with preferences */}
      {isAuthenticated && (recommendations.length > 0 || recsLoading) && (
        <section className="py-20 bg-slate-50 dark:bg-slate-950/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-end justify-between mb-10 flex-wrap gap-4">
              <div>
                <p className="text-sm font-medium text-amber-600 mb-1 flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4" /> {t('home.personalizedFor')}
                </p>
                <h2 className="text-3xl font-bold text-slate-900 dark:text-white">{t('home.recommendedTitle')}</h2>
              </div>
              <Button variant="secondary" rightIcon={<ArrowRight className="w-4 h-4" />} onClick={() => navigate('/recommendations')}>
                {t('home.seeAllPicks')}
              </Button>
            </div>
            {recsLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => <DestinationSkeleton key={i} />)}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                {recommendations.map((dest, i) => (
                  <motion.div
                    key={dest.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <DestinationCard
                      destination={dest}
                      isFavorite={favoriteIds.has(dest.id)}
                      onFavoriteToggle={toggle}
                      showScore
                      score={dest.score}
                    />
                    {dest.match_explanation && (
                      <div className="mt-2 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700 px-3 py-2.5">
                        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{dest.match_explanation}</p>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </section>
      )}

      {/* CTA Banner */}
      {!isAuthenticated && (
        <section className="py-20 bg-gradient-to-br from-primary-600 to-accent-600">
          <div className="max-w-2xl mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">{t('home.ctaTitle')}</h2>
            <p className="text-white/80 mb-8 text-lg">
              {t('home.ctaSubtitle')}
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Button size="lg" className="bg-white text-primary-700 hover:bg-white/90" onClick={() => navigate('/register')}>
                {t('home.createFreeAccount')}
              </Button>
              <Button variant="ghost" size="lg" className="text-white hover:bg-white/10 border border-white/30" onClick={() => navigate('/explore')}>
                {t('home.browseDestinations')}
              </Button>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
