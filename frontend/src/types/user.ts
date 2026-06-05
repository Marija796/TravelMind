import type { TravelType, Season } from './destination'

export interface User {
  id: number
  username: string
  email: string
  bio: string
  preferred_travel_type: TravelType | ''
  preferred_season: Season | ''
  preferred_activities: string[]
  trip_duration_preference: number | null
  budget: string | null
  avatar_url: string | null
  favorite_destination_ids: number[]
  wishlist_destination_ids: number[]
  visited_destination_ids: number[]
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
  bio?: string
  preferred_travel_type?: TravelType | ''
  preferred_season?: Season | ''
  preferred_activities?: string[]
  trip_duration_preference?: number | null
  budget?: string | null
  avatar_url?: string | null
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
