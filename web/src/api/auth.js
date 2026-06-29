import api from './index'

export const authApi = {
  // Login
  login(data) {
    return api.post('/auth/login', data)
  },
  
  // Get current user
  getCurrentUser() {
    return api.get('/auth/me')
  }
}
