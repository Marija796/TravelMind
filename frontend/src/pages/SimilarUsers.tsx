import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Users } from 'lucide-react'
import { getSimilarUsers } from '@/services/similarUsers'
import type { SimilarUser } from '@/types/user'
import SimilarUserGrid from '@/components/users/SimilarUserGrid'

export default function SimilarUsers() {
  const { t } = useTranslation()
  const [users, setUsers] = useState<SimilarUser[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getSimilarUsers()
      .then((res) => setUsers(res.results))
      .catch(() => {})
      .finally(() => setIsLoading(false))
  }, [])

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mb-2">
          <Users className="w-6 h-6 text-primary-500" />
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('similarUsers.title')}</h1>
        </div>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('similarUsers.subtitle')}</p>

        <SimilarUserGrid users={users} isLoading={isLoading} />
      </div>
    </div>
  )
}
