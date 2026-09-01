import api from './api'
import type { Destination } from '@/types/destination'

// travel_type/best_season/difficulty_level/region are typed as plain
// strings here (not their literal-union types) since this payload comes
// straight from uncontrolled <select>/form values, and travel_type/
// best_season in particular can be a dynamic taxonomy slug that doesn't
// exist in the frontend's static union.
export type AdminDestinationPayload = Partial<
  Omit<Destination, 'travel_type' | 'best_season' | 'difficulty_level' | 'region'>
> & {
  travel_type?: string
  best_season?: string | null
  difficulty_level?: string
  region?: string
}

// List/detail reuse the existing public services/destinations.ts - only
// create/update/delete need admin-gated endpoints.
export const createAdminDestination = (data: AdminDestinationPayload) =>
  api.post<Destination>('/destinations/admin/create/', data).then((r) => r.data)

export const updateAdminDestination = (id: number, data: AdminDestinationPayload) =>
  api.patch<Destination>(`/destinations/admin/${id}/`, data).then((r) => r.data)

export const deleteAdminDestination = (id: number) =>
  api.delete(`/destinations/admin/${id}/`)
