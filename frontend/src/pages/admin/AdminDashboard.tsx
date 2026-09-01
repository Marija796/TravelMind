import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Users, UserX, MapPin, Star, ShieldCheck, TrendingUp, Sparkles, Sun, Compass, Search } from 'lucide-react'
import { getAdminStats } from '@/services/adminStats'
import type { AdminStats } from '@/types/admin'
import Card from '@/components/ui/Card'
import Skeleton from '@/components/ui/Skeleton'

export default function AdminDashboard() {
  const { t } = useTranslation()
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getAdminStats().then(setStats).catch(() => {}).finally(() => setIsLoading(false))
  }, [])

  const tiles = stats ? [
    { label: t('admin.stats.userCount'), value: stats.user_count, sub: t('admin.stats.activeCount', { count: stats.active_user_count }), icon: <Users className="w-5 h-5" />, color: 'text-blue-500' },
    { label: t('admin.stats.inactiveCount'), value: stats.inactive_user_count, sub: null, icon: <UserX className="w-5 h-5" />, color: 'text-slate-500' },
    { label: t('admin.stats.destinationCount'), value: stats.destination_count, sub: null, icon: <MapPin className="w-5 h-5" />, color: 'text-emerald-500' },
    { label: t('admin.stats.avgRating'), value: stats.average_destination_rating ?? '—', sub: t('admin.stats.totalReviews', { count: stats.total_destination_reviews }), icon: <Star className="w-5 h-5" />, color: 'text-amber-500' },
    { label: t('admin.stats.adminCount'), value: stats.admin_count, sub: null, icon: <ShieldCheck className="w-5 h-5" />, color: 'text-purple-500' },
    { label: t('admin.stats.similarUsersEligible'), value: stats.users_with_preferences_count, sub: null, icon: <Sparkles className="w-5 h-5" />, color: 'text-rose-500' },
  ] : []

  return (
    <div className="pt-8 pb-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{t('admin.dashboard.title')}</h1>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('admin.dashboard.subtitle')}</p>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
            {[1, 2, 3, 4, 5, 6].map((i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
          </div>
        ) : !stats ? (
          <p className="text-slate-500 dark:text-slate-400">{t('admin.dashboard.loadFailed')}</p>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
              {tiles.map((tile) => (
                <Card key={tile.label} padding="md">
                  <div className={`mb-2 ${tile.color}`}>{tile.icon}</div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{tile.value}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{tile.label}</p>
                  {tile.sub && <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{tile.sub}</p>}
                </Card>
              ))}
            </div>

            <Card padding="md">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-primary-500" />
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t('admin.dashboard.mostPopular')}</h2>
              </div>
              {stats.most_popular_destinations.length === 0 ? (
                <p className="text-sm text-slate-500 dark:text-slate-400">{t('admin.dashboard.noData')}</p>
              ) : (
                <ol className="space-y-2">
                  {stats.most_popular_destinations.map((dest, i) => (
                    <li key={dest.id} className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-700 last:border-0">
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 rounded-full bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 text-xs font-bold flex items-center justify-center">{i + 1}</span>
                        <Link to={`/destination/${dest.slug}`} className="text-sm font-medium text-slate-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400">
                          {dest.name}
                        </Link>
                      </div>
                      <span className="text-xs text-slate-500 dark:text-slate-400">{t('admin.dashboard.reviewCount', { count: dest.review_count_annotated })}</span>
                    </li>
                  ))}
                </ol>
              )}
            </Card>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
              <Card padding="md">
                <div className="flex items-center gap-2 mb-4">
                  <Search className="w-5 h-5 text-blue-500" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t('admin.dashboard.mostSearched')}</h2>
                </div>
                {stats.most_searched_destinations.length === 0 ? (
                  <p className="text-sm text-slate-500 dark:text-slate-400">{t('admin.dashboard.noData')}</p>
                ) : (
                  <ul className="space-y-2">
                    {stats.most_searched_destinations.map((row) => (
                      <li key={row.query} className="flex items-center justify-between py-1.5 text-sm">
                        <span className="text-slate-700 dark:text-slate-300">{row.query}</span>
                        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">{row.count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>

              <Card padding="md">
                <div className="flex items-center gap-2 mb-4">
                  <Compass className="w-5 h-5 text-primary-500" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t('admin.dashboard.commonTravelTypes')}</h2>
                </div>
                {stats.most_common_travel_types.length === 0 ? (
                  <p className="text-sm text-slate-500 dark:text-slate-400">{t('admin.dashboard.noData')}</p>
                ) : (
                  <ul className="space-y-2">
                    {stats.most_common_travel_types.map((row) => (
                      <li key={row.slug} className="flex items-center justify-between py-1.5 text-sm">
                        <span className="text-slate-700 dark:text-slate-300">{row.name}</span>
                        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">{row.count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>

              <Card padding="md">
                <div className="flex items-center gap-2 mb-4">
                  <Sun className="w-5 h-5 text-amber-500" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t('admin.dashboard.popularSeasons')}</h2>
                </div>
                {stats.most_popular_seasons.length === 0 ? (
                  <p className="text-sm text-slate-500 dark:text-slate-400">{t('admin.dashboard.noData')}</p>
                ) : (
                  <ul className="space-y-2">
                    {stats.most_popular_seasons.map((row) => (
                      <li key={row.slug} className="flex items-center justify-between py-1.5 text-sm">
                        <span className="text-slate-700 dark:text-slate-300">{row.name}</span>
                        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">{row.count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
