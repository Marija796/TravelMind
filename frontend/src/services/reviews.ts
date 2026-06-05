import api from './api'
import type { Review, CreateReviewPayload } from '@/types/review'

export const getReviews = (destinationId: number) =>
  api.get<Review[]>(`/reviews/${destinationId}/`).then((r) => r.data)

export const createReview = (destinationId: number, data: CreateReviewPayload) =>
  api.post<Review>(`/reviews/${destinationId}/`, data).then((r) => r.data)
