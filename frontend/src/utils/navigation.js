/**
 * Navigation Utilities
 * Centralized navigation helpers using named routes for type safety
 */

import { ADMIN_ROUTES, TEACHER_ROUTES, STUDENT_ROUTES } from './constants/routes'

/**
 * Navigate to a named route
 * @param {Object} router - Vue Router instance
 * @param {string} name - Route name
 * @param {Object} params - Route params
 * @param {Object} query - Query parameters
 */
export const navigateTo = (router, name, params = {}, query = {}) => {
    router.push({ name, params, query })
}

/**
 * Navigate to login page
 */
export const navigateToLogin = (router) => {
    router.push({ name: 'Login' })
}

/**
 * Navigate to signup page
 */
export const navigateToSignup = (router) => {
    router.push({ name: 'Signup' })
}

/**
 * Navigate to home page
 */
export const navigateToHome = (router) => {
    router.push({ name: 'Home' })
}

/**
 * Navigate to appropriate dashboard based on user role
 * @param {Object} router - Vue Router instance
 * @param {string} role - User role ('admin', 'teacher', 'student')
 */
export const navigateToDashboard = (router, role) => {
    const dashboards = {
        admin: 'AdminDashboard',
        teacher: 'TeacherDashboard',
        student: 'StudentDashboard'
    }

    const routeName = dashboards[role]
    if (routeName) {
        router.push({ name: routeName })
    } else {
        navigateToHome(router)
    }
}

/**
 * Navigate back or to fallback route
 * @param {Object} router - Vue Router instance
 * @param {string} fallbackName - Fallback route name
 */
export const navigateBack = (router, fallbackName = 'Home') => {
    if (window.history.length > 1) {
        router.back()
    } else {
        router.push({ name: fallbackName })
    }
}

/**
 * Replace current route (no history entry)
 * @param {Object} router - Vue Router instance
 * @param {string} name - Route name
 * @param {Object} params - Route params
 */
export const replaceRoute = (router, name, params = {}) => {
    router.replace({ name, params })
}

/**
 * Check if current route matches name
 * @param {Object} route - Current route object
 * @param {string} name - Route name to check
 * @returns {boolean}
 */
export const isCurrentRoute = (route, name) => {
    return route.name === name
}

/**
 * Get route path by name (useful for external links)
 * @param {Object} router - Vue Router instance
 * @param {string} name - Route name
 * @param {Object} params - Route params
 * @returns {string} Route path
 */
export const getRoutePath = (router, name, params = {}) => {
    const route = router.resolve({ name, params })
    return route.href
}

export default {
    navigateTo,
    navigateToLogin,
    navigateToSignup,
    navigateToHome,
    navigateToDashboard,
    navigateBack,
    replaceRoute,
    isCurrentRoute,
    getRoutePath
}
/**
 * Generate breadcrumbs array for the application
 * @param {string} role - The user role (admin, teacher, student)
 * @param {string} currentLabel - The label for the current page
 * @param {string} parentRoute - The parent route name to link back to (optional)
 * @returns {Array} Array of breadcrumb objects
 */
export const generateBreadcrumbs = (role, currentLabel, parentRoute = null) => {
    const roleCapitalized = role ? role.charAt(0).toUpperCase() + role.slice(1) : 'Admin'
    const dashboardRoute = role ? `${roleCapitalized}Dashboard` : 'AdminDashboard'

    const breadcrumbs = [
        { name: 'Dashboard', disabled: false, href: { name: dashboardRoute } }
    ]

    if (parentRoute) {
        breadcrumbs.push({ name: parentRoute, disabled: false, href: { name: parentRoute } })
    }

    breadcrumbs.push({ name: currentLabel, disabled: true, href: '' })
    return breadcrumbs
}
