import api from './api'
import type { SimilarUsersResponse } from '@/types/user'

export const getSimilarUsers = () =>
  api.get<SimilarUsersResponse>('/users/similar/').then((r) => r.data)
