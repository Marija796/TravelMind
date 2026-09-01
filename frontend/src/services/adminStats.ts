import api from './api'
import type { AdminStats } from '@/types/admin'

export const getAdminStats = () =>
  api.get<AdminStats>('/admin/stats/').then((r) => r.data)
