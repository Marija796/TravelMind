import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Save, Trash2, User, Camera } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { Destination, TravelType, Season } from '@/types/destination'
import type { Gender } from '@/types/user'
import { updateProfile, updateProfileImage } from '@/services/users'
import { getFavorites, removeFavorite } from '@/services/favorites'
import { getWishlist, removeFromWishlist } from '@/services/wishlist'
import { getVisited, removeFromVisited } from '@/services/visited'
import { useAuth } from '@/hooks/useAuth'
import { ACTIVITY_OPTIONS, TRAVEL_TYPE_LABELS } from '@/types/destination'
import DestinationCard from '@/components/destination/DestinationCard'
import DestinationSkeleton from '@/components/destination/DestinationSkeleton'
import PreferenceSelector from '@/components/common/PreferenceSelector'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import toast from 'react-hot-toast'

const TravelTypeOptions: Array<{ value: TravelType; label: string }> = [
  { value: 'beach', label: 'Beach' },
  { value: 'mountain', label: 'Mountain' },
  { value: 'city', label: 'City' },
  { value: 'adventure', label: 'Adventure' },
  { value: 'cultural', label: 'Cultural' },
  { value: 'luxury', label: 'Luxury' },
  { value: 'relaxation', label: 'Relaxation' },
]

const SeasonOptions: Array<{ value: Season; label: string }> = [
  { value: 'spring', label: 'Spring' },
  { value: 'summer', label: 'Summer' },
  { value: 'autumn', label: 'Autumn' },
  { value: 'winter', label: 'Winter' },
]

const GenderOptions: Array<{ value: Gender; label: string }> = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
]

const extractErrorMessage = (err: unknown, fallback: string) => {
  const axiosErr = err as { response?: { data?: Record<string, string[] | string> } }
  const data = axiosErr?.response?.data
  if (!data) return fallback
  return Object.values(data).flat().join(' ') || fallback
}

type TabKey = 'saved' | 'wishlist' | 'visited'

export default function Profile() {
  const { t } = useTranslation()
  const { user, refreshUser } = useAuth()
  const [activeTab, setActiveTab] = useState<TabKey>('saved')
  const [favorites, setFavorites] = useState<Destination[]>([])
  const [wishlist, setWishlist] = useState<Destination[]>([])
  const [visited, setVisited] = useState<Destination[]>([])
  const [loadingFavs, setLoadingFavs] = useState(true)
  const [loadingWish, setLoadingWish] = useState(true)
  const [loadingVisited, setLoadingVisited] = useState(true)
  const [saving, setSaving] = useState(false)

  const [travelType, setTravelType] = useState<TravelType | ''>(user?.preferred_travel_type || '')
  const [season, setSeason] = useState<Season | ''>(user?.preferred_season || '')
  const [activities, setActivities] = useState<string[]>(user?.preferred_activities || [])
  const [gender, setGender] = useState<Gender | ''>(user?.gender || '')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(user?.profile_image || null)

  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    defaultValues: {
      username: user?.username || '',
      short_summary: user?.short_summary || '',
      budget: user?.budget || '',
      trip_duration_preference: user?.trip_duration_preference || '',
    },
  })

  useEffect(() => {
    getFavorites().then(setFavorites).catch(() => {}).finally(() => setLoadingFavs(false))
    getWishlist().then(setWishlist).catch(() => {}).finally(() => setLoadingWish(false))
    getVisited().then(setVisited).catch(() => {}).finally(() => setLoadingVisited(false))
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImageFile(file)
    setImagePreview(URL.createObjectURL(file))
  }

  const onSubmit = async (data: Record<string, unknown>) => {
    setSaving(true)
    let imageFailed = false
    let fieldsFailed = false

    if (imageFile) {
      try {
        await updateProfileImage(imageFile)
      } catch (err) {
        imageFailed = true
        toast.error(extractErrorMessage(err, 'Failed to upload profile picture'))
      }
    }

    try {
      await updateProfile({
        username: data.username as string,
        short_summary: data.short_summary as string,
        gender,
        budget: data.budget ? String(data.budget) : null,
        trip_duration_preference: data.trip_duration_preference ? Number(data.trip_duration_preference) : null,
        preferred_travel_type: travelType,
        preferred_season: season,
        preferred_activities: activities,
      })
    } catch (err) {
      fieldsFailed = true
      toast.error(extractErrorMessage(err, 'Failed to save changes'))
    }

    await refreshUser()
    setImageFile(null)
    if (!imageFailed && !fieldsFailed) {
      toast.success(t('profile.saveChanges') + ' ✓')
    }
    setSaving(false)
  }

  const removeFav = async (id: number) => {
    try {
      await removeFavorite(id)
      setFavorites((prev) => prev.filter((d) => d.id !== id))
      toast.success('Removed from favorites')
    } catch { toast.error('Failed to remove') }
  }

  const removeWish = async (id: number) => {
    try {
      await removeFromWishlist(id)
      setWishlist((prev) => prev.filter((d) => d.id !== id))
      toast.success('Removed from wishlist')
    } catch { toast.error('Failed to remove') }
  }

  const removeVisit = async (id: number) => {
    try {
      await removeFromVisited(id)
      setVisited((prev) => prev.filter((d) => d.id !== id))
      toast.success('Removed from visited')
    } catch { toast.error('Failed to remove') }
  }

  const initials = user?.username?.slice(0, 2).toUpperCase() || 'TM'

  const tabs: { key: TabKey; label: string; count: number }[] = [
    { key: 'saved', label: t('profile.savedDestinations'), count: favorites.length },
    { key: 'wishlist', label: t('profile.wishlist'), count: wishlist.length },
    { key: 'visited', label: t('profile.visited'), count: visited.length },
  ]

  const isLoading = activeTab === 'saved' ? loadingFavs : activeTab === 'wishlist' ? loadingWish : loadingVisited
  const items = activeTab === 'saved' ? favorites : activeTab === 'wishlist' ? wishlist : visited
  const removeItem = activeTab === 'saved' ? removeFav : activeTab === 'wishlist' ? removeWish : removeVisit

  const emptyConfig = {
    saved: { emoji: '🤍', title: t('profile.noSaved'), hint: t('profile.noSavedHint') },
    wishlist: { emoji: '🔖', title: t('profile.noWishlist'), hint: t('profile.noWishlistHint') },
    visited: { emoji: '✈️', title: t('profile.noVisited'), hint: t('profile.noVisitedHint') },
  }[activeTab]

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Profile header */}
        <div className="flex items-center gap-5 mb-10">
          {imagePreview ? (
            <img src={imagePreview} alt={user?.username} className="w-20 h-20 rounded-2xl object-cover" />
          ) : (
            <div className="w-20 h-20 bg-gradient-to-br from-primary-400 to-accent-400 rounded-2xl flex items-center justify-center text-white text-2xl font-bold">
              {initials}
            </div>
          )}
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{user?.username}</h1>
            <p className="text-slate-500 dark:text-slate-400">{user?.email}</p>
            {user?.preferred_travel_type && (
              <p className="text-sm text-primary-600 font-medium mt-1">
                {TRAVEL_TYPE_LABELS[user.preferred_travel_type]} {t('profile.traveller')}
              </p>
            )}
          </div>
        </div>

        {/* Edit form */}
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6 mb-8 space-y-6">
          <div className="flex items-center gap-2 mb-2">
            <User className="w-5 h-5 text-primary-500" />
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t('profile.editProfile')}</h2>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('profile.profileImage')}</label>
            <label className="inline-flex items-center gap-2 cursor-pointer text-sm font-medium text-primary-600 hover:text-primary-700">
              <Camera className="w-4 h-4" />
              {t('profile.changePhoto')}
              <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
            </label>
          </div>

          <Input
            label={t('profile.username')}
            {...register('username', { required: true })}
            error={errors.username ? 'Username is required' : undefined}
          />

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('profile.shortSummary')}</label>
            <textarea
              {...register('short_summary', { maxLength: 280 })}
              rows={3}
              maxLength={280}
              placeholder={t('profile.shortSummaryPlaceholder')}
              className="input-base resize-none"
            />
            <p className="mt-1 text-xs text-slate-400 text-right">{(watch('short_summary') || '').length}/280</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label={t('profile.maxBudget')} type="number" placeholder="e.g. 5000" {...register('budget')} />
            <Input label={t('profile.tripDuration')} type="number" placeholder="e.g. 14" {...register('trip_duration_preference')} />
          </div>

          <PreferenceSelector
            label={t('profile.gender')}
            options={GenderOptions}
            selected={gender ? [gender] : []}
            onChange={(v) => setGender((v[0] as Gender) || '')}
            singleSelect
          />

          <PreferenceSelector
            label={t('profile.preferredTravelType')}
            options={TravelTypeOptions}
            selected={travelType ? [travelType] : []}
            onChange={(v) => setTravelType(v[0] as TravelType || '')}
            singleSelect
          />

          <PreferenceSelector
            label={t('profile.preferredSeason')}
            options={SeasonOptions}
            selected={season ? [season] : []}
            onChange={(v) => setSeason(v[0] as Season || '')}
            singleSelect
          />

          <PreferenceSelector
            label={t('profile.preferredActivities')}
            options={ACTIVITY_OPTIONS.map((a) => ({ value: a, label: a }))}
            selected={activities}
            onChange={setActivities}
          />

          <Button type="submit" isLoading={saving} leftIcon={<Save className="w-4 h-4" />}>
            {t('profile.saveChanges')}
          </Button>
        </form>

        {/* Collections with tabs */}
        <div>
          <div className="flex gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl mb-6 w-fit">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.key
                    ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
                }`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className="ml-1.5 text-xs text-slate-400 dark:text-slate-500">({tab.count})</span>
                )}
              </button>
            ))}
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[1, 2].map((i) => <DestinationSkeleton key={i} />)}
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-2xl">
              <p className="text-4xl mb-3">{emptyConfig.emoji}</p>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-1">{emptyConfig.title}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">{emptyConfig.hint}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {items.map((dest) => (
                <div key={dest.id} className="relative group">
                  <DestinationCard
                    destination={dest}
                    isFavorite={activeTab === 'saved'}
                    isWishlisted={activeTab === 'wishlist'}
                    isVisited={activeTab === 'visited'}
                  />
                  <button
                    onClick={() => removeItem(dest.id)}
                    className="absolute top-3 left-3 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-sm z-20"
                    title="Remove"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
