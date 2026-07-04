import type { Destination } from './destination'

export interface ScoreBreakdown {
  type_match: number
  budget_fit: number
  season_match: number
  activity_overlap: number
}

export interface ScoredDestination extends Destination {
  /** Weighted geometric mean of per-preference-group similarity (travel
   *  type, season, activities, budget, duration), in the range [0.85, 1.0] -
   *  only destinations meeting the 0.85 "strong match" threshold are
   *  returned. A geometric mean means any single badly-conflicting
   *  preference pulls the score toward 0, so matches are sharply
   *  differentiated rather than clustering near the same value. */
  score: number
  score_breakdown: ScoreBreakdown
  match_explanation: string
  /** Human-readable band for `score` - "Excellent Match" / "Great Match" /
   *  "Good Match" / "Fair Match" - so users see match strength at a glance. */
  match_quality: string
}

export interface RecommendationResponse {
  count: number
  results: ScoredDestination[]
}
