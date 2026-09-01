import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import { Save } from 'lucide-react'
import toast from 'react-hot-toast'
import { getDestination } from '@/services/destinations'
import { createAdminDestination, updateAdminDestination } from '@/services/adminDestinations'
import { useTravelCategories, useSeasons } from '@/hooks/useTaxonomy'
import type { Destination } from '@/types/destination'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

interface FormData {
  name: string
  name_mk: string
  city: string
  country: string
  country_mk: string
  region: string
  description: string
  description_mk: string
  travel_type: string
  best_season: string
  estimated_cost: string
  difficulty_level: string
  trip_duration_min: number
  trip_duration_max: number
  image_url: string
  booking_url: string
  flight_url: string
  images: string
  activities: string
  attractions: string
  travel_tips: string
  popularity_score: number
}

const REGIONS = ['europe', 'asia', 'north_america', 'south_america', 'africa', 'oceania']
const DIFFICULTIES = ['easy', 'moderate', 'challenging']
const URL_PATTERN = /^https?:\/\/.+/i

const defaultValues: FormData = {
  name: '', name_mk: '', city: '', country: '', country_mk: '', region: '',
  description: '', description_mk: '', travel_type: '', best_season: '',
  estimated_cost: '', difficulty_level: 'easy', trip_duration_min: 1, trip_duration_max: 7,
  image_url: '', booking_url: '', flight_url: '',
  images: '', activities: '', attractions: '', travel_tips: '', popularity_score: 0,
}

export default function AdminDestinationForm() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEdit = !!id
  const [isLoading, setIsLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const { categories } = useTravelCategories()
  const { seasons } = useSeasons()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({ defaultValues })

  useEffect(() => {
    if (!id) return
    getDestination(Number(id))
      .then((d: Destination) => reset({
        name: d.name, name_mk: d.name_mk, city: d.city, country: d.country, country_mk: d.country_mk, region: d.region,
        description: d.description, description_mk: d.description_mk,
        travel_type: d.travel_type, best_season: d.best_season || '',
        estimated_cost: d.estimated_cost, difficulty_level: d.difficulty_level,
        trip_duration_min: d.trip_duration_min, trip_duration_max: d.trip_duration_max,
        image_url: d.image_url || '', booking_url: d.booking_url || '', flight_url: d.flight_url || '',
        images: (d.images || []).join(', '),
        activities: (d.activities || []).join(', '), attractions: d.attractions,
        travel_tips: d.travel_tips, popularity_score: d.popularity_score,
      }))
      .catch(() => toast.error(t('admin.destinations.loadFailed')))
      .finally(() => setIsLoading(false))
  }, [id, reset, t])

  const onSubmit = async (data: FormData) => {
    setSaving(true)
    const payload = {
      ...data,
      best_season: data.best_season || null,
      images: data.images ? data.images.split(',').map((s) => s.trim()).filter(Boolean) : [],
      activities: data.activities ? data.activities.split(',').map((s) => s.trim()).filter(Boolean) : [],
      trip_duration_min: Number(data.trip_duration_min),
      trip_duration_max: Number(data.trip_duration_max),
      popularity_score: Number(data.popularity_score),
    }
    try {
      if (isEdit) await updateAdminDestination(Number(id), payload)
      else await createAdminDestination(payload)
      toast.success(t('admin.destinations.saved'))
      navigate('/admin/destinations')
    } catch (err) {
      const errData = (err as { response?: { data?: Record<string, string[] | string> } })?.response?.data
      toast.error(errData ? Object.values(errData).flat().join(' ') : t('admin.destinations.saveFailed'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="pt-8 pb-16">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">
          {isEdit ? t('admin.destinations.editTitle') : t('admin.destinations.createTitle')}
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('admin.destinations.formSubtitle')}</p>

        {isLoading ? (
          <p className="text-slate-500 dark:text-slate-400">{t('common.loading')}</p>
        ) : (
          <Card padding="md">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label={t('admin.destinations.name')} {...register('name', { required: true })} error={errors.name ? t('admin.destinations.fieldRequired') : undefined} />
                <Input label={t('admin.destinations.nameMk')} {...register('name_mk')} />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label={t('admin.destinations.city')} {...register('city')} />
                <Input label={t('admin.destinations.country')} {...register('country', { required: true })} error={errors.country ? t('admin.destinations.fieldRequired') : undefined} />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label={t('admin.destinations.countryMk')} {...register('country_mk')} />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('admin.destinations.description')}</label>
                <textarea {...register('description', { required: true })} rows={3} className="input-base resize-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('admin.destinations.descriptionMk')}</label>
                <textarea {...register('description_mk')} rows={3} className="input-base resize-none" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('filter.travelType')}</label>
                  <select {...register('travel_type', { required: true })} className="input-base text-sm">
                    <option value="">—</option>
                    {categories.map((c) => <option key={c.slug} value={c.slug}>{c.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('filter.season')}</label>
                  <select {...register('best_season')} className="input-base text-sm">
                    <option value="">—</option>
                    {seasons.map((s) => <option key={s.slug} value={s.slug}>{s.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('filter.region')}</label>
                  <select {...register('region')} className="input-base text-sm">
                    <option value="">—</option>
                    {REGIONS.map((r) => <option key={r} value={r}>{t(`region.${r}`)}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Input label={t('admin.destinations.cost')} type="number" step="0.01" {...register('estimated_cost', { required: true })} error={errors.estimated_cost ? t('admin.destinations.fieldRequired') : undefined} />
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('destination.difficulty')}</label>
                  <select {...register('difficulty_level')} className="input-base text-sm">
                    {DIFFICULTIES.map((d) => <option key={d} value={d}>{t(`filter.${d}`)}</option>)}
                  </select>
                </div>
                <Input label={t('admin.destinations.popularity')} type="number" step="0.1" {...register('popularity_score')} />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label={t('admin.destinations.durationMin')} type="number" {...register('trip_duration_min')} />
                <Input label={t('admin.destinations.durationMax')} type="number" {...register('trip_duration_max')} />
              </div>

              <Input label={t('admin.destinations.imageUrl')} {...register('image_url')} placeholder="https://..." />
              <Input label={t('admin.destinations.imagesList')} {...register('images')} placeholder="https://..., https://..." />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label={t('admin.destinations.bookingUrl')}
                  placeholder={t('admin.destinations.urlAutoHint')}
                  {...register('booking_url', { pattern: { value: URL_PATTERN, message: t('admin.destinations.invalidUrl') } })}
                  error={errors.booking_url?.message}
                />
                <Input
                  label={t('admin.destinations.flightUrl')}
                  placeholder={t('admin.destinations.urlAutoHint')}
                  {...register('flight_url', { pattern: { value: URL_PATTERN, message: t('admin.destinations.invalidUrl') } })}
                  error={errors.flight_url?.message}
                />
              </div>
              <Input label={t('destination.activities')} {...register('activities')} placeholder={t('admin.destinations.activitiesPlaceholder')} />

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('destination.attractions')}</label>
                <textarea {...register('attractions')} rows={2} className="input-base resize-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('destination.travelTips')}</label>
                <textarea {...register('travel_tips')} rows={2} className="input-base resize-none" />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="secondary" onClick={() => navigate('/admin/destinations')}>{t('common.cancel')}</Button>
                <Button type="submit" isLoading={saving} leftIcon={<Save className="w-4 h-4" />}>{t('common.save')}</Button>
              </div>
            </form>
          </Card>
        )}
      </div>
    </div>
  )
}
