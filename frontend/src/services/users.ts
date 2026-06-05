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

export const googleAuth = (data: GoogleAuthPayload) =>
  api.post<GoogleAuthResponse>('/users/google-auth/', data).then((r) => r.data)

export const requestPasswordReset = (data: PasswordResetPayload) =>
  api.post<PasswordResetResponse>('/users/password-reset/', data).then((r) => r.data)

export const confirmPasswordReset = (data: PasswordResetConfirmPayload) =>
  api.post<{ message: string }>('/users/password-reset-confirm/', data).then((r) => r.data)
