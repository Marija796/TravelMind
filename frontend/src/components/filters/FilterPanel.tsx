import { useTranslation } from 'react-i18next'
import type { FilterParams, TravelType, Season, DifficultyLevel, Region } from '@/types/destination'
import { REGION_LABELS } from '@/types/destination'
import Button from '@/components/ui/Button'

interface Props {
  filters: FilterParams
  onChange: (updated: FilterParams) => void
  onClear: () => void
}

const TravelTypes: TravelType[] = ['beach', 'mountain', 'city', 'adventure', 'cultural', 'luxury', 'relaxation']
const Seasons: Season[] = ['spring', 'summer', 'autumn', 'winter']
const Difficulties: DifficultyLevel[] = ['easy', 'moderate', 'challenging']
const Regions: Region[] = ['europe', 'asia', 'north_america', 'south_america', 'africa', 'oceania']

export default function FilterPanel({ filters, onChange, onClear }: Props) {
  const { t } = useTranslation()
  const set = (key: keyof FilterParams, value: unknown) => onChange({ ...filters, [key]: value, page: 1 })
  const hasActive = Object.entries(filters).some(([k, v]) => k !== 'page' && k !== 'ordering' && v !== '' && v !== undefined)

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-900 dark:text-white">{t('filter.filters')}</h3>
        {hasActive && (
          <button onClick={onClear} className="text-xs text-primary-600 hover:underline">{t('filter.clearAll')}</button>
        )}
      </div>

      {/* Region */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">{t('filter.region')}</p>
        <div className="flex flex-wrap gap-1.5">
          {Regions.map((r) => (
            <button
              key={r}
              onClick={() => set('region', filters.region === r ? '' : r)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filters.region === r
                  ? 'bg-violet-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              {REGION_LABELS[r]}
            </button>
          ))}
        </div>
      </div>

      {/* Travel Type */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">{t('filter.travelType')}</p>
        <div className="flex flex-wrap gap-1.5">
          {TravelTypes.map((type) => (
            <button
              key={type}
              onClick={() => set('travel_type', filters.travel_type === type ? '' : type)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filters.travel_type === type
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              {t(`travelType.${type}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Season */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">{t('filter.season')}</p>
        <div className="flex flex-wrap gap-1.5">
          {Seasons.map((s) => (
            <button
              key={s}
              onClick={() => set('season', filters.season === s ? '' : s)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filters.season === s
                  ? 'bg-accent-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              {t(`season.${s}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Difficulty */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">{t('filter.difficulty')}</p>
        <div className="flex gap-1.5">
          {Difficulties.map((d) => (
            <button
              key={d}
              onClick={() => set('difficulty_level', filters.difficulty_level === d ? '' : d)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filters.difficulty_level === d
                  ? 'bg-amber-500 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              {t(`filter.${d}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Country */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">{t('filter.country')}</p>
        <input
          type="text"
          placeholder={t('filter.countryPlaceholder')}
          value={filters.country || ''}
          onChange={(e) => set('country', e.target.value || '')}
          className="input-base text-sm"
        />
      </div>

      {/* Budget Max */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">{t('filter.maxBudgetLabel')}</p>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">€</span>
          <input
            type="number"
            placeholder={t('filter.anyBudget')}
            value={filters.budget_max || ''}
            onChange={(e) => set('budget_max', e.target.value ? Number(e.target.value) : '')}
            className="input-base pl-7 text-sm"
          />
        </div>
      </div>

      {/* Duration */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">{t('filter.maxDurationLabel')}</p>
        <input
          type="number"
          placeholder={t('filter.anyDuration')}
          value={filters.duration_max || ''}
          onChange={(e) => set('duration_max', e.target.value ? Number(e.target.value) : '')}
          className="input-base text-sm"
        />
      </div>

      {/* Sort */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">{t('filter.sortBy')}</p>
        <select
          value={filters.ordering || '-popularity_score'}
          onChange={(e) => set('ordering', e.target.value)}
          className="input-base text-sm"
        >
          <option value="-popularity_score">{t('filter.mostPopular')}</option>
          <option value="estimated_cost">{t('filter.priceAsc')}</option>
          <option value="-estimated_cost">{t('filter.priceDesc')}</option>
          <option value="name">{t('filter.nameAZ')}</option>
          <option value="-created_at">{t('filter.newestFirst')}</option>
        </select>
      </div>

      {hasActive && (
        <Button variant="secondary" fullWidth onClick={onClear} size="sm">
          {t('filter.clearAllFilters')}
        </Button>
      )}
    </div>
  )
}
