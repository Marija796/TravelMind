import api from './api'
import type {
  User, LoginPayload, LoginResponse, RegisterPayload, UpdateProfilePayload,
  GoogleAuthPayload, GoogleAuthResponse, PasswordResetPayload, PasswordResetResponse, PasswordResetConfirmPayload,
} from '@/types/user'

export const register = (data: RegisterPayload) =>
  api.post<User>('/users/register/', data).then((r) => r.data)

export const login = (data: LoginPayload) =>
  api.post<LoginResponse>('/users/login/', data).then((r) => r.data)

export const getProfile = () =>
  api.get<User>('/users/profile/').then((r) => r.data)

export const updateProfile = (data: UpdateProfilePayload) =>
  api.patch<User>('/users/profile/', data).then((r) => r.data)

export const updateProfileImage = (file: File) => {
  const formData = new FormData()
  formData.append('profile_image', file)
  // Let axios/the browser set the multipart Content-Type + boundary itself;
  // the api instance's default 'application/json' header must be cleared,
  // not just overridden with a plain 'multipart/form-data' string (which
  // would be sent without a boundary and fail to parse server-side).
  return api
    .patch<User>('/users/profile/', formData, { headers: { 'Content-Type': undefined } })
    .then((r) => r.data)
}

export const googleAuth = (data: GoogleAuthPayload) =>
  api.post<GoogleAuthResponse>('/users/google-auth/', data).then((r) => r.data)

export const requestPasswordReset = (data: PasswordResetPayload) =>
  api.post<PasswordResetResponse>('/users/password-reset/', data).then((r) => r.data)

export const confirmPasswordReset = (data: PasswordResetConfirmPayload) =>
  api.post<{ message: string }>('/users/password-reset-confirm/', data).then((r) => r.data)
