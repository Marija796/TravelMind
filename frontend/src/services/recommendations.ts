import api from './api'
import type { RecommendationResponse } from '@/types/recommendation'

export const getRecommendations = () =>
  api.get<RecommendationResponse>('/recommendations/').then((r) => r.data)

export interface AnonymousRecParams {
  travel_type?: string
  budget?: string
  season?: string
  activities?: string
}

export const getAnonymousRecommendations = (params: AnonymousRecParams) =>
  api.get<RecommendationResponse>('/recommendations/anonymous/', { params }).then((r) => r.data)
