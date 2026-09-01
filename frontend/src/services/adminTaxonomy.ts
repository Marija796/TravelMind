import api from './api'
import type { TravelCategoryDTO, SeasonDTO } from '@/types/taxonomy'

// List reuses the existing public services/taxonomy.ts - only
// create/update/delete need admin-gated endpoints.
export const createTravelCategory = (data: Omit<TravelCategoryDTO, 'id'>) =>
  api.post<TravelCategoryDTO>('/destinations/admin/categories/', data).then((r) => r.data)

export const updateTravelCategory = (id: number, data: Partial<Omit<TravelCategoryDTO, 'id'>>) =>
  api.patch<TravelCategoryDTO>(`/destinations/admin/categories/${id}/`, data).then((r) => r.data)

export const deleteTravelCategory = (id: number) =>
  api.delete(`/destinations/admin/categories/${id}/`)

export const createSeason = (data: Omit<SeasonDTO, 'id'>) =>
  api.post<SeasonDTO>('/destinations/admin/seasons/', data).then((r) => r.data)

export const updateSeason = (id: number, data: Partial<Omit<SeasonDTO, 'id'>>) =>
  api.patch<SeasonDTO>(`/destinations/admin/seasons/${id}/`, data).then((r) => r.data)

export const deleteSeason = (id: number) =>
  api.delete(`/destinations/admin/seasons/${id}/`)
