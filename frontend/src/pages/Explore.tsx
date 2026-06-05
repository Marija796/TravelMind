import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { Destination, FilterParams } from '@/types/destination'
import type { PaginatedResponse } from '@/types/destination'
import { getDestinations } from '@/services/destinations'
import { useAuth } from '@/hooks/useAuth'
import { useFavorites } from '@/hooks/useFavorites'
import { useDebounce } from '@/hooks/useDebounce'
import DestinationGrid from '@/components/destination/DestinationGrid'
import SearchBar from '@/components/filters/SearchBar'
import FilterPanel from '@/components/filters/FilterPanel'
import ActiveFilterTags from '@/components/filters/ActiveFilterTags'

export default function Explore() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const { favoriteIds, toggle } = useFavorites(user?.favorite_destination_ids)
  const [searchParams, setSearchParams] = useSearchParams()

  const [data, setData] = useState<PaginatedResponse<Destination> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [filterOpen, setFilterOpen] = useState(false)

  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [filters, setFilters] = useState<FilterParams>({
    travel_type: (searchParams.get('travel_type') as FilterParams['travel_type']) || '',
    season: (searchParams.get('season') as FilterParams['season']) || '',
    difficulty_level: (searchParams.get('difficulty_level') as FilterParams['difficulty_level']) || '',
    country: searchParams.get('country') || '',
    region: (searchParams.get('region') as FilterParams['region']) || '',
    budget_max: searchParams.get('budget_max') ? Number(searchParams.get('budget_max')) : '',
    duration_max: searchParams.get('duration_max') ? Number(searchParams.get('duration_max')) : '',
    ordering: searchParams.get('ordering') || '-popularity_score',
    page: Number(searchParams.get('page')) || 1,
  })

  const debouncedSearch = useDebounce(search, 400)

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const params: FilterParams & { search?: string } = { ...filters }
      if (debouncedSearch) params.search = debouncedSearch
      const result = await getDestinations(params)
      setData(result)
    } catch {
      setData(null)
    } finally {
      setIsLoading(false)
    }
  }, [filters, debouncedSearch])

  useEffect(() => { fetchData() }, [fetchData])

  useEffect(() => {
    const params: Record<string, string> = {}
    if (search) params.search = search
    if (filters.travel_type) params.travel_type = filters.travel_type
    if (filters.season) params.season = filters.season
    if (filters.difficulty_level) params.difficulty_level = filters.difficulty_level
    if (filters.country) params.country = filters.country
    if (filters.region) params.region = filters.region
    if (filters.budget_max) params.budget_max = String(filters.budget_max)
    if (filters.duration_max) params.duration_max = String(filters.duration_max)
    if (filters.ordering && filters.ordering !== '-popularity_score') params.ordering = filters.ordering
    if (filters.page && filters.page > 1) params.page = String(filters.page)
    setSearchParams(params)
  }, [filters, search, setSearchParams])

  const clearFilters = () => setFilters({ page: 1, ordering: '-popularity_score' })
  const setPage = (page: number) => setFilters((f) => ({ ...f, page }))

  const totalPages = data ? Math.ceil(data.count / 12) : 0

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-1">{t('explore.title')}</h1>
          <p className="text-slate-500 dark:text-slate-400">
            {data ? t(data.count === 1 ? 'explore.foundSingle' : 'explore.foundPlural', { count: data.count }) : t('explore.subtitle')}
          </p>
        </div>

        {/* Search */}
        <div className="mb-4">
          <SearchBar
            value={search}
            onChange={(v) => { setSearch(v); setFilters((f) => ({ ...f, page: 1 })) }}
            showFilterButton
            onFilterToggle={() => setFilterOpen(!filterOpen)}
            isFilterOpen={filterOpen}
          />
        </div>

        {/* Active filter tags */}
        <ActiveFilterTags filters={filters} onChange={setFilters} />

        <div className="flex gap-6 mt-6">
          {/* Filter sidebar - desktop */}
          <div className="hidden lg:block w-64 shrink-0">
            <div className="sticky top-24">
              <FilterPanel filters={filters} onChange={setFilters} onClear={clearFilters} />
            </div>
          </div>

          {/* Mobile filter panel */}
          <AnimatePresence>
            {filterOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="lg:hidden w-full mb-4 overflow-hidden"
              >
                <FilterPanel filters={filters} onChange={setFilters} onClear={clearFilters} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Grid */}
          <div className="flex-1 min-w-0">
            <DestinationGrid
              destinations={data?.results || []}
              isLoading={isLoading}
              favoriteIds={favoriteIds}
              onFavoriteToggle={toggle}
            />

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-10">
                <button
                  onClick={() => setPage(Math.max(1, (filters.page || 1) - 1))}
                  disabled={(filters.page || 1) <= 1}
                  className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((p) => Math.abs(p - (filters.page || 1)) <= 2)
                  .map((p) => (
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={`w-9 h-9 rounded-xl text-sm font-medium transition-all ${
                        p === (filters.page || 1)
                          ? 'bg-primary-600 text-white'
                          : 'border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                <button
                  onClick={() => setPage(Math.min(totalPages, (filters.page || 1) + 1))}
                  disabled={(filters.page || 1) >= totalPages}
                  className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
