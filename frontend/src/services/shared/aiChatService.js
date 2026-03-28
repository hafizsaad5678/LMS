import api from './core/api'

export default {
  /**
   * Send a query to the AI Chatbot orchestrator
   * @param {string} query - The user's message
   * @param {string} sessionId - Optional UUID for persistent session
   */
  async sendMessage(message, sessionId = null) {
    const payload = { message }
    if (sessionId) payload.session_id = sessionId
    
    const response = await api.post('/ai/chat/send/', payload)
    return response.data
  },

  /**
   * Fetch all chat sessions for the current user
   */
  async getSessions() {
    const response = await api.get('/ai/chat/sessions/')
    return response.data
  },

  /**
   * Fetch messages for a specific session
   */
  async getSessionMessages(sessionId) {
    const response = await api.get(`/ai/chat/sessions/${sessionId}/`)
    return response.data
  },

  /**
   * Delete a chat session
   */
  async deleteSession(sessionId) {
    const response = await api.delete(`/ai/chat/sessions/${sessionId}/`)
    return response.status
  },

  /**
   * Upload a document for RAG indexing
   */
  async uploadDocument(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/ai/chat/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}
