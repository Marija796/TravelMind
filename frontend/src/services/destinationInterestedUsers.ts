import api from './api'
import type { DestinationInterestedUsersResponse } from '@/types/user'

export const getDestinationInterestedUsers = (destinationId: number) =>
  api.get<DestinationInterestedUsersResponse>(`/users/destinations/${destinationId}/interested/`).then((r) => r.data)
