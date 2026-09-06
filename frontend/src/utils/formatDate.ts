/**
 * App-wide date formatting: always dd.mm.yyyy.
 *
 * Deliberately NOT toLocaleDateString(locale) - that renders a different
 * order per language (en-US gives "Sep 4, 2026", mk-MK gives "4.9.2026"),
 * so the same screen showed two different date shapes depending on the
 * active language, and neither was zero-padded. Building the string from
 * the individual date parts keeps one unambiguous format everywhere,
 * independent of locale.
 */

const pad = (value: number) => String(value).padStart(2, '0')

const toDate = (value: string | number | Date) => (value instanceof Date ? value : new Date(value))

/** dd.mm.yyyy - e.g. 04.09.2026 */
export function formatDate(value: string | number | Date): string {
  const date = toDate(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()}`
}

/** dd.mm.yyyy HH:MM - for the places that also showed a time component. */
export function formatDateTime(value: string | number | Date): string {
  const date = toDate(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${formatDate(date)} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
