import type { FilterParams } from '@/types/destination'
import { TRAVEL_TYPE_LABELS, SEASON_LABELS, DIFFICULTY_LABELS, REGION_LABELS } from '@/types/destination'
import type { Region } from '@/types/destination'
import Badge from '@/components/ui/Badge'

interface Props {
  filters: FilterParams
  onChange: (updated: FilterParams) => void
}

export default function ActiveFilterTags({ filters, onChange }: Props) {
  const remove = (key: keyof FilterParams) => onChange({ ...filters, [key]: '', page: 1 })
  const tags: { key: keyof FilterParams; label: string }[] = []

  if (filters.region) tags.push({ key: 'region', label: REGION_LABELS[filters.region as Region] })
  if (filters.travel_type) tags.push({ key: 'travel_type', label: TRAVEL_TYPE_LABELS[filters.travel_type] })
  if (filters.season) tags.push({ key: 'season', label: SEASON_LABELS[filters.season] })
  if (filters.difficulty_level) tags.push({ key: 'difficulty_level', label: DIFFICULTY_LABELS[filters.difficulty_level] })
  if (filters.country) tags.push({ key: 'country', label: `Country: ${filters.country}` })
  if (filters.budget_max) tags.push({ key: 'budget_max', label: `Under $${filters.budget_max}` })
  if (filters.duration_max) tags.push({ key: 'duration_max', label: `Max ${filters.duration_max} days` })

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
