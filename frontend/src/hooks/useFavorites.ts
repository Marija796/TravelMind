import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { addFavorite, removeFavorite } from '@/services/favorites'
import { useAuth } from './useAuth'
import toast from 'react-hot-toast'

export function useFavorites(initialIds: number[] = []) {
  const { t } = useTranslation()
  const { isAuthenticated } = useAuth()
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set(initialIds))

  const toggle = async (id: number) => {
    if (!isAuthenticated) {
      toast.error(t('destination.loginToFavorite'))
      return
    }
    const isFav = favoriteIds.has(id)
    setFavoriteIds((prev) => {
      const next = new Set(prev)
      isFav ? next.delete(id) : next.add(id)
      return next
    })
    try {
      if (isFav) {
        await removeFavorite(id)
        toast.success(t('destination.removedFromFavoritesToast'))
      } else {
        await addFavorite(id)
        toast.success(t('destination.savedToFavoritesToast'))
      }
    } catch {
      setFavoriteIds((prev) => {
        const next = new Set(prev)
        isFav ? next.add(id) : next.delete(id)
        return next
      })
      toast.error(t('destination.favoritesUpdateFailed'))
    }
  }

  return { favoriteIds, toggle, isFavorite: (id: number) => favoriteIds.has(id) }
}
