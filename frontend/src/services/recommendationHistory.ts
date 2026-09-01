import api from './api'
import type { RecommendationHistoryEntry } from '@/types/recommendationHistory'
import type { PaginatedResponse } from '@/types/destination'

export const getRecommendationHistory = (page = 1) =>
  api.get<PaginatedResponse<RecommendationHistoryEntry>>('/recommendations/history/', { params: { page } }).then((r) => r.data)
