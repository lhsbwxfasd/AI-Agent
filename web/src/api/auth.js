import api from './index'

export const authApi = {
  // Login
  login(data) {
    return api.post('/users/login', data)
  },
  
  // Register
  register(data) {
    return api.post('/users/register', data)
  },
  
  // Get current user
  getCurrentUser() {
    return api.get('/users/me')
  },
  
  // Update current user
  updateCurrentUser(data) {
    return api.put('/users/me', data)
  }
}
