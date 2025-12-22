import { defineStore } from 'pinia'
import { authAPI } from '@/services/api'
import router from '@/router'

export const useAuth = defineStore('auth', {
  state: () => ({
    access_token: localStorage.getItem('access_token') || null,
    refresh_token: localStorage.getItem('refresh_token') || null,
    userName: localStorage.getItem('username') || null,
    user: null,
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.access_token,
    getUser: (state) => state.user
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authAPI.login(credentials)

        // Store tokens
        this.access_token = response.data.access
        this.refresh_token = response.data.refresh
        this.userName = response.data.username || response.data.full_name || 'Admin'

        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        localStorage.setItem('username', this.userName)

        // Redirect to dashboard
        router.push('/admin-dashboard')

        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Login failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async signup(userData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authAPI.signup(userData)
        router.push({ name: 'Login', query: { msg: 'Check your email to verify account' } })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Signup failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async forgotPassword(email) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authAPI.forgotPassword({ email })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Request failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async resetPassword(uidb64, token, passwordData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authAPI.resetPassword(uidb64, token, passwordData)
        router.push({ name: 'Login', query: { msg: 'Password reset successful' } })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Reset failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    logout() {
      this.access_token = null
      this.refresh_token = null
      this.userName = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('username')
      localStorage.removeItem('userRole')
      router.push('/login')
    }
  }
})
