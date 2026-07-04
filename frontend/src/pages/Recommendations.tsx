import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sparkles, RefreshCw, Settings } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { ScoredDestination } from '@/types/recommendation'
import type { TravelType, Season } from '@/types/destination'
import { getRecommendations, getAnonymousRecommendations } from '@/services/recommendations'
import { updateProfile } from '@/services/users'
import { useAuth } from '@/hooks/useAuth'
import { useFavorites } from '@/hooks/useFavorites'
import { ACTIVITY_OPTIONS } from '@/types/destination'
import DestinationCard from '@/components/destination/DestinationCard'
import DestinationSkeleton from '@/components/destination/DestinationSkeleton'
import PreferenceSelector from '@/components/common/PreferenceSelector'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import toast from 'react-hot-toast'

const TravelTypeOptions: Array<{ value: TravelType; label: string }> = [
  { value: 'beach', label: 'Beach' },
  { value: 'mountain', label: 'Mountain' },
  { value: 'city', label: 'City' },
  { value: 'adventure', label: 'Adventure' },
  { value: 'cultural', label: 'Cultural' },
  { value: 'luxury', label: 'Luxury' },
  { value: 'relaxation', label: 'Relaxation' },
]

const SeasonOptions: Array<{ value: Season; label: string }> = [
  { value: 'spring', label: 'Spring' },
  { value: 'summer', label: 'Summer' },
  { value: 'autumn', label: 'Autumn' },
  { value: 'winter', label: 'Winter' },
]

export default function Recommendations() {
  const { t } = useTranslation()
  const { user, isAuthenticated } = useAuth()
  const { favoriteIds, toggle } = useFavorites(user?.favorite_destination_ids)
  const [results, setResults] = useState<ScoredDestination[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showPrefs, setShowPrefs] = useState(false)
  const [hasFetched, setHasFetched] = useState(false)
  const [showAll, setShowAll] = useState(false)

  const [travelType, setTravelType] = useState<TravelType | ''>(user?.preferred_travel_type || '')
  const [season, setSeason] = useState<Season | ''>(user?.preferred_season || '')
  const [activities, setActivities] = useState<string[]>(user?.preferred_activities || [])
  const [budget, setBudget] = useState(user?.budget || '')
  const [duration, setDuration] = useState<string>(user?.trip_duration_preference ? String(user.trip_duration_preference) : '')

  const hasPrefs = !!(user?.preferred_travel_type || user?.budget || user?.preferred_season)

  const fetchRecs = async () => {
    setIsLoading(true)
    setHasFetched(true)
    setShowAll(false)
    try {
      const data = await getRecommendations()
      setResults(data.results)
    } catch {
      toast.error('Failed to load recommendations')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchAnonymousRecs = async () => {
    setIsLoading(true)
    setHasFetched(true)
    setShowAll(false)
    try {
      const params: Record<string, string> = {}
      if (travelType) params.travel_type = travelType
      if (budget) params.budget = String(budget)
      if (season) params.season = season
      if (activities.length) params.activities = activities.join(',')
      const data = await getAnonymousRecommendations(params)
      setResults(data.results)
    } catch {
      toast.error('Failed to load recommendations')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!isAuthenticated) return
    if (hasPrefs) fetchRecs()
    else setShowPrefs(true)
  }, [isAuthenticated])

  const savePrefs = async () => {
    try {
      await updateProfile({
        preferred_travel_type: travelType,
        preferred_season: season,
        preferred_activities: activities,
        budget: budget ? String(budget) : null,
        trip_duration_preference: duration ? Number(duration) : null,
      })
      toast.success('Preferences saved!')
      setShowPrefs(false)
      await fetchRecs()
    } catch {
      toast.error('Failed to save preferences')
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="pt-24 pb-16 min-h-screen">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center justify-center gap-3 mb-2">
              <Sparkles className="w-7 h-7 text-amber-500" />
              {t('recommendations.guestTitle')}
            </h1>
            <p className="text-slate-500 dark:text-slate-400">{t('recommendations.guestSubtitle')}</p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6 space-y-6 mb-8">
            <PreferenceSelector
              label={t('recommendations.travelType')}
              options={TravelTypeOptions}
              selected={travelType ? [travelType] : []}
              onChange={(v) => setTravelType(v[0] as TravelType || '')}
              singleSelect
            />
            <PreferenceSelector
              label={t('recommendations.bestSeason')}
              options={SeasonOptions}
              selected={season ? [season] : []}
              onChange={(v) => setSeason(v[0] as Season || '')}
              singleSelect
            />
            <PreferenceSelector
              label={t('recommendations.activities')}
              options={ACTIVITY_OPTIONS.map((a) => ({ value: a, label: a }))}
              selected={activities}
              onChange={setActivities}
            />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label={t('recommendations.maxBudget')}
                type="number"
                placeholder="e.g. 3000"
                value={budget || ''}
                onChange={(e) => setBudget(e.target.value)}
              />
            </div>
            <Button onClick={fetchAnonymousRecs} leftIcon={<Sparkles className="w-4 h-4" />} isLoading={isLoading}>
              {t('recommendations.getMyRecs')}
            </Button>
          </div>

          {hasFetched && results.length > 0 && (
            <>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">{t(results.length === 1 ? 'recommendations.matchedCount' : 'recommendations.matchedCountPlural', { count: results.length })}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {(showAll ? results : results.slice(0, 3)).map((dest, i) => (
                  <motion.div key={dest.id} initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.07 }}>
                    <DestinationCard destination={dest} showScore score={dest.score} />
                    {(dest.match_quality || dest.match_explanation) && (
                      <div className="mt-2 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700 px-3 py-2.5 space-y-1">
                        {dest.match_quality && (
                          <p className="text-xs font-semibold text-primary-600 dark:text-primary-400">{dest.match_quality}</p>
                        )}
                        {dest.match_explanation && (
                          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{dest.match_explanation}</p>
                        )}
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
              {results.length > 3 && (
                <div className="mt-6 text-center">
                  <Button variant="secondary" size="sm" onClick={() => setShowAll((v) => !v)}>
                    {showAll ? t('recommendations.showLess') : t('recommendations.showMore', { count: results.length - 3 })}
                  </Button>
                </div>
              )}
              <div className="mt-8 text-center">
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">{t('recommendations.signInForPersonalized')}</p>
                <Link to="/register">
                  <Button leftIcon={<Sparkles className="w-4 h-4" />}>{t('home.createFreeAccount')}</Button>
                </Link>
              </div>
            </>
          )}

          {hasFetched && results.length === 0 && !isLoading && (
            <div className="text-center py-12">
              <p className="text-4xl mb-3">🔍</p>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-1">{t('recommendations.noMatches')}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('recommendations.noMatchesHint')}</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
              <Sparkles className="w-7 h-7 text-amber-500" />
              {t('recommendations.title')}
            </h1>
            <p className="text-slate-500 dark:text-slate-400 mt-1">{t('recommendations.subtitle')}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" leftIcon={<Settings className="w-4 h-4" />} onClick={() => setShowPrefs(!showPrefs)}>
              {t('recommendations.preferences')}
            </Button>
            {hasFetched && (
              <Button variant="secondary" size="sm" leftIcon={<RefreshCw className="w-4 h-4" />} onClick={fetchRecs} isLoading={isLoading}>
                {t('recommendations.refresh')}
              </Button>
            )}
          </div>
        </div>

        {/* Preferences panel */}
        {showPrefs && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6 mb-8 space-y-6"
          >
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t('recommendations.setPreferences')}</h2>

            <PreferenceSelector
              label={t('recommendations.travelType')}
              options={TravelTypeOptions}
              selected={travelType ? [travelType] : []}
              onChange={(v) => setTravelType(v[0] as TravelType || '')}
              singleSelect
            />

            <PreferenceSelector
              label={t('recommendations.bestSeason')}
              options={SeasonOptions}
              selected={season ? [season] : []}
              onChange={(v) => setSeason(v[0] as Season || '')}
              singleSelect
            />

            <PreferenceSelector
              label={t('recommendations.activities')}
              options={ACTIVITY_OPTIONS.map((a) => ({ value: a, label: a }))}
              selected={activities}
              onChange={setActivities}
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label={t('recommendations.maxBudget')}
                type="number"
                placeholder="e.g. 3000"
                value={budget || ''}
                onChange={(e) => setBudget(e.target.value)}
              />
              <Input
                label={t('recommendations.tripDuration')}
                type="number"
                placeholder="e.g. 10"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
            </div>

            <Button onClick={savePrefs} leftIcon={<Sparkles className="w-4 h-4" />}>
              {t('recommendations.getRecommendations')}
            </Button>
          </motion.div>
        )}

        {/* Results */}
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => <DestinationSkeleton key={i} />)}
          </div>
        ) : hasFetched && results.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-5xl mb-4">🔍</p>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">{t('recommendations.noMatches')}</h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6">{t('recommendations.noMatchesHint')}</p>
            <Button onClick={() => setShowPrefs(true)}>{t('recommendations.updatePreferences')}</Button>
          </div>
        ) : results.length > 0 ? (
          <>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">{t(results.length === 1 ? 'recommendations.matchedCount' : 'recommendations.matchedCountPlural', { count: results.length })}</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {(showAll ? results : results.slice(0, 3)).map((dest, i) => (
                <motion.div
                  key={dest.id}
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.07, duration: 0.35 }}
                >
                  <div className="relative">
                    <DestinationCard
                      destination={dest}
                      isFavorite={favoriteIds.has(dest.id)}
                      onFavoriteToggle={toggle}
                      showScore
                      score={dest.score}
                    />
                    <div className="mt-2 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700 overflow-hidden">
                      {(dest.match_quality || dest.match_explanation) && (
                        <div className="px-3 py-2.5 border-b border-slate-100 dark:border-slate-700 space-y-1">
                          {dest.match_quality && (
                            <p className="text-xs font-semibold text-primary-600 dark:text-primary-400">{dest.match_quality}</p>
                          )}
                          {dest.match_explanation && (
                            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{dest.match_explanation}</p>
                          )}
                        </div>
                      )}
                      <div className="px-3 py-2 grid grid-cols-2 gap-x-4 gap-y-1">
                        {Object.entries(dest.score_breakdown).map(([k, v]) => (
                          <div key={k} className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
                            <span className="capitalize">{k.replace(/_/g, ' ')}</span>
                            <span className={`font-medium ${v > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>+{v}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            {results.length > 3 && (
              <div className="mt-8 text-center">
                <Button variant="secondary" onClick={() => setShowAll((v) => !v)}>
                  {showAll ? t('recommendations.showLess') : t('recommendations.showMore', { count: results.length - 3 })}
                </Button>
              </div>
            )}
          </>
        ) : !showPrefs ? (
          <div className="text-center py-20">
            <p className="text-5xl mb-4">✈️</p>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">{t('recommendations.setYourPreferences')}</h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6">{t('recommendations.setPrefsHint')}</p>
            <Button onClick={() => setShowPrefs(true)} leftIcon={<Settings className="w-4 h-4" />}>
              {t('recommendations.setPrefsButton')}
            </Button>
          </div>
        ) : null}
      </div>
    </div>
  )
}
