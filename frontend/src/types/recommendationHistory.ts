export interface RecommendationHistoryPreferencesSnapshot {
  travel_type: string | null
  season: string | null
  activities: string[]
  budget: string | null
  trip_duration_preference: number | null
}

export interface RecommendationHistoryResultSnapshot {
  destination_id: number
  name: string
  // Absent on history rows written before bilingual snapshots were added.
  name_mk?: string
  slug: string
  score: number
  match_quality: string
}

export interface RecommendationHistoryEntry {
  id: number
  preferences_snapshot: RecommendationHistoryPreferencesSnapshot
  results_snapshot: RecommendationHistoryResultSnapshot[]
  result_count: number
  created_at: string
}
