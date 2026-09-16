import api from './api'
import type { User } from '../types'

export const authService = {
  register: (payload: { full_name: string; email: string; password: string }) =>
    api.post<User>('/auth/register', payload).then((response) => response.data),
  login: (payload: { email: string; password: string }) =>
    api.post<{ access_token: string; token_type: string }>('/auth/login', payload).then((response) => response.data),
  me: () => api.get<User>('/auth/me').then((response) => response.data),
}
