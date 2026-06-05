import api from './api'
import type { Destination } from '@/types/destination'

export const getVisited = () =>
  api.get<Destination[]>('/users/visited/').then((r) => r.data)

export const markVisited = (id: number) =>
  api.post(`/users/visited/${id}/`).then((r) => r.data)

export const removeFromVisited = (id: number) =>
  api.delete(`/users/visited/${id}/`).then((r) => r.data)
