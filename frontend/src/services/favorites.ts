import api from './api'
import type { Destination } from '@/types/destination'

export const getFavorites = () =>
  api.get<Destination[]>('/users/favorites/').then((r) => r.data)

export const addFavorite = (id: number) =>
  api.post(`/users/favorites/${id}/`).then((r) => r.data)

export const removeFavorite = (id: number) =>
  api.delete(`/users/favorites/${id}/`).then((r) => r.data)
