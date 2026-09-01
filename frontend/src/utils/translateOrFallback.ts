import type { TFunction } from 'i18next'

/**
 * Looks up a static i18n key (e.g. travelType.beach) for the 7/4 originally
 * seeded categories/seasons, but falls back to the taxonomy row's own
 * bilingual name for a category/season an admin adds later - which has no
 * pre-existing translation key, only whatever name/name_mk the admin typed
 * into the DB when creating it.
 */
export function translateOrFallback(t: TFunction, key: string, fallback: string): string {
  return t(key, { defaultValue: fallback })
}
