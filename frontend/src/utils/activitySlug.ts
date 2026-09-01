/**
 * Converts a stored activity value (e.g. 'Food & Dining') into a stable
 * camelCase i18n key segment (e.g. 'foodDining') for activity.<key> lookups.
 * The stored/API value itself stays the plain English string - only the
 * displayed label goes through translation - so existing user data and the
 * backend's PREFERENCE_ACTIVITY_OPTIONS list never need to change.
 */
export function activitySlug(activity: string): string {
  return activity
    .replace(/&/g, '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((word, i) => (i === 0 ? word.toLowerCase() : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()))
    .join('')
}
