import { safeStorage } from '@/utils/security'
import { createRouter, createWebHistory } from 'vue-router'
import { authRoutes } from './routes/auth'
import { adminRoutes } from './routes/admin'
import { teacherRoutes } from './routes/teacher'
import { studentRoutes } from './routes/student'
import { publicRoutes } from './routes/public'
import { ADMIN_ROUTES, TEACHER_ROUTES, STUDENT_ROUTES } from '@/utils/constants/routes'
import { USER_ROLES, API_BASE_URL } from '@/utils/constants/config'

const routes = [
  ...authRoutes,
  ...publicRoutes,
  adminRoutes,
  teacherRoutes,
  studentRoutes,

  // 404 Not Found - catch all route
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/shared/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  }
})

const AUTH_CHECK_TTL_MS = 60 * 1000
let lastAuthCheckAt = 0
let lastAuthCheckKey = ''
let pendingAuthCheck = null
let pendingAuthCheckKey = ''

const getAuthProbeUrl = (userRole, userId) => {
  if (userRole === USER_ROLES.ADMIN) {
    return userId ? `${API_BASE_URL}/admins/${userId}/` : `${API_BASE_URL}/admins/?page=1`
  }
  if (userRole === USER_ROLES.TEACHER) {
    return userId ? `${API_BASE_URL}/teachers/${userId}/` : `${API_BASE_URL}/teacher/my-classes/`
  }
  if (userRole === USER_ROLES.STUDENT && userId) {
    return `${API_BASE_URL}/students/${userId}/`
  }
  return null
}

const verifyTokenWithBackend = async (token, userRole) => {
  const userId = safeStorage.get('userId') || safeStorage.get('student_id')
  const probeUrl = getAuthProbeUrl(userRole, userId)

  // Missing probe target should not hard-logout users during client reload/hydration.
  if (!probeUrl) return true

  const cacheKey = `${token}:${userRole}:${userId || ''}`
  const now = Date.now()
  if (lastAuthCheckKey === cacheKey && (now - lastAuthCheckAt) < AUTH_CHECK_TTL_MS) {
    return true
  }

  if (pendingAuthCheck && pendingAuthCheckKey === cacheKey) {
    return pendingAuthCheck
  }

  pendingAuthCheckKey = cacheKey
  pendingAuthCheck = (async () => {
    try {
      let response = await fetch(probeUrl, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      // If token is expired (401), try to refresh it before giving up
      if (response.status === 401) {
        const refreshToken = safeStorage.get('refresh_token')
        if (refreshToken) {
          try {
            const refreshResponse = await fetch(`${API_BASE_URL}/token/refresh/`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ refresh: refreshToken }),
            })

            if (refreshResponse.ok) {
              const refreshData = await refreshResponse.json()
              const newAccessToken = refreshData.access

              if (newAccessToken) {
                // Save new token so Axios and future page requests pick it up
                safeStorage.set('access_token', newAccessToken)

                // Retry probe request with the newly acquired token
                response = await fetch(probeUrl, {
                  method: 'GET',
                  headers: {
                    Authorization: `Bearer ${newAccessToken}`,
                  },
                })
              }
            }
          } catch (refreshErr) {
            console.error('Token refresh failed in router guard:', refreshErr)
          }
        }
      }

      // Only explicit auth failures should invalidate the session.
      if (response.status === 401 || response.status === 403) {
        return false
      }

      // For transient server/network states (5xx, startup lag), keep the session.
      if (!response.ok) {
        return true
      }

      // Update auth check cache with the current token
      const currentToken = safeStorage.get('access_token') || token
      lastAuthCheckAt = Date.now()
      lastAuthCheckKey = `${currentToken}:${userRole}:${userId || ''}`
      return true
    } catch {
      // Dev reloads or temporary network issues should not force logout.
      return true
    } finally {
      pendingAuthCheck = null
      pendingAuthCheckKey = ''
    }
  })()

  return pendingAuthCheck
}

// Auth guard with role-based protection
router.beforeEach(async (to, from, next) => {
  const token = safeStorage.get('access_token')
  const userRole = safeStorage.get('userRole')

  const requiresGuest = to.matched.some(record => record.meta?.requiresGuest)
  const requiresAuth = to.matched.some(record => record.meta?.requiresAuth)
  const requiredRole = to.matched.map(record => record.meta?.role).find(Boolean)

  const dashboardPaths = {
    [USER_ROLES.ADMIN]: ADMIN_ROUTES.DASHBOARD.path,
    [USER_ROLES.TEACHER]: TEACHER_ROUTES.DASHBOARD.path,
    [USER_ROLES.STUDENT]: STUDENT_ROUTES.DASHBOARD.path,
  }

  // Guest-only pages
  if (requiresGuest && token) {
    return next(dashboardPaths[userRole] || '/')
  }

  // Protected pages
  if (requiresAuth && !token) {
    return next({ name: 'Login' })
  }

  // Role-based protection using route metadata
  if (requiresAuth && token) {
    if (!userRole) {
      safeStorage.clear()
      return next({ name: 'Login' })
    }

    const isVerified = await verifyTokenWithBackend(token, userRole)
    if (!isVerified) {
      safeStorage.clear()
      return next({ name: 'Login' })
    }

    if (requiredRole && userRole !== requiredRole) {
      return next(dashboardPaths[userRole] || '/')
    }
  }

  next()
})

export default router
