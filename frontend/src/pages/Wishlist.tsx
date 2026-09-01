import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trash2 } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { Destination } from '@/types/destination'
import { getWishlist, removeFromWishlist } from '@/services/wishlist'
import DestinationCard from '@/components/destination/DestinationCard'
import DestinationSkeleton from '@/components/destination/DestinationSkeleton'
import Button from '@/components/ui/Button'
import toast from 'react-hot-toast'

export default function Wishlist() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [items, setItems] = useState<Destination[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getWishlist()
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const remove = async (id: number) => {
    try {
      await removeFromWishlist(id)
      setItems((prev) => prev.filter((d) => d.id !== id))
      toast.success(t('destination.removedFromWishlistToast'))
    } catch {
      toast.error(t('profile.removeFailed'))
    }
  }

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">{t('wishlist.title')}</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">{t('wishlist.subtitle')}</p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => <DestinationSkeleton key={i} />)}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-2xl">
            <p className="text-5xl mb-4">🔖</p>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">{t('wishlist.empty')}</h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6">{t('wishlist.emptyHint')}</p>
            <Button onClick={() => navigate('/explore')}>{t('wishlist.explore')}</Button>
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
              {t('wishlist.countOnWishlist', { count: items.length })}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {items.map((dest) => (
                <div key={dest.id} className="relative group">
                  <DestinationCard destination={dest} isWishlisted />
                  <button
                    onClick={() => remove(dest.id)}
                    className="absolute top-3 left-3 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-sm z-20"
                    title={t('destination.removeFromWishlist')}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
