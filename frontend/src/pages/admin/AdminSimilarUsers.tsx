import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, RefreshCw, Users } from 'lucide-react'
import toast from 'react-hot-toast'
import { getAdminUsers, getAdminUserSimilar } from '@/services/adminUsers'
import type { AdminUser, AdminSimilarUsersResponse } from '@/types/admin'
import { useDebounce } from '@/hooks/useDebounce'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import Skeleton from '@/components/ui/Skeleton'
import SimilarUserGrid from '@/components/users/SimilarUserGrid'

export default function AdminSimilarUsers() {
  const { t } = useTranslation()
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 400)
  const [candidates, setCandidates] = useState<AdminUser[]>([])
  const [selected, setSelected] = useState<AdminUser | null>(null)
  const [data, setData] = useState<AdminSimilarUsersResponse | null>(null)
  const [isLoadingResults, setIsLoadingResults] = useState(false)

  useEffect(() => {
    if (!debouncedSearch) { setCandidates([]); return }
    getAdminUsers({ search: debouncedSearch })
      .then((res) => setCandidates(res.results))
      .catch(() => {})
  }, [debouncedSearch])

  const loadSimilarity = (user: AdminUser) => {
    setSelected(user)
    setIsLoadingResults(true)
    setData(null)
    getAdminUserSimilar(user.id)
      .then(setData)
      .catch(() => toast.error(t('admin.similarUsers.loadFailed')))
      .finally(() => setIsLoadingResults(false))
  }

  return (
    <div className="pt-8 pb-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{t('admin.similarUsers.title')}</h1>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('admin.similarUsers.subtitle')}</p>

        <Card padding="md" className="mb-6">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            {t('admin.similarUsers.pickUser')}
          </label>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t('admin.users.searchPlaceholder')}
              className="input-base text-sm pl-9"
            />
          </div>
          {candidates.length > 0 && !selected && (
            <ul className="mt-2 border border-slate-100 dark:border-slate-700 rounded-xl overflow-hidden divide-y divide-slate-100 dark:divide-slate-700">
              {candidates.map((c) => (
                <li key={c.id}>
                  <button
                    type="button"
                    onClick={() => { loadSimilarity(c); setSearch(''); setCandidates([]) }}
                    className="w-full text-left px-4 py-2.5 text-sm hover:bg-slate-50 dark:hover:bg-slate-700/40 flex items-center justify-between"
                  >
                    <span className="font-medium text-slate-900 dark:text-white">{c.username}</span>
                    <span className="text-slate-400 text-xs">{c.email}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {selected && (
          <>
            <Card padding="md" className="mb-6">
              <div className="flex items-center justify-between flex-wrap gap-3 mb-3">
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-primary-500" />
                  <h2 className="font-semibold text-slate-900 dark:text-white">{selected.username}</h2>
                </div>
                <Button size="sm" variant="secondary" leftIcon={<RefreshCw className="w-3.5 h-3.5" />} onClick={() => loadSimilarity(selected)} isLoading={isLoadingResults}>
                  {t('admin.similarUsers.recalculate')}
                </Button>
              </div>
              {data?.target && (
                <div className="flex flex-wrap gap-2">
                  {data.target.preferred_travel_type && <Badge label={data.target.preferred_travel_type} color="purple" />}
                  {data.target.preferred_season && <Badge label={data.target.preferred_season} color="blue" />}
                  {data.target.budget && <Badge label={`€${data.target.budget}`} color="emerald" />}
                  {data.target.trip_duration_preference && <Badge label={`${data.target.trip_duration_preference} ${t('destination.days')}`} color="slate" />}
                  {data.target.preferred_activities.map((a) => <Badge key={a} label={a} color="amber" />)}
                  {!data.target.preferred_travel_type && !data.target.preferred_season && !data.target.budget && data.target.preferred_activities.length === 0 && (
                    <span className="text-xs text-slate-400">{t('admin.similarUsers.noPreferences')}</span>
                  )}
                </div>
              )}
            </Card>

            {isLoadingResults ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => <Skeleton key={i} className="h-40 rounded-2xl" />)}
              </div>
            ) : data?.reason === 'no_preferences_set' ? (
              <Card padding="lg" className="text-center">
                <p className="text-slate-500 dark:text-slate-400">{t('admin.similarUsers.noPreferencesSet')}</p>
              </Card>
            ) : data ? (
              <SimilarUserGrid users={data.results} />
            ) : null}
          </>
        )}
      </div>
    </div>
  )
}
