export interface Review {
  id: number
  username: string
  avatar_url: string | null
  destination: number
  rating: 1 | 2 | 3 | 4 | 5
  comment: string
  created_at: string
}

export interface CreateReviewPayload {
  rating: number
  comment: string
}
