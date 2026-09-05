import type { Destination } from './destination'

export interface ScoreBreakdown {
  type_match: number
  budget_fit: number
  season_match: number
  activity_overlap: number
}

export interface ScoredDestination extends Destination {
  /** Final hybrid score in [0, 0.97] - the higher of whichever signal(s)
   *  qualified this destination (explicit preferences via a weighted
   *  geometric mean, the user's own favorited/visited history, and/or
   *  collaborative filtering from similar users), each gated by its own
   *  independent threshold. See `recommendation_source` for which. */
  score: number
  score_breakdown: ScoreBreakdown
  match_explanation: string
  /** Human-readable band for `score` - "Excellent Match" / "Great Match" /
   *  "Good Match" / "Fair Match" - so users see match strength at a glance. */
  match_quality: string
  /** Which signal(s) qualified this destination: 'preference' (explicit
   *  preferences and/or the user's own history), 'collaborative' (similar
   *  users' favorites/wishlist/ratings/visits only), or 'hybrid' (both). */
  recommendation_source: 'preference' | 'collaborative' | 'hybrid'
}

export interface RecommendationResponse {
  count: number
  results: ScoredDestination[]
}
