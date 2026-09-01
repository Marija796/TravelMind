import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Trash2, Pencil, Check, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { getTravelCategories, getSeasons } from '@/services/taxonomy'
import {
  createTravelCategory, updateTravelCategory, deleteTravelCategory,
  createSeason, updateSeason, deleteSeason,
} from '@/services/adminTaxonomy'
import { invalidateTaxonomyCache } from '@/hooks/useTaxonomy'
import type { TravelCategoryDTO, SeasonDTO } from '@/types/taxonomy'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

interface RowFormState { slug: string; name: string; name_mk: string }
const emptyRow: RowFormState = { slug: '', name: '', name_mk: '' }

function TaxonomySection<T extends TravelCategoryDTO | SeasonDTO>({
  title, items, onReload, onCreate, onUpdate, onDelete,
}: {
  title: string
  items: T[]
  onReload: () => void
  onCreate: (data: RowFormState) => Promise<unknown>
  onUpdate: (id: number, data: RowFormState) => Promise<unknown>
  onDelete: (id: number) => Promise<unknown>
}) {
  const { t } = useTranslation()
  const [adding, setAdding] = useState(false)
  const [newRow, setNewRow] = useState<RowFormState>(emptyRow)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editRow, setEditRow] = useState<RowFormState>(emptyRow)
  const [busy, setBusy] = useState(false)

  const startEdit = (item: T) => {
    setEditingId(item.id)
    setEditRow({ slug: item.slug, name: item.name, name_mk: item.name_mk })
  }

  const submitCreate = async () => {
    if (!newRow.slug || !newRow.name) return
    setBusy(true)
    try {
      await onCreate(newRow)
      setNewRow(emptyRow)
      setAdding(false)
      onReload()
    } catch {
      toast.error(t('admin.taxonomy.saveFailed'))
    } finally {
      setBusy(false)
    }
  }

  const submitEdit = async () => {
    if (editingId === null) return
    setBusy(true)
    try {
      await onUpdate(editingId, editRow)
      setEditingId(null)
      onReload()
    } catch {
      toast.error(t('admin.taxonomy.saveFailed'))
    } finally {
      setBusy(false)
    }
  }

  const handleDelete = async (id: number) => {
    setBusy(true)
    try {
      await onDelete(id)
      onReload()
    } catch (err) {
      const message = (err as { response?: { data?: { error?: string } } })?.response?.data?.error
      toast.error(message || t('admin.taxonomy.deleteFailed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card padding="md">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h2>
        <Button size="sm" variant="secondary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setAdding((v) => !v)}>
          {t('admin.taxonomy.add')}
        </Button>
      </div>

      {adding && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-4 p-3 bg-slate-50 dark:bg-slate-900/40 rounded-xl">
          <Input placeholder={t('admin.taxonomy.slug')} value={newRow.slug} onChange={(e) => setNewRow({ ...newRow, slug: e.target.value })} />
          <Input placeholder={t('admin.taxonomy.nameEn')} value={newRow.name} onChange={(e) => setNewRow({ ...newRow, name: e.target.value })} />
          <div className="flex gap-2">
            <Input placeholder={t('admin.taxonomy.nameMk')} value={newRow.name_mk} onChange={(e) => setNewRow({ ...newRow, name_mk: e.target.value })} />
            <Button size="sm" onClick={submitCreate} isLoading={busy}><Check className="w-4 h-4" /></Button>
          </div>
        </div>
      )}

      <ul className="space-y-1.5">
        {items.map((item) => (
          <li key={item.id} className="flex items-center gap-2 py-1.5 border-b border-slate-50 dark:border-slate-700/50 last:border-0">
            {editingId === item.id ? (
              <>
                <Input value={editRow.slug} onChange={(e) => setEditRow({ ...editRow, slug: e.target.value })} className="!py-1 text-xs" />
                <Input value={editRow.name} onChange={(e) => setEditRow({ ...editRow, name: e.target.value })} className="!py-1 text-xs" />
                <Input value={editRow.name_mk} onChange={(e) => setEditRow({ ...editRow, name_mk: e.target.value })} className="!py-1 text-xs" />
                <button onClick={submitEdit} disabled={busy} className="p-1.5 text-emerald-600"><Check className="w-4 h-4" /></button>
                <button onClick={() => setEditingId(null)} className="p-1.5 text-slate-400"><X className="w-4 h-4" /></button>
              </>
            ) : (
              <>
                <span className="text-xs font-mono text-slate-400 w-24 shrink-0">{item.slug}</span>
                <span className="flex-1 text-sm text-slate-900 dark:text-white">{item.name}</span>
                <span className="flex-1 text-sm text-slate-500 dark:text-slate-400">{item.name_mk || '—'}</span>
                <button onClick={() => startEdit(item)} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500">
                  <Pencil className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => handleDelete(item.id)} disabled={busy} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-500">
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </>
            )}
          </li>
        ))}
      </ul>
    </Card>
  )
}

export default function AdminTaxonomy() {
  const { t } = useTranslation()
  const [categories, setCategories] = useState<TravelCategoryDTO[]>([])
  const [seasons, setSeasons] = useState<SeasonDTO[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = () => {
    // Every reload here follows an admin mutation (or is the initial load),
    // so drop the shared cache too - otherwise a FilterPanel/Profile/
    // Recommendations instance that mounts later in this same SPA session
    // (no full page reload) would keep serving the pre-mutation list.
    invalidateTaxonomyCache()
    Promise.all([getTravelCategories(), getSeasons()])
      .then(([cats, seas]) => { setCategories(cats); setSeasons(seas) })
      .catch(() => toast.error(t('admin.taxonomy.loadFailed')))
      .finally(() => setIsLoading(false))
  }

  useEffect(reload, [])

  return (
    <div className="pt-8 pb-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{t('admin.taxonomy.title')}</h1>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('admin.taxonomy.subtitle')}</p>

        {isLoading ? (
          <p className="text-slate-500 dark:text-slate-400">{t('common.loading')}</p>
        ) : (
          <div className="space-y-6">
            <TaxonomySection
              title={t('admin.taxonomy.categories')}
              items={categories}
              onReload={reload}
              onCreate={(data) => createTravelCategory({ ...data, icon: '', order: categories.length })}
              onUpdate={(id, data) => updateTravelCategory(id, data)}
              onDelete={(id) => deleteTravelCategory(id)}
            />
            <TaxonomySection
              title={t('admin.taxonomy.seasons')}
              items={seasons}
              onReload={reload}
              onCreate={(data) => createSeason({ ...data, order: seasons.length })}
              onUpdate={(id, data) => updateSeason(id, data)}
              onDelete={(id) => deleteSeason(id)}
            />
          </div>
        )}
      </div>
    </div>
  )
}
