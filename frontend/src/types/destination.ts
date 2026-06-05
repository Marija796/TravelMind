export type TravelType = 'beach' | 'mountain' | 'city' | 'adventure' | 'cultural' | 'luxury' | 'relaxation'
export type Season = 'spring' | 'summer' | 'autumn' | 'winter'
export type DifficultyLevel = 'easy' | 'moderate' | 'challenging'
export type Region = 'europe' | 'asia' | 'north_america' | 'south_america' | 'africa' | 'oceania'

export interface Destination {
  id: number
  slug: string
  name: string
  city: string
  country: string
  region: string
  description: string
  description_mk: string
  travel_type: TravelType
  estimated_cost: string
  image_url: string | null
  images: string[]
  activities: string[]
  attractions: string
  travel_tips: string
  best_season: Season | ''
  difficulty_level: DifficultyLevel
  trip_duration_min: number
  trip_duration_max: number
  popularity_score: number
  latitude: number | null
  longitude: number | null
  cost_breakdown: {
    currency: string
    flight: number
    accommodation: number
    daily_expenses: number
    nights: number
  } | null
  average_rating: number | null
  review_count: number
  is_favorited: boolean
  is_wishlisted: boolean
  is_visited: boolean
  created_at: string
}

export interface FilterParams {
  search?: string
  travel_type?: TravelType | ''
  budget_max?: number | ''
  budget_min?: number | ''
  season?: Season | ''
  difficulty_level?: DifficultyLevel | ''
  duration_max?: number | ''
  ordering?: string
  page?: number
  country?: string
  region?: Region | ''
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export const TRAVEL_TYPE_LABELS: Record<TravelType, string> = {
  beach: 'Beach',
  mountain: 'Mountain',
  city: 'City Tourism',
  adventure: 'Adventure',
  cultural: 'Cultural',
  luxury: 'Luxury',
  relaxation: 'Relaxation',
}

export const SEASON_LABELS: Record<Season, string> = {
  spring: 'Spring',
  summer: 'Summer',
  autumn: 'Autumn',
  winter: 'Winter',
}

export const DIFFICULTY_LABELS: Record<DifficultyLevel, string> = {
  easy: 'Easy',
  moderate: 'Moderate',
  challenging: 'Challenging',
}

export const ACTIVITY_OPTIONS = [
  'Hiking', 'Beaches', 'Nightlife', 'Museums', 'Food & Dining',
  'Skiing', 'Surfing', 'Snorkeling', 'Rock Climbing', 'Cycling',
  'Shopping', 'Art & Culture', 'Photography', 'Wildlife Safari',
  'Spa & Wellness', 'Water Sports', 'City Tours', 'Wine Tasting',
]

export const REGION_LABELS: Record<Region, string> = {
  europe: 'Europe',
  asia: 'Asia',
  north_america: 'North America',
  south_america: 'South America',
  africa: 'Africa',
  oceania: 'Australia & Oceania',
}

export const TRAVEL_TYPE_COLORS: Record<TravelType, string> = {
  beach: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  mountain: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
  city: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  adventure: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  cultural: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
  luxury: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300',
  relaxation: 'bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300',
}
