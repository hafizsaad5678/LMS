import { safeStorage } from '@/utils/security'
import { createRouter, createWebHistory } from 'vue-router'
import { authRoutes } from './routes/auth'
import { adminRoutes } from './routes/admin'
import { teacherRoutes } from './routes/teacher'
import { studentRoutes } from './routes/student'
import { ADMIN_ROUTES, TEACHER_ROUTES, STUDENT_ROUTES } from '@/utils/constants/routes'
import { USER_ROLES } from '@/utils/constants/config'

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

// Auth guard with role-based protection
router.beforeEach((to, from, next) => {
  const token = safeStorage.get('access_token')
  const userRole = safeStorage.get('userRole')

  const dashboardPaths = {
    [USER_ROLES.ADMIN]: ADMIN_ROUTES.DASHBOARD.path,
    [USER_ROLES.TEACHER]: TEACHER_ROUTES.DASHBOARD.path,
    [USER_ROLES.STUDENT]: STUDENT_ROUTES.DASHBOARD.path,
  }

  // Guest-only pages
  if (to.meta.requiresGuest && token) {
    return next(dashboardPaths[userRole] || '/')
  }

  // Protected pages
  if (to.meta.requiresAuth && !token) {
    return next({ name: 'Login' })
  }

  // Role-based protection
  if (token && userRole) {
    const path = to.path
    if (userRole === USER_ROLES.STUDENT && (path.startsWith(ADMIN_ROUTES.DASHBOARD.path) || path.startsWith(TEACHER_ROUTES.DASHBOARD.path))) {
      return next(STUDENT_ROUTES.DASHBOARD.path)
    }
    if (userRole === USER_ROLES.TEACHER && path.startsWith(ADMIN_ROUTES.DASHBOARD.path)) {
      return next(TEACHER_ROUTES.DASHBOARD.path)
    }
  }

  next()
})

export default router
