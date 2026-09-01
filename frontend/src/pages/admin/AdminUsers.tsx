import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Search, Plus, Pencil, Trash2, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'
import { getAdminUsers, updateAdminUser, deleteAdminUser } from '@/services/adminUsers'
import type { AdminUser } from '@/types/admin'
import { useAuth } from '@/hooks/useAuth'
import { useDebounce } from '@/hooks/useDebounce'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Badge from '@/components/ui/Badge'
import Modal from '@/components/ui/Modal'
import Skeleton from '@/components/ui/Skeleton'

export default function AdminUsers() {
  const { t } = useTranslation()
  const { user: me } = useAuth()
  const [users, setUsers] = useState<AdminUser[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 400)
  const [roleFilter, setRoleFilter] = useState<'' | 'user' | 'admin'>('')
  const [confirmDelete, setConfirmDelete] = useState<AdminUser | null>(null)
  const [deleting, setDeleting] = useState(false)

  const load = () => {
    setIsLoading(true)
    getAdminUsers({ search: debouncedSearch || undefined, role: roleFilter || undefined })
      .then((data) => setUsers(data.results))
      .catch(() => toast.error(t('admin.users.loadFailed')))
      .finally(() => setIsLoading(false))
  }

  useEffect(load, [debouncedSearch, roleFilter])

  const toggleActive = async (u: AdminUser) => {
    try {
      const updated = await updateAdminUser(u.id, { is_active: !u.is_active })
      setUsers((prev) => prev.map((x) => (x.id === u.id ? updated : x)))
      toast.success(updated.is_active ? t('admin.users.activated') : t('admin.users.deactivated'))
    } catch {
      toast.error(t('admin.users.updateFailed'))
    }
  }

  const handleDelete = async () => {
    if (!confirmDelete) return
    setDeleting(true)
    try {
      await deleteAdminUser(confirmDelete.id)
      setUsers((prev) => prev.filter((u) => u.id !== confirmDelete.id))
      toast.success(t('admin.users.deleted'))
      setConfirmDelete(null)
    } catch (err) {
      const message = (err as { response?: { data?: { error?: string } } })?.response?.data?.error
      toast.error(message || t('admin.users.deleteFailed'))
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="pt-8 pb-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-1 flex-wrap gap-3">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('admin.users.title')}</h1>
          <Link to="/admin/users/new">
            <Button leftIcon={<Plus className="w-4 h-4" />} size="sm">{t('admin.users.create')}</Button>
          </Link>
        </div>
        <p className="text-slate-500 dark:text-slate-400 mb-8">{t('admin.users.subtitle')}</p>

        <div className="flex flex-wrap gap-3 mb-6">
          <div className="flex-1 min-w-[240px]">
            <Input
              placeholder={t('admin.users.searchPlaceholder')}
              leftIcon={<Search className="w-4 h-4" />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex gap-1.5">
            {(['', 'user', 'admin'] as const).map((r) => (
              <button
                key={r || 'all'}
                onClick={() => setRoleFilter(r)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  roleFilter === r
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                }`}
              >
                {r === '' ? t('common.all') : r === 'admin' ? t('admin.role.admin') : t('admin.role.user')}
              </button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-2">{[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-16 rounded-xl" />)}</div>
        ) : users.length === 0 ? (
          <Card padding="lg" className="text-center">
            <p className="text-slate-500 dark:text-slate-400">{t('admin.users.empty')}</p>
          </Card>
        ) : (
          <Card padding="none" className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-700 text-left text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
                  <th className="px-4 py-3 font-medium">{t('admin.users.username')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.users.email')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.role.role')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.users.status')}</th>
                  <th className="px-4 py-3 font-medium text-right">{t('admin.users.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-slate-50 dark:border-slate-700/50 last:border-0 hover:bg-slate-50 dark:hover:bg-slate-700/20">
                    <td className="px-4 py-3 font-medium text-slate-900 dark:text-white flex items-center gap-1.5">
                      {u.role === 'admin' && <ShieldCheck className="w-3.5 h-3.5 text-primary-500 shrink-0" />}
                      {u.username}
                    </td>
                    <td className="px-4 py-3 text-slate-500 dark:text-slate-400">{u.email}</td>
                    <td className="px-4 py-3">
                      <Badge label={u.role === 'admin' ? t('admin.role.admin') : t('admin.role.user')} color={u.role === 'admin' ? 'purple' : 'slate'} />
                    </td>
                    <td className="px-4 py-3">
                      <button onClick={() => toggleActive(u)} disabled={u.id === me?.id}>
                        <Badge
                          label={u.is_active ? t('admin.users.active') : t('admin.users.inactive')}
                          color={u.is_active ? 'emerald' : 'rose'}
                          className={u.id === me?.id ? '' : 'cursor-pointer hover:opacity-80'}
                        />
                      </button>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <Link to={`/admin/users/${u.id}`} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500">
                          <Pencil className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => setConfirmDelete(u)}
                          disabled={u.id === me?.id}
                          className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-500 disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </div>

      <Modal isOpen={!!confirmDelete} onClose={() => setConfirmDelete(null)} title={t('admin.users.deleteConfirmTitle')}>
        <p className="text-sm text-slate-600 dark:text-slate-300 mb-6">
          {t('admin.users.deleteConfirmBody', { username: confirmDelete?.username })}
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmDelete(null)}>{t('common.cancel')}</Button>
          <Button variant="danger" onClick={handleDelete} isLoading={deleting}>{t('common.remove')}</Button>
        </div>
      </Modal>
    </div>
  )
}
