import { defineStore } from 'pinia'
import { authAPI } from '@/services/shared'
import router from '@/router'
import { validateUserId, safeStorage } from '@/utils/security'
import { USER_ROLES } from '@/utils/constants/config'
import { ADMIN_ROUTES, TEACHER_ROUTES, STUDENT_ROUTES } from '@/utils/constants/routes'
import { STORAGE_KEYS, clearAuthData } from '@/utils/constants/storage'

export const useAuth = defineStore('auth', {
  state: () => ({
    access_token: safeStorage.get('access_token'),
    refresh_token: safeStorage.get('refresh_token'),
    userName: safeStorage.get('username'),
    userId: safeStorage.get('userId'),
    userRole: safeStorage.get('userRole'),
    userEmail: safeStorage.get('userEmail'),
    user: null,
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.access_token,
    getUser: (state) => state.user,
    displayName: (state) => {
      const emailFallback = state.userEmail ? state.userEmail.split('@')[0] : null
      const isPlaceholderAdmin = state.userName === 'Admin'
      const preferredName = state.user?.full_name || state.user?.username || emailFallback
      return (!isPlaceholderAdmin && state.userName) || preferredName || 'User'
    }
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authAPI.login(credentials)

        // Store tokens and user info
        this.access_token = response.data.access
        this.refresh_token = response.data.refresh
        const emailValue = response.data.email || credentials.username || null
        const emailPrefix = emailValue && emailValue.includes('@') ? emailValue.split('@')[0] : null
        this.userName = response.data.full_name || response.data.username || credentials.username || emailPrefix || 'User'
        this.user = response.data.user || response.data

        const userRole = response.data.role || 'unknown'
        // Try multiple possible fields for user ID
        const userId = response.data.user_id || response.data.id || response.data.student_id || response.data.teacher_id || response.data.admin_id

        safeStorage.set('access_token', response.data.access)
        safeStorage.set('refresh_token', response.data.refresh)
        safeStorage.set('username', this.userName)
        safeStorage.set('userRole', userRole)
        safeStorage.set('userEmail', emailValue)

        // Validate and store user ID
        if (userId && validateUserId(String(userId))) {
          safeStorage.set('userId', userId)
          this.userId = userId
        }

        // Update state
        this.userRole = userRole
        this.userEmail = emailValue

        // Update axios default headers with new token
        const api = (await import('@/services/shared')).default
        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`

        // Determine redirect path using route constants
        const dashboardPaths = {
          [USER_ROLES.ADMIN]: ADMIN_ROUTES.DASHBOARD.path,
          [USER_ROLES.TEACHER]: TEACHER_ROUTES.DASHBOARD.path,
          [USER_ROLES.STUDENT]: STUDENT_ROUTES.DASHBOARD.path,
        }
        const redirectPath = dashboardPaths[userRole] || '/'

        // Try to hydrate a role-specific display name from profile records.
        this.hydrateDisplayName(userRole, userId).catch(() => {
          // Keep login resilient even if profile fetch fails.
        })

        // Preload dashboard stats in background (don't wait for it)
        this.preloadDashboardStats(userRole, userId).catch(err => {
          console.warn('Failed to preload dashboard stats:', err)
        })

        // Use router.push instead of window.location.href
        // Add a small delay to ensure token is set before navigation
        await new Promise(resolve => setTimeout(resolve, 50))
        router.push(redirectPath)

        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Login failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async hydrateDisplayName(userRole = this.userRole, userId = this.userId) {
      if (userRole === USER_ROLES.ADMIN) {
        const emailFallback = this.userEmail && this.userEmail.includes('@') ? this.userEmail.split('@')[0] : this.userEmail
        const preferredName = this.user?.full_name || this.user?.username || emailFallback
        const adminName = this.userName && this.userName !== 'Admin' ? this.userName : preferredName
        if (adminName) {
          this.userName = adminName
          safeStorage.set(STORAGE_KEYS.USERNAME, adminName)
        }
        return this.userName
      }

      if (!userRole || !userId) return this.userName

      try {
        let profile = null
        if (userRole === USER_ROLES.TEACHER) {
          const { teacherService } = await import('@/services/shared')
          profile = await teacherService.getTeacher(userId)
        } else if (userRole === USER_ROLES.STUDENT) {
          const { studentService } = await import('@/services/shared')
          profile = await studentService.getStudent(userId)
        }

        const resolvedName = profile?.full_name || profile?.name || this.userName
        if (resolvedName) {
          this.userName = resolvedName
          safeStorage.set(STORAGE_KEYS.USERNAME, resolvedName)
        }
        return this.userName
      } catch {
        return this.userName
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
      this.userId = null
      this.userRole = null
      this.userEmail = null
      this.user = null
      clearAuthData()
      router.push({ name: 'Login' })
    },

    /**
     * Preload dashboard stats after login for instant dashboard load
     */
    async preloadDashboardStats(userRole, userId) {
      try {
        if (userRole === USER_ROLES.ADMIN) {
          const { default: adminPanelService } = await import('@/services/admin/adminPanelService')
          await adminPanelService.getDashboardStats()
        } else if (userRole === USER_ROLES.TEACHER) {
          const { default: teacherPanelService } = await import('@/services/teacher/teacherPanelService')
          await teacherPanelService.getDashboardStats()
        } else if (userRole === USER_ROLES.STUDENT && userId) {
          const { default: studentPanelService } = await import('@/services/student/studentPanelService')
          await studentPanelService.getDashboardStats(userId)
        }
      } catch {
        // Silently fail - dashboard will load normally if preload fails
      }
    }
  }
})

