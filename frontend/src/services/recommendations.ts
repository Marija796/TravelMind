import api from './api'
import type { RecommendationResponse } from '@/types/recommendation'

export const getRecommendations = () =>
  api.get<RecommendationResponse>('/recommendations/').then((r) => r.data)
