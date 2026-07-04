import api from './api'
import type { AppReview, AppReviewListResponse, UpsertAppReviewPayload } from '@/types/review'

export const getAppReviews = () =>
  api.get<AppReviewListResponse>('/reviews/app/').then((r) => r.data)

export const getMyAppReview = () =>
  api.get<AppReview | null>('/reviews/app/me/').then((r) => r.data)

export const createAppReview = (data: UpsertAppReviewPayload) =>
  api.post<AppReview>('/reviews/app/me/', data).then((r) => r.data)

export const updateAppReview = (data: UpsertAppReviewPayload) =>
  api.patch<AppReview>('/reviews/app/me/', data).then((r) => r.data)

export const deleteAppReview = () => api.delete('/reviews/app/me/')
