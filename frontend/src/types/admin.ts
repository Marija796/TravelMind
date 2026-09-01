import type { Role, Gender, SimilarUser } from './user'
import type { TravelType, Season } from './destination'

export interface AdminUser {
  id: number
  username: string
  email: string
  role: Role
  is_active: boolean
  short_summary: string
  gender: Gender | ''
  preferred_travel_type: TravelType | ''
  preferred_season: Season | ''
  preferred_activities: string[]
  trip_duration_preference: number | null
  budget: string | null
  date_joined: string
  last_login: string | null
}

export interface AdminUserListParams {
  search?: string
  role?: Role | ''
  is_active?: boolean | ''
  page?: number
}

// preferred_travel_type/preferred_season are plain strings (not the static
// TravelType/Season unions) since they're dynamic taxonomy slugs, matching
// AdminDestinationPayload's precedent for the same admin-form vs. static-
// union mismatch.
export interface AdminUserCreatePayload {
  username: string
  email: string
  password: string
  role: Role
  is_active: boolean
  short_summary?: string
  gender?: string
  preferred_travel_type?: string | null
  preferred_season?: string | null
  preferred_activities?: string[]
  trip_duration_preference?: number | null
  budget?: string | null
}

export interface AdminUserUpdatePayload {
  username?: string
  email?: string
  role?: Role
  is_active?: boolean
  short_summary?: string
  gender?: string
  preferred_travel_type?: string | null
  preferred_season?: string | null
  preferred_activities?: string[]
  trip_duration_preference?: number | null
  budget?: string | null
}

export interface AdminSimilarUsersResponse {
  count: number
  results: SimilarUser[]
  reason: 'no_preferences_set' | null
  target: {
    id: number
    username: string
    preferred_travel_type: string | null
    preferred_season: string | null
    preferred_activities: string[]
    budget: string | null
    trip_duration_preference: number | null
  }
}

export interface AdminStats {
  user_count: number
  active_user_count: number
  inactive_user_count: number
  admin_count: number
  destination_count: number
  average_destination_rating: number | null
  total_destination_reviews: number
  average_app_rating: number | null
  total_app_reviews: number
  most_popular_destinations: Array<{
    id: number
    name: string
    slug: string
    review_count_annotated: number
  }>
  most_common_travel_types: Array<{ slug: string; name: string; count: number }>
  most_popular_seasons: Array<{ slug: string; name: string; count: number }>
  most_searched_destinations: Array<{ query: string; count: number }>
  users_with_preferences_count: number
}
