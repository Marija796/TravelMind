import api from './api'
import type { Destination } from '@/types/destination'

export const getWishlist = () =>
  api.get<Destination[]>('/users/wishlist/').then((r) => r.data)

export const addToWishlist = (id: number) =>
  api.post(`/users/wishlist/${id}/`).then((r) => r.data)

export const removeFromWishlist = (id: number) =>
  api.delete(`/users/wishlist/${id}/`).then((r) => r.data)
