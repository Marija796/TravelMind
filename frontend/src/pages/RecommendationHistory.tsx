import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { History, ChevronLeft, ChevronRight } from 'lucide-react'
import { getRecommendationHistory } from '@/services/recommendationHistory'
import type { RecommendationHistoryEntry } from '@/types/recommendationHistory'
import { useTravelCategories, useSeasons } from '@/hooks/useTaxonomy'
import { translateOrFallback } from '@/utils/translateOrFallback'
import { localizedName } from '@/utils/localizedDestination'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Skeleton from '@/components/ui/Skeleton'

const PAGE_SIZE = 12

export default function RecommendationHistory() {
  const { t, i18n } = useTranslation()
  const [entries, setEntries] = useState<RecommendationHistoryEntry[]>([])
  const [count, setCount] = useState(0)
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const { categories } = useTravelCategories()
  const { seasons } = useSeasons()

  useEffect(() => {
    setIsLoading(true)
    getRecommendationHistory(page)
      .then((data) => { setEntries(data.results); setCount(data.count) })
      .catch(() => {})
      .finally(() => setIsLoading(false))
  }, [page])

  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE))

  const typeLabel = (slug: string | null) => {
    if (!slug) return null
    const c = categories.find((cat) => cat.slug === slug)
    return translateOrFallback(t, `travelType.${slug}`, (i18n.language === 'mk' && c?.name_mk ? c.name_mk : c?.name) || slug)
  }
  const seasonLabel = (slug: string | null) => {
    if (!slug) return null
    const s = seasons.find((season) => season.slug === slug)
    return translateOrFallback(t, `season.${slug}`, (i18n.language === 'mk' && s?.name_mk ? s.name_mk : s?.name) || slug)
  }

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mb-2">
          <History className="w-6 h-6 text-primary-500" />
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('history.title')}</h1>
        </div>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('history.subtitle')}</p>

        {isLoading ? (
          <div className="space-y-4">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-40 rounded-2xl" />)}</div>
        ) : entries.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-4">🕓</p>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">{t('history.empty')}</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">{t('history.emptyHint')}</p>
            <Link to="/recommendations">
              <Button>{t('recommendations.setPrefsButton')}</Button>
            </Link>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {entries.map((entry) => {
                const prefs = entry.preferences_snapshot
                return (
                  <Card key={entry.id} padding="md">
                    <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {t('history.searchedOn', { date: new Date(entry.created_at).toLocaleString(i18n.language) })}
                      </p>
                      <span className="text-xs text-slate-400 dark:text-slate-500">
                        {t('history.viewedResults', { count: entry.result_count })}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {typeLabel(prefs.travel_type) && <Badge label={typeLabel(prefs.travel_type)!} color="blue" />}
                      {seasonLabel(prefs.season) && <Badge label={seasonLabel(prefs.season)!} color="amber" />}
                      {prefs.budget && <Badge label={`€${prefs.budget}`} color="emerald" />}
                      {prefs.trip_duration_preference && (
                        <Badge label={t('recommendations.tripDuration') + `: ${prefs.trip_duration_preference}`} color="purple" />
                      )}
                      {prefs.activities.length === 0 && !prefs.travel_type && !prefs.season && !prefs.budget && !prefs.trip_duration_preference && (
                        <span className="text-xs text-slate-400 dark:text-slate-500">{t('history.noPreferences')}</span>
                      )}
                    </div>

                    {entry.results_snapshot.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {entry.results_snapshot.slice(0, 6).map((r) => (
                          <Link
                            key={r.destination_id}
                            to={`/destination/${r.slug}`}
                            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-50 dark:bg-slate-900/40 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                          >
                            {localizedName(r, i18n.language)}
                            <span className="text-primary-600 dark:text-primary-400 font-semibold">{Math.round(r.score * 100)}%</span>
                          </Link>
                        ))}
                      </div>
                    )}
                  </Card>
                )
              })}
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-3 mt-8">
                <Button variant="secondary" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} leftIcon={<ChevronLeft className="w-4 h-4" />}>
                  {t('common.back')}
                </Button>
                <span className="text-sm text-slate-500 dark:text-slate-400">{page} / {totalPages}</span>
                <Button variant="secondary" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages} rightIcon={<ChevronRight className="w-4 h-4" />}>
                  {t('common.viewAll')}
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
