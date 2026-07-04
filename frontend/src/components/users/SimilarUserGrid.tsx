import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'
import type { SimilarUser } from '@/types/user'
import SimilarUserCard from './SimilarUserCard'
import SimilarUserSkeleton from './SimilarUserSkeleton'

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

interface Props {
  users: SimilarUser[]
  isLoading?: boolean
  skeletonCount?: number
}

export default function SimilarUserGrid({ users, isLoading, skeletonCount = 6 }: Props) {
  const { t } = useTranslation()

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <SimilarUserSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (users.length === 0) {
    return (
      <div className="py-20 text-center">
        <p className="text-4xl mb-4">🧭</p>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">{t('similarUsers.noOthers')}</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">{t('similarUsers.noOthersHint')}</p>
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      {users.map((u) => (
        <motion.div key={u.id} variants={itemVariants}>
          <SimilarUserCard user={u} />
        </motion.div>
      ))}
    </motion.div>
  )
}
