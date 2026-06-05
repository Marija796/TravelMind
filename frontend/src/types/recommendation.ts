import type { Destination } from './destination'

export interface ScoreBreakdown {
  type_match: number
  budget_fit: number
  season_match: number
  activity_overlap: number
}

export interface ScoredDestination extends Destination {
  score: number
  score_breakdown: ScoreBreakdown
  match_explanation: string
}

export interface RecommendationResponse {
  count: number
  results: ScoredDestination[]
}
