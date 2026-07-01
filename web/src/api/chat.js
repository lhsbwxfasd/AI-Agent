import api from './index'
import { useAuthStore } from '@/stores/auth'

export const chatApi = {
  // Get available models
  getModels() {
    return api.get('/chat/models')
  },
  
  // Chat completion (non-streaming)
  chat(data) {
    return api.post('/chat/completions', data)
  },
  
  // Chat completion (streaming)
  async chatStream(data, onMessage, onError, onComplete) {
    const authStore = useAuthStore()
    const headers = {
      'Content-Type': 'application/json'
    }
    if (authStore.token) {
      headers.Authorization = `Bearer ${authStore.token}`
    }
    
    try {
      const response = await fetch('/api/v1/chat/completions/stream', {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              onMessage(data)
              
              if (data.type === 'end') {
                onComplete(data)
                return
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      onError(error)
    }
  },
  
  // Upload attachment
  async uploadAttachment(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const authStore = useAuthStore()
    const headers = {}
    if (authStore.token) {
      headers.Authorization = `Bearer ${authStore.token}`
    }
    
    const response = await fetch('/api/v1/attachments/upload', {
      method: 'POST',
      headers,
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Upload failed')
    }
    
    return response.json()
  }
}
