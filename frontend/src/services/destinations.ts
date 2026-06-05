import api from './api'
import type { Destination, FilterParams, PaginatedResponse } from '@/types/destination'

export const getDestinations = (params?: FilterParams) =>
  api.get<PaginatedResponse<Destination>>('/destinations/', { params }).then((r) => r.data)

export const getDestination = (id: number) =>
  api.get<Destination>(`/destinations/${id}/`).then((r) => r.data)

export const getDestinationBySlug = (slug: string) =>
  api.get<Destination>(`/destinations/by-slug/${slug}/`).then((r) => r.data)

export const getFeaturedDestinations = () =>
  api.get<PaginatedResponse<Destination>>('/destinations/', {
    params: { ordering: '-popularity_score', page_size: 6 },
  }).then((r) => r.data)
