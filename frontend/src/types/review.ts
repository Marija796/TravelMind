export interface Review {
  id: number
  username: string
  profile_image: string | null
  destination: number
  rating: 1 | 2 | 3 | 4 | 5
  comment: string
  created_at: string
}

export interface CreateReviewPayload {
  rating: number
  comment: string
}

export interface AppReview {
  id: number
  username: string
  profile_image: string | null
  rating: 1 | 2 | 3 | 4 | 5
  comment: string
  created_at: string
  updated_at: string
}

export interface AppReviewListResponse {
  count: number
  average_rating: number | null
  total_reviews: number
  results: AppReview[]
}

export interface UpsertAppReviewPayload {
  rating: number
  comment: string
}
