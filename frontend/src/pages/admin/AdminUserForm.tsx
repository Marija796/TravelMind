import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import { Save } from 'lucide-react'
import toast from 'react-hot-toast'
import { getAdminUser, createAdminUser, updateAdminUser } from '@/services/adminUsers'
import type { Role } from '@/types/user'
import { ACTIVITY_OPTIONS } from '@/types/destination'
import { useTravelCategories, useSeasons } from '@/hooks/useTaxonomy'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import PreferenceSelector from '@/components/common/PreferenceSelector'

interface FormData {
  username: string
  email: string
  password: string
  role: Role
  is_active: boolean
  short_summary: string
  gender: string
  preferred_travel_type: string
  preferred_season: string
  budget: string
  trip_duration_preference: string
}

const defaultValues: FormData = {
  username: '', email: '', password: '', role: 'user', is_active: true,
  short_summary: '', gender: '', preferred_travel_type: '', preferred_season: '',
  budget: '', trip_duration_preference: '',
}

export default function AdminUserForm() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEdit = !!id
  const [isLoading, setIsLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [activities, setActivities] = useState<string[]>([])
  const { categories } = useTravelCategories()
  const { seasons } = useSeasons()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({ defaultValues })

  useEffect(() => {
    if (!id) return
    getAdminUser(Number(id))
      .then((u) => {
        reset({
          username: u.username, email: u.email, password: '', role: u.role, is_active: u.is_active,
          short_summary: u.short_summary || '', gender: u.gender || '',
          preferred_travel_type: u.preferred_travel_type || '', preferred_season: u.preferred_season || '',
          budget: u.budget || '', trip_duration_preference: u.trip_duration_preference ? String(u.trip_duration_preference) : '',
        })
        setActivities(u.preferred_activities || [])
      })
      .catch(() => toast.error(t('admin.users.loadFailed')))
      .finally(() => setIsLoading(false))
  }, [id, reset, t])

  const onSubmit = async (data: FormData) => {
    setSaving(true)
    const preferencePayload = {
      short_summary: data.short_summary,
      gender: data.gender,
      preferred_travel_type: data.preferred_travel_type || null,
      preferred_season: data.preferred_season || null,
      preferred_activities: activities,
      budget: data.budget || null,
      trip_duration_preference: data.trip_duration_preference ? Number(data.trip_duration_preference) : null,
    }
    try {
      if (isEdit) {
        await updateAdminUser(Number(id), {
          username: data.username, email: data.email, role: data.role, is_active: data.is_active,
          ...preferencePayload,
        })
      } else {
        await createAdminUser({
          username: data.username, email: data.email, password: data.password, role: data.role, is_active: data.is_active,
          ...preferencePayload,
        })
      }
      toast.success(t('admin.users.saved'))
      navigate('/admin/users')
    } catch (err) {
      const data = (err as { response?: { data?: Record<string, string[] | string> } })?.response?.data
      toast.error(data ? Object.values(data).flat().join(' ') : t('admin.users.saveFailed'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="pt-8 pb-16">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">
          {isEdit ? t('admin.users.editTitle') : t('admin.users.createTitle')}
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('admin.users.formSubtitle')}</p>

        {isLoading ? (
          <p className="text-slate-500 dark:text-slate-400">{t('common.loading')}</p>
        ) : (
          <Card padding="md">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input
                label={t('admin.users.username')}
                {...register('username', { required: true })}
                error={errors.username ? t('profile.usernameRequired') : undefined}
              />
              <Input
                label={t('admin.users.email')}
                type="email"
                {...register('email', { required: true })}
                error={errors.email ? t('admin.users.emailRequired') : undefined}
              />
              {!isEdit && (
                <Input
                  label={t('auth.password')}
                  type="password"
                  {...register('password', { required: !isEdit, minLength: 8 })}
                  error={errors.password ? t('auth.minPasswordChars') : undefined}
                />
              )}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('admin.role.role')}</label>
                  <select {...register('role')} className="input-base text-sm">
                    <option value="user">{t('admin.role.user')}</option>
                    <option value="admin">{t('admin.role.admin')}</option>
                  </select>
                </div>
                <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300 mt-6 sm:mt-0 sm:self-end sm:mb-2.5">
                  <input type="checkbox" {...register('is_active')} className="rounded border-slate-300" />
                  {t('admin.users.active')}
                </label>
              </div>

              <hr className="border-slate-100 dark:border-slate-700" />
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{t('admin.users.preferencesSection')}</p>

              <Input label={t('profile.shortSummary')} {...register('short_summary')} />

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('filter.travelType')}</label>
                  <select {...register('preferred_travel_type')} className="input-base text-sm">
                    <option value="">—</option>
                    {categories.map((c) => <option key={c.slug} value={c.slug}>{c.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('filter.season')}</label>
                  <select {...register('preferred_season')} className="input-base text-sm">
                    <option value="">—</option>
                    {seasons.map((s) => <option key={s.slug} value={s.slug}>{s.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">{t('profile.gender')}</label>
                  <select {...register('gender')} className="input-base text-sm">
                    <option value="">—</option>
                    <option value="male">{t('gender.male')}</option>
                    <option value="female">{t('gender.female')}</option>
                    <option value="other">{t('gender.other')}</option>
                    <option value="prefer_not_to_say">{t('gender.prefer_not_to_say')}</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label={t('recommendations.maxBudget')} type="number" step="0.01" {...register('budget')} />
                <Input label={t('recommendations.tripDuration')} type="number" {...register('trip_duration_preference')} />
              </div>

              <PreferenceSelector
                label={t('recommendations.activities')}
                options={ACTIVITY_OPTIONS.map((a) => ({ value: a, label: a }))}
                selected={activities}
                onChange={setActivities}
              />

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="secondary" onClick={() => navigate('/admin/users')}>{t('common.cancel')}</Button>
                <Button type="submit" isLoading={saving} leftIcon={<Save className="w-4 h-4" />}>{t('common.save')}</Button>
              </div>
            </form>
          </Card>
        )}
      </div>
    </div>
  )
}
