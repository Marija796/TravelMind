import type { TravelType, Season } from './destination'

export type Gender = 'male' | 'female' | 'other' | 'prefer_not_to_say'
export type Role = 'user' | 'admin'

export interface User {
  id: number
  username: string
  email: string
  role: Role
  is_verified: boolean
  short_summary: string
  gender: Gender | ''
  preferred_travel_type: TravelType | ''
  preferred_season: Season | ''
  preferred_activities: string[]
  trip_duration_preference: number | null
  budget: string | null
  profile_image: string | null
  favorite_destination_ids: number[]
  wishlist_destination_ids: number[]
  visited_destination_ids: number[]
}

export interface SimilarUser {
  id: number
  username: string
  gender: Gender | ''
  short_summary: string
  profile_image: string | null
  similarity: number
}

export interface SimilarUsersResponse {
  count: number
  results: SimilarUser[]
  reason: 'no_preferences_set' | null
}

// Returned by /users/destinations/<id>/interested/ - a SimilarUser plus why
// they showed up for this specific destination: 'direct' (they favorited/
// wishlisted it themselves) or 'similar_destination' (they favorited/
// wishlisted a destination with the same travel type or country, only used
// to backfill when the direct pool is thin).
export interface DestinationInterestedUser extends SimilarUser {
  interest: 'direct' | 'similar_destination'
}

export interface DestinationInterestedUsersResponse {
  count: number
  results: DestinationInterestedUser[]
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
  password2: string
}

export interface LoginResponse {
  access: string
  refresh: string
}

export interface UpdateProfilePayload {
  username?: string
  short_summary?: string
  gender?: Gender | ''
  preferred_travel_type?: TravelType | ''
  preferred_season?: Season | ''
  preferred_activities?: string[]
  trip_duration_preference?: number | null
  budget?: string | null
}

export interface GoogleAuthPayload { code?: string; credential?: string }
export interface GoogleAuthResponse { access: string; refresh: string; user: User }
export interface PasswordResetPayload { email: string }
export interface PasswordResetResponse { message: string; dev_reset_url?: string }
export interface PasswordResetConfirmPayload {
  uid: string
  token: string
  new_password: string
  new_password2: string
}

export interface VerifyEmailPayload { uid: string; token: string }
export interface ResendVerificationPayload { email: string }
