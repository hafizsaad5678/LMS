import { safeStorage } from '@/utils/security'
import { createRouter, createWebHistory } from 'vue-router'
import { authRoutes } from './routes/auth'
import { adminRoutes } from './routes/admin'
import { teacherRoutes } from './routes/teacher'
import { studentRoutes } from './routes/student'
import { ADMIN_ROUTES, TEACHER_ROUTES, STUDENT_ROUTES } from '@/utils/constants/routes'
import { USER_ROLES } from '@/utils/constants/config'
import { API_BASE_URL } from '@/utils/constants/config'

const routes = [
  ...authRoutes,
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

const AUTH_CHECK_TTL_MS = 10 * 1000
let lastAuthCheckAt = 0
let lastAuthCheckKey = ''

const getAuthProbeUrl = (userRole, userId) => {
  if (userRole === USER_ROLES.ADMIN) {
    return `${API_BASE_URL}/admins/`
  }
  if (userRole === USER_ROLES.TEACHER) {
    return `${API_BASE_URL}/teacher/my-classes/`
  }
  if (userRole === USER_ROLES.STUDENT && userId) {
    return `${API_BASE_URL}/students/${userId}/`
  }
  return null
}

const verifyTokenWithBackend = async (token, userRole) => {
  const userId = safeStorage.get('userId') || safeStorage.get('student_id')
  const probeUrl = getAuthProbeUrl(userRole, userId)

  if (!probeUrl) return false

  const cacheKey = `${token}:${userRole}:${userId || ''}`
  const now = Date.now()
  if (lastAuthCheckKey === cacheKey && (now - lastAuthCheckAt) < AUTH_CHECK_TTL_MS) {
    return true
  }

  try {
    const response = await fetch(probeUrl, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      return false
    }

    lastAuthCheckAt = now
    lastAuthCheckKey = cacheKey
    return true
  } catch {
    return false
  }
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
