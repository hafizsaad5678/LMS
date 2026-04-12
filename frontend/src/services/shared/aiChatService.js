import api from './core/api'
import { API_BASE_URL } from '@/utils/constants/config'
import { STORAGE_KEYS } from '@/utils/constants/storage'
import { safeStorage } from '@/utils/security'


const buildApiUrl = (path) => {
  const cleanBase = String(API_BASE_URL || '').replace(/\/$/, '')
  const cleanPath = String(path || '').replace(/^\//, '')
  return `${cleanBase}/${cleanPath}`
}


const parseSsePayload = (eventBlock) => {
  const lines = eventBlock.split('\n')
  const dataLines = []
  for (const line of lines) {
    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim())
    }
  }

  if (dataLines.length === 0) return null

  const payloadText = dataLines.join('\n')
  if (!payloadText) return null

  try {
    return JSON.parse(payloadText)
  } catch {
    return null
  }
}


const refreshAccessToken = async () => {
  const refreshToken = safeStorage.get(STORAGE_KEYS.REFRESH_TOKEN)
  if (!refreshToken) return null

  const response = await fetch(buildApiUrl('/token/refresh/'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken }),
  })

  if (!response.ok) return null

  const data = await response.json().catch(() => null)
  const newAccessToken = data?.access
  if (!newAccessToken) return null

  safeStorage.set(STORAGE_KEYS.ACCESS_TOKEN, newAccessToken)
  return newAccessToken
}

export default {
  /**
   * Send a query to the AI Chatbot orchestrator
   * @param {string} query - The user's message
   * @param {string} sessionId - Optional UUID for persistent session
   */
  async sendMessage(message, sessionId = null, requestConfig = {}) {
    const payload = { message }
    if (sessionId) payload.session_id = sessionId

    const response = await api.post('/ai/chat/send/', payload, requestConfig)
    return response.data
  },

  /**
   * Send a query and stream assistant chunks via SSE.
   */
  async sendMessageStream(message, sessionId = null, options = {}) {
    const payload = { message, stream: true }
    if (sessionId) payload.session_id = sessionId

    const sendStreamRequest = async (token) => {
      return fetch(buildApiUrl('/ai/chat/send/?stream=1'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
        signal: options.signal,
      })
    }

    let token = safeStorage.get(STORAGE_KEYS.ACCESS_TOKEN)
    let response = await sendStreamRequest(token)
    if (response.status === 401) {
      const refreshedToken = await refreshAccessToken()
      if (refreshedToken) {
        token = refreshedToken
        response = await sendStreamRequest(token)
      }
    }

    if (!response.ok) {
      const errText = await response.text()
      throw new Error(errText || `Streaming request failed (${response.status})`)
    }

    const contentType = String(response.headers.get('content-type') || '').toLowerCase()
    if (contentType.includes('application/json')) {
      const payload = await response.json().catch(() => null)
      const content = payload?.message?.content || ''
      if (content) {
        options.onChunk?.(content, payload)
      }
      const donePayload = {
        done: true,
        session_id: payload?.session_id || null,
        message: payload?.message || null,
      }
      options.onDone?.(donePayload)
      return donePayload
    }

    if (!response.body) {
      throw new Error('Streaming response body not available')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let donePayload = null

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''

      for (const eventBlock of events) {
        const payloadObj = parseSsePayload(eventBlock)
        if (!payloadObj) continue

        if (payloadObj.error) {
          throw new Error(payloadObj.details || payloadObj.error)
        }

        if (payloadObj.chunk) {
          options.onChunk?.(payloadObj.chunk, payloadObj)
        }

        if (payloadObj.done) {
          donePayload = payloadObj
          options.onDone?.(payloadObj)
        }
      }
    }

    if (!donePayload) {
      const lastPayload = parseSsePayload(buffer)
      if (lastPayload?.done) {
        donePayload = lastPayload
        options.onDone?.(lastPayload)
      }
    }

    return donePayload
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
   * Rename a chat session title
   */
  async renameSession(sessionId, title) {
    const response = await api.patch(`/ai/chat/sessions/${sessionId}/`, { title })
    return response.data
  },

  /**
   * Upload a document for RAG indexing
   */
  async uploadDocument(file, sessionId = null) {
    const formData = new FormData()
    formData.append('file', file)
    if (sessionId) formData.append('session_id', sessionId)
    const response = await api.post('/ai/chat/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Fetch async document indexing status
   */
  async getUploadStatus(fileId) {
    const response = await api.get(`/ai/chat/upload/${fileId}/status/`)
    return response.data
  }
}
