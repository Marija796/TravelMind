import { useState } from 'react'
import { addFavorite, removeFavorite } from '@/services/favorites'
import { useAuth } from './useAuth'
import toast from 'react-hot-toast'

export function useFavorites(initialIds: number[] = []) {
  const { isAuthenticated } = useAuth()
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set(initialIds))

  const toggle = async (id: number) => {
    if (!isAuthenticated) {
      toast.error('Please log in to save favorites')
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
        toast.success('Removed from favorites')
      } else {
        await addFavorite(id)
        toast.success('Saved to favorites')
      }
    } catch {
      setFavoriteIds((prev) => {
        const next = new Set(prev)
        isFav ? next.add(id) : next.delete(id)
        return next
      })
      toast.error('Failed to update favorites')
    }
  }

  return { favoriteIds, toggle, isFavorite: (id: number) => favoriteIds.has(id) }
}
