import api from './index'

export const conversationApi = {
  // Create conversation
  create(data) {
    return api.post('/conversations/', data)
  },
  
  // List conversations
  list(params = {}) {
    return api.get('/conversations/', { params })
  },
  
  // Get conversation
  get(id) {
    return api.get(`/conversations/${id}`)
  },
  
  // Update conversation
  update(id, data) {
    return api.put(`/conversations/${id}`, data)
  },
  
  // Delete conversation
  delete(id) {
    return api.delete(`/conversations/${id}`)
  },
  
  // Get conversation messages
  getMessages(id, params = {}) {
    return api.get(`/conversations/${id}/messages`, { params })
  }
}
