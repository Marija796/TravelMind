import api from './api'
import type { AdminUser, AdminUserListParams, AdminUserCreatePayload, AdminUserUpdatePayload, AdminSimilarUsersResponse } from '@/types/admin'
import type { PaginatedResponse } from '@/types/destination'

export const getAdminUsers = (params?: AdminUserListParams) =>
  api.get<PaginatedResponse<AdminUser>>('/users/admin/users/', { params }).then((r) => r.data)

export const getAdminUser = (id: number) =>
  api.get<AdminUser>(`/users/admin/users/${id}/`).then((r) => r.data)

export const createAdminUser = (data: AdminUserCreatePayload) =>
  api.post<AdminUser>('/users/admin/users/create/', data).then((r) => r.data)

export const updateAdminUser = (id: number, data: AdminUserUpdatePayload) =>
  api.patch<AdminUser>(`/users/admin/users/${id}/`, data).then((r) => r.data)

export const deleteAdminUser = (id: number) =>
  api.delete(`/users/admin/users/${id}/`)

export const getAdminUserSimilar = (id: number) =>
  api.get<AdminSimilarUsersResponse>(`/users/admin/users/${id}/similar/`).then((r) => r.data)
