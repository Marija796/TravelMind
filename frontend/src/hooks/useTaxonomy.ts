import { useEffect, useState } from 'react'
import { getTravelCategories, getSeasons } from '@/services/taxonomy'
import type { TravelCategoryDTO, SeasonDTO } from '@/types/taxonomy'

// Module-level cache + in-flight promise so every component using these
// hooks on the same page load shares one network request instead of each
// FilterPanel/Profile/Recommendations instance firing its own.
let categoriesCache: TravelCategoryDTO[] | null = null
let categoriesPromise: Promise<TravelCategoryDTO[]> | null = null
let seasonsCache: SeasonDTO[] | null = null
let seasonsPromise: Promise<SeasonDTO[]> | null = null

export function useTravelCategories() {
  const [categories, setCategories] = useState<TravelCategoryDTO[]>(categoriesCache ?? [])
  const [isLoading, setIsLoading] = useState(categoriesCache === null)

  useEffect(() => {
    if (categoriesCache) {
      setCategories(categoriesCache)
      setIsLoading(false)
      return
    }
    if (!categoriesPromise) {
      categoriesPromise = getTravelCategories().then((data) => {
        categoriesCache = data
        return data
      })
    }
    categoriesPromise.then((data) => {
      setCategories(data)
      setIsLoading(false)
    })
  }, [])

  return { categories, isLoading }
}

export function useSeasons() {
  const [seasons, setSeasons] = useState<SeasonDTO[]>(seasonsCache ?? [])
  const [isLoading, setIsLoading] = useState(seasonsCache === null)

  useEffect(() => {
    if (seasonsCache) {
      setSeasons(seasonsCache)
      setIsLoading(false)
      return
    }
    if (!seasonsPromise) {
      seasonsPromise = getSeasons().then((data) => {
        seasonsCache = data
        return data
      })
    }
    seasonsPromise.then((data) => {
      setSeasons(data)
      setIsLoading(false)
    })
  }, [])

  return { seasons, isLoading }
}

// Called after any admin create/update/delete on categories or seasons, so
// components already mounted elsewhere in the same SPA session (FilterPanel,
// Profile, Recommendations) refetch instead of serving a stale cached list
// until the next full page reload.
export function invalidateTaxonomyCache() {
  categoriesCache = null
  categoriesPromise = null
  seasonsCache = null
  seasonsPromise = null
}
