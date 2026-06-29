import api from './index'

export const knowledgeApi = {
  // Add document
  addDocument(data) {
    return api.post('/knowledge/documents', data)
  },
  
  // Batch add documents
  batchAddDocuments(data) {
    return api.post('/knowledge/documents/batch', data)
  },
  
  // Upload file
  uploadFile(file, metadata = {}) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('metadata', JSON.stringify(metadata))
    
    return api.post('/knowledge/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // Delete document
  deleteDocument(id) {
    return api.delete('/knowledge/documents', { params: { id } })
  },
  
  // Get info
  getInfo() {
    return api.get('/knowledge/info')
  }
}
