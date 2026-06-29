import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const isAuthenticated = ref(!!token.value)

  async function login(username, password) {
    try {
      const response = await authApi.login({ username, password })
      token.value = response.access_token
      isAuthenticated.value = true
      localStorage.setItem('token', response.access_token)
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  async function getCurrentUser() {
    try {
      const response = await authApi.getCurrentUser()
      user.value = response
      return response
    } catch (error) {
      console.error('Get current user failed:', error)
      return null
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    getCurrentUser,
    logout
  }
})
