import api from './api'
import type { TravelCategoryDTO, SeasonDTO } from '@/types/taxonomy'

export const getTravelCategories = () =>
  api.get<TravelCategoryDTO[]>('/destinations/categories/').then((r) => r.data)

export const getSeasons = () =>
  api.get<SeasonDTO[]>('/destinations/seasons/').then((r) => r.data)
