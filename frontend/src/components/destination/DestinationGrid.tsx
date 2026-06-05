import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'
import type { Destination } from '@/types/destination'
import DestinationCard from './DestinationCard'
import DestinationSkeleton from './DestinationSkeleton'

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

interface Props {
  destinations: Destination[]
  isLoading?: boolean
  skeletonCount?: number
  favoriteIds?: Set<number>
  onFavoriteToggle?: (id: number) => void
  showScore?: boolean
  scores?: Record<number, number>
}

export default function DestinationGrid({
  destinations,
  isLoading,
  skeletonCount = 6,
  favoriteIds,
  onFavoriteToggle,
  showScore,
  scores,
}: Props) {
  const { t } = useTranslation()

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <DestinationSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (destinations.length === 0) {
    return (
      <div className="py-20 text-center">
        <p className="text-4xl mb-4">🗺️</p>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">{t('common.noResults')}</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">{t('common.adjustFilters')}</p>
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
      {destinations.map((dest) => (
        <motion.div key={dest.id} variants={itemVariants}>
          <DestinationCard
            destination={dest}
            isFavorite={favoriteIds?.has(dest.id) ?? dest.is_favorited}
            onFavoriteToggle={onFavoriteToggle}
            showScore={showScore}
            score={scores?.[dest.id]}
          />
        </motion.div>
      ))}
    </motion.div>
  )
}
