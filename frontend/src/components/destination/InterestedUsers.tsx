import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Users } from 'lucide-react'
import { getDestinationInterestedUsers } from '@/services/destinationInterestedUsers'
import type { DestinationInterestedUser } from '@/types/user'
import SimilarUserGrid from '@/components/users/SimilarUserGrid'

interface Props {
  destinationId: number
  destinationName: string
}

export default function InterestedUsers({ destinationId, destinationName }: Props) {
  const { t } = useTranslation()
  const [users, setUsers] = useState<DestinationInterestedUser[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    getDestinationInterestedUsers(destinationId)
      .then((res) => { if (!cancelled) setUsers(res.results) })
      .catch(() => { if (!cancelled) setUsers([]) })
      .finally(() => { if (!cancelled) setIsLoading(false) })
    return () => { cancelled = true }
  }, [destinationId])

  return (
    <div className="mb-12">
      <div className="flex items-center gap-2 mb-1">
        <Users className="w-5 h-5 text-primary-500" />
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">{t('destination.interestedUsersTitle')}</h2>
      </div>
      <p className="text-slate-500 dark:text-slate-400 mb-6">{t('destination.interestedUsersSubtitle')}</p>

      <SimilarUserGrid
        users={users}
        isLoading={isLoading}
        skeletonCount={3}
        emptyTitle={t('destination.interestedUsersEmpty')}
        renderSubtitle={(u) => {
          const user = u as DestinationInterestedUser
          return user.interest === 'direct'
            ? t('destination.interestedInThis', { name: destinationName })
            : t('destination.interestedInSimilar')
        }}
      />
    </div>
  )
}
