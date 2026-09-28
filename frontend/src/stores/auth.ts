import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/api/client'
import type { UserCreate, UserResponse, TokenResponse } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserResponse | null>(null)
  const isAuthenticated = ref(false)

  async function register(payload: UserCreate) {
    await apiClient.post<UserResponse>('/api/auth/register', payload)
    // после регистрации сразу логинимся
    await login(payload.username, payload.password)
  }

  async function login(username: string, password: string) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  const { data } = await apiClient.post<TokenResponse>(
    '/api/auth/token',
    formData,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  )

  localStorage.setItem('access_token', data.access_token)
  isAuthenticated.value = true
  await fetchUser()
}

  async function fetchUser() {
    try {
      const { data } = await apiClient.get<UserResponse>('/api/auth/me')
      user.value = data
      isAuthenticated.value = true
    } catch {
      isAuthenticated.value = false
      user.value = null
    }
  }

  async function logout() {
  try {
    await apiClient.post('/api/auth/logout')  // бэк удалит куку
  } catch {
  }
  localStorage.removeItem('access_token')
  isAuthenticated.value = false
  user.value = null
}

  return { user, isAuthenticated, register, login, fetchUser, logout }
})