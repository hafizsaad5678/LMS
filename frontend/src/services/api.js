import axios from 'axios'
import router from '@/router'

const API_BASE_URL = 'http://127.0.0.1:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for handling 401 / token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Only retry once
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          // Call backend to refresh access token
          const res = await api.post('/token/refresh/', { refresh: refreshToken })
          localStorage.setItem('access_token', res.data.access)

          // Retry the original request with new access token
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`
          return api(originalRequest)
        } catch (err) {
          // Refresh token expired or invalid → logout
          localStorage.clear()
          router.push('/login')
          return Promise.reject(err)
        }
      } else {
        // No refresh token → logout
        localStorage.clear()
        router.push('/login')
      }
    }

    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (credentials) => api.post('/login/', credentials),
  signup: (userData) => api.post('/signup/', userData),
  forgotPassword: (email) => api.post('/forgot-password/', email),
  resetPassword: (uidb64, token, passwordData) => api.post(`/reset-password/${uidb64}/${token}/`, passwordData),
  verifyEmail: (uidb64, token) => api.get(`/verify/${uidb64}/${token}/`)
}

export default api