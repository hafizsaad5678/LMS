import axios from 'axios'
import router from '@/router'
import { getErrorMessage } from '@/utils/errorMap'
import { API_BASE_URL } from '@/utils/constants/config'
import { STORAGE_KEYS } from '@/utils/constants/storage'
import { safeStorage } from '@/utils/security'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = safeStorage.get(STORAGE_KEYS.ACCESS_TOKEN)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // Let the browser automatically set the correct Content-Type boundary for FormData
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  
  return config
}, (error) => {
  return Promise.reject(error)
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Response interceptor for handling 401 / token refresh and automatic error handling
api.interceptors.response.use(
  (response) => {
    // Automatically extract data from response for cleaner service code
    // Services can now just return api.get() instead of api.get().then(res => res.data)
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // If the error is 401 and not a retry, attempt to refresh token
    const isLoginRequest = originalRequest.url.includes('/login/')
    const isRefreshRequest = originalRequest.url.includes('/token/refresh/')

    if (error.response?.status === 401 && !originalRequest._retry && !isLoginRequest && !isRefreshRequest) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = safeStorage.get(STORAGE_KEYS.REFRESH_TOKEN)
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/token/refresh/`, { refresh: refreshToken })
          const newAccessToken = res.data.access

          safeStorage.set(STORAGE_KEYS.ACCESS_TOKEN, newAccessToken)
          api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`

          processQueue(null, newAccessToken)

          // Retry with new token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return api(originalRequest)
        } catch (err) {
          processQueue(err, null)
          safeStorage.clear()
          // Use location.href for a clean redirect if router is in a weird state
          window.location.href = '/login'
          return Promise.reject(err)
        } finally {
          isRefreshing = false
        }
      } else {
        safeStorage.clear()
        window.location.href = '/login'
      }
    }

    // Enhance error object with user-friendly message
    if (error.response) {
      error.userMessage = getErrorMessage(error)
    } else if (error.request) {
      error.userMessage = 'Network error. Please check your connection.'
    } else {
      error.userMessage = 'An unexpected error occurred.'
    }

    return Promise.reject(error)
  }
)

/**
 * Wrapper for API calls with automatic error handling
 * Use this for cleaner service code without repetitive try-catch
 */
export const apiCall = async (apiFunction, entity = null, action = null) => {
  try {
    const response = await apiFunction()
    return { success: true, data: response.data, response }
  } catch (error) {
    console.error(`API Error [${entity}/${action}]:`, error)
    return {
      success: false,
      error,
      message: error.userMessage || getErrorMessage(error, entity, action)
    }
  }
}

export const authAPI = {
  login: (credentials) => api.post('/login/', credentials),
  forgotPassword: (email) => api.post('/forgot-password/', email),
  resetPassword: (uidb64, token, passwordData) => api.post(`/reset-password/${uidb64}/${token}/`, passwordData),
  verifyEmail: (uidb64, token) => api.get(`/verify/${uidb64}/${token}/`)
}

export default api
