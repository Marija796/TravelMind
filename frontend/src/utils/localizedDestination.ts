interface NamedMk {
  name: string
  name_mk?: string
}

interface DescribedMk {
  description: string
  description_mk?: string
}

interface CountriedMk {
  country: string
  country_mk?: string
}

// Every destination has a bilingual name/name_mk, description/description_mk,
// and country/country_mk pair (populated for all 100 seeded destinations) -
// these pick the field matching the active UI language, falling back to
// English when a Macedonian value is missing (e.g. on a destination an admin
// just created without filling in the Macedonian field yet).
export function localizedName(destination: NamedMk, language: string): string {
  return language === 'mk' && destination.name_mk ? destination.name_mk : destination.name
}

export function localizedDescription(destination: DescribedMk, language: string): string {
  return language === 'mk' && destination.description_mk ? destination.description_mk : destination.description
}

export function localizedCountry(destination: CountriedMk, language: string): string {
  return language === 'mk' && destination.country_mk ? destination.country_mk : destination.country
}
