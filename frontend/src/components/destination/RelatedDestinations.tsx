import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import type { Destination } from '@/types/destination'
import { getDestinations } from '@/services/destinations'
import DestinationCard from './DestinationCard'
import Skeleton from '@/components/ui/Skeleton'

interface Props {
  travelType: string
  excludeId: number
}

export default function RelatedDestinations({ travelType, excludeId }: Props) {
  const { t } = useTranslation()
  const [destinations, setDestinations] = useState<Destination[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getDestinations({ travel_type: travelType as Destination['travel_type'], page: 1 })
      .then((data) => setDestinations(data.results.filter((d) => d.id !== excludeId).slice(0, 3)))
      .catch(() => {})
      .finally(() => setIsLoading(false))
  }, [travelType, excludeId])

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => <Skeleton key={i} className="h-48" />)}
      </div>
    )
  }

  if (destinations.length === 0) return null

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">{t('destination.youMayAlsoLike')}</h2>
        <Link to={`/explore?travel_type=${travelType}`} className="text-sm text-primary-600 hover:underline">
          {t('common.seeAll')}
        </Link>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {destinations.map((d) => (
          <DestinationCard key={d.id} destination={d} />
        ))}
      </div>
    </div>
  )
}
