import { useTranslation } from 'react-i18next'
import type { FilterParams } from '@/types/destination'
import Badge from '@/components/ui/Badge'

interface Props {
  filters: FilterParams
  onChange: (updated: FilterParams) => void
}

export default function ActiveFilterTags({ filters, onChange }: Props) {
  const { t } = useTranslation()
  const remove = (key: keyof FilterParams) => onChange({ ...filters, [key]: '', page: 1 })
  const tags: { key: keyof FilterParams; label: string }[] = []

  if (filters.region)           tags.push({ key: 'region',           label: t(`region.${filters.region}`) })
  if (filters.travel_type)      tags.push({ key: 'travel_type',      label: t(`travelType.${filters.travel_type}`) })
  if (filters.season)           tags.push({ key: 'season',           label: t(`season.${filters.season}`) })
  if (filters.difficulty_level) tags.push({ key: 'difficulty_level', label: t(`filter.${filters.difficulty_level}`) })
  if (filters.country)          tags.push({ key: 'country',          label: `${t('filter.country')}: ${filters.country}` })
  if (filters.budget_max)       tags.push({ key: 'budget_max',       label: t('filter.activeBudget', { value: filters.budget_max }) })
  if (filters.duration_max)     tags.push({ key: 'duration_max',     label: t('filter.activeDuration', { value: filters.duration_max }) })

  if (tags.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <Badge
          key={tag.key}
          label={tag.label}
          color="blue"
          removable
          onRemove={() => remove(tag.key)}
        />
      ))}
    </div>
  )
}
