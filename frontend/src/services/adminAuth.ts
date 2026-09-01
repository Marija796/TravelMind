import api from './api'
import type { LoginPayload, LoginResponse } from '@/types/user'

// Separate backend endpoint (see users.admin_serializers.AdminTokenObtainPairSerializer)
// that rejects a non-admin account even with a correct password - not a
// frontend-only check layered on the regular login endpoint.
export const adminLogin = (data: LoginPayload) =>
  api.post<LoginResponse>('/users/admin/login/', data).then((r) => r.data)
