import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Search, Plus, Pencil, Trash2, ChevronLeft, ChevronRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { getDestinations } from '@/services/destinations'
import { deleteAdminDestination } from '@/services/adminDestinations'
import type { Destination } from '@/types/destination'
import { useDebounce } from '@/hooks/useDebounce'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Modal from '@/components/ui/Modal'
import Skeleton from '@/components/ui/Skeleton'

const PAGE_SIZE = 12

export default function AdminDestinations() {
  const { t } = useTranslation()
  const [destinations, setDestinations] = useState<Destination[]>([])
  const [count, setCount] = useState(0)
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 400)
  const [confirmDelete, setConfirmDelete] = useState<Destination | null>(null)
  const [deleting, setDeleting] = useState(false)

  const load = () => {
    setIsLoading(true)
    getDestinations({ search: debouncedSearch || undefined, page })
      .then((data) => { setDestinations(data.results); setCount(data.count) })
      .catch(() => toast.error(t('admin.destinations.loadFailed')))
      .finally(() => setIsLoading(false))
  }

  useEffect(load, [debouncedSearch, page])
  useEffect(() => setPage(1), [debouncedSearch])

  const handleDelete = async () => {
    if (!confirmDelete) return
    setDeleting(true)
    try {
      await deleteAdminDestination(confirmDelete.id)
      toast.success(t('admin.destinations.deleted'))
      setConfirmDelete(null)
      load()
    } catch {
      toast.error(t('admin.destinations.deleteFailed'))
    } finally {
      setDeleting(false)
    }
  }

  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE))

  return (
    <div className="pt-8 pb-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-1 flex-wrap gap-3">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('admin.destinations.title')}</h1>
          <Link to="/admin/destinations/new">
            <Button leftIcon={<Plus className="w-4 h-4" />} size="sm">{t('admin.destinations.create')}</Button>
          </Link>
        </div>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('admin.destinations.subtitle')}</p>

        <div className="mb-6 max-w-sm">
          <Input
            placeholder={t('admin.destinations.searchPlaceholder')}
            leftIcon={<Search className="w-4 h-4" />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {isLoading ? (
          <div className="space-y-2">{[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-16 rounded-xl" />)}</div>
        ) : destinations.length === 0 ? (
          <Card padding="lg" className="text-center">
            <p className="text-slate-500 dark:text-slate-400">{t('admin.destinations.empty')}</p>
          </Card>
        ) : (
          <>
            <Card padding="none" className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-700 text-left text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    <th className="px-4 py-3 font-medium">{t('admin.destinations.name')}</th>
                    <th className="px-4 py-3 font-medium">{t('admin.destinations.country')}</th>
                    <th className="px-4 py-3 font-medium">{t('admin.destinations.cost')}</th>
                    <th className="px-4 py-3 font-medium text-right">{t('admin.users.actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {destinations.map((d) => (
                    <tr key={d.id} className="border-b border-slate-50 dark:border-slate-700/50 last:border-0 hover:bg-slate-50 dark:hover:bg-slate-700/20">
                      <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">{d.name}</td>
                      <td className="px-4 py-3 text-slate-500 dark:text-slate-400">{d.country}</td>
                      <td className="px-4 py-3 text-slate-500 dark:text-slate-400">€{Number(d.estimated_cost).toLocaleString()}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-1">
                          <Link to={`/admin/destinations/${d.id}`} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500">
                            <Pencil className="w-4 h-4" />
                          </Link>
                          <button onClick={() => setConfirmDelete(d)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-500">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-3 mt-6">
                <Button variant="secondary" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} leftIcon={<ChevronLeft className="w-4 h-4" />}>
                  {t('common.back')}
                </Button>
                <span className="text-sm text-slate-500 dark:text-slate-400">{page} / {totalPages}</span>
                <Button variant="secondary" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages} rightIcon={<ChevronRight className="w-4 h-4" />}>
                  {t('common.viewAll')}
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      <Modal isOpen={!!confirmDelete} onClose={() => setConfirmDelete(null)} title={t('admin.destinations.deleteConfirmTitle')}>
        <p className="text-sm text-slate-600 dark:text-slate-300 mb-6">
          {t('admin.destinations.deleteConfirmBody', { name: confirmDelete?.name })}
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmDelete(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={handleDelete} isLoading={deleting}>{t('common.remove')}</Button>
        </div>
      </Modal>
    </div>
  )
}
