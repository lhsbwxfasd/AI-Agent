import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  
  // 从localStorage恢复用户信息
  const savedUser = localStorage.getItem('user')
  const user = ref(savedUser ? JSON.parse(savedUser) : null)
  
  const isAuthenticated = ref(!!token.value)
  
  const isAdmin = computed(() => {
    return user.value?.is_admin === true
  })
  
  const username = computed(() => {
    return user.value?.username || ''
  })

  async function login(username, password) {
    try {
      const response = await authApi.login({ username, password })
      
      if (response && response.access_token) {
        token.value = response.access_token
        isAuthenticated.value = true
        localStorage.setItem('token', response.access_token)
        
        if (response.user) {
          user.value = response.user
          localStorage.setItem('user', JSON.stringify(response.user))
        }
        
        return true
      }
      
      return false
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  async function getCurrentUser() {
    try {
      const response = await authApi.getCurrentUser()
      user.value = response
      localStorage.setItem('user', JSON.stringify(response))
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
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    username,
    login,
    getCurrentUser,
    logout
  }
})
