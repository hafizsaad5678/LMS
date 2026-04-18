/**
 * Application Configuration Constants
 * Centralized configuration values
 */

// ── Backend / API URLs ──────────────────────────────────────────────
// Single source of truth – every file must import from here instead of
// hard-coding "http://127.0.0.1:8000" or similar strings.
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
export const BACKEND_BASE_URL = API_BASE_URL.replace(/\/api\/?$/, '')  // strips trailing /api

/**
 * Build an absolute file / media URL from a relative backend path.
 * If the URL is already absolute it is returned as-is.
 * @param {string} url - relative or absolute URL
 * @returns {string|null}
 */
export const getFileUrl = (url) => {
    if (!url) return null
    if (url.startsWith('http')) return url
    return `${BACKEND_BASE_URL}${url.startsWith('/') ? '' : '/'}${url}`
}

// ── User Roles ──────────────────────────────────────────────────────
export const USER_ROLES = Object.freeze({
    ADMIN: 'admin',
    TEACHER: 'teacher',
    STUDENT: 'student',
})

// Feature flags (set to true when enabling hidden/disabled capabilities)
export const FEATURE_FLAGS = Object.freeze({
    ADMIN_ASSIGNMENT_MANAGEMENT: false
})

// Currency
export const CURRENCY = 'PKR'
export const CURRENCY_LOCALE = 'en-PK'

// Cache
export const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

// Countries list
export const COUNTRIES = [
    'Pakistan',
    'India',
    'Bangladesh',
    'United States',
    'United Kingdom',
    'Canada',
    'Australia',
    'Saudi Arabia',
    'UAE',
    'Other'
]

// Gender options
export const GENDER_OPTIONS = [
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' },
    { value: 'other', label: 'Other' }
]

// Status options
export const STATUS_OPTIONS = [
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' }
]

// Semester status
export const SEMESTER_STATUS_OPTIONS = [
    { value: 'draft', label: 'Draft' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'archived', label: 'Archived' }
]

// Period durations
export const PERIOD_DURATIONS = [
    { value: 30, label: '30 minutes' },
    { value: 45, label: '45 minutes' },
    { value: 50, label: '50 minutes' },
    { value: 60, label: '60 minutes' }
]

// Days of week
export const DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
export const DAY_LABELS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

// Format currency helper
export const formatCurrencyValue = (amount) => {
    if (amount === null || amount === undefined) return `${CURRENCY} 0`
    return `${CURRENCY} ${Number(amount).toLocaleString()}`
}

export default {
    API_BASE_URL,
    BACKEND_BASE_URL,
    getFileUrl,
    USER_ROLES,
    FEATURE_FLAGS,
    CURRENCY,
    CURRENCY_LOCALE,
    CACHE_DURATION,
    COUNTRIES,
    GENDER_OPTIONS,
    STATUS_OPTIONS,
    SEMESTER_STATUS_OPTIONS,
    PERIOD_DURATIONS,
    DAYS_OF_WEEK,
    DAY_LABELS,
    formatCurrencyValue
}
