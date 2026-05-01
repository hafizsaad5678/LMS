/**
 * Shared Utility Functions
 * Common helpers used across multiple services
 * 
 * NOTE: Date formatting functions are in @/utils/formatters.js
 * This file contains API/service-specific utilities
 */

/**
 * Get human-readable time ago string
 * @param {string|Date} dateString - Date to convert
 * @returns {string} - Human readable time ago
 */
export const getTimeAgo = (dateString) => {
    if (!dateString) return 'Recently'

    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now - date) / 1000)

    if (seconds < 60) return 'Just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`
    if (seconds < 2592000) return `${Math.floor(seconds / 604800)} weeks ago`
    return `${Math.floor(seconds / 2592000)} months ago`
}

/**
 * Validate CNIC format (Pakistani National ID)
 * @param {string} cnic - CNIC to validate
 * @returns {boolean} - Is valid
 */
export const validateCNIC = (cnic) => {
    if (!cnic || !cnic.trim()) return true // Empty is valid (optional field)
    const digits = cnic.replace(/[-\s]/g, '')
    return digits.length === 13 && /^\d+$/.test(digits)
}

/**
 * Extract error message from API error response
 * @param {Error} error - Axios error object
 * @param {string} fallback - Fallback message
 * @returns {string} - Error message
 */
export const extractErrorMessage = (error, fallback = 'An error occurred') => {
    if (!error.response?.data) return fallback

    const data = error.response.data

    // Handle different error formats
    if (typeof data === 'string') return data
    if (data.detail) return data.detail
    if (data.error) return data.error
    if (data.message) return data.message

    // Handle field-specific errors
    const fieldErrors = ['cnic', 'email', 'phone', 'full_name']
    for (const field of fieldErrors) {
        if (data[field]) {
            return Array.isArray(data[field]) ? data[field][0] : data[field]
        }
    }

    // Handle errors object
    if (data.errors) {
        return Object.values(data.errors).flat().join(', ')
    }

    return fallback
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} - Debounced function
 */
export const debounce = (func, wait = 300) => {
    let timeout
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout)
            func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
    }
}

/**
 * Normalize API response to array
 * Handles various API response formats consistently
 * @param {any} response - API response (can be array, object with results, or axios response)
 * @returns {Array} - Normalized array
 */
/**
 * Convert JSON object to FormData for multipart/form-data requests
 * @param {Object} obj - Object to convert
 * @returns {FormData} - FormData object
 */
export const toFormData = (obj) => {
    const formData = new FormData()
    Object.keys(obj).forEach(key => {
        const value = obj[key]
        if (value === null || value === undefined) return
        
        if (Array.isArray(value)) {
            value.forEach(item => formData.append(key, item))
        } else if (value instanceof File) {
            formData.append(key, value)
        } else if (typeof value === 'object' && !(value instanceof File)) {
            // Only append if it's not a generic object we should ignore
            // or handle specific sub-objects if needed
            if (value.id) formData.append(key, value.id)
            else formData.append(key, JSON.stringify(value))
        } else if (typeof value === 'boolean') {
            formData.append(key, value ? 'true' : 'false')
        } else {
            formData.append(key, value)
        }
    })
    return formData
}

export const normalizeToArray = (response) => {
    if (Array.isArray(response)) return response
    if (response?.results) return response.results
    if (response?.data?.results) return response.data.results
    if (response?.data && Array.isArray(response.data)) return response.data
    return []
}

export default {
    getTimeAgo,
    validateCNIC,
    extractErrorMessage,
    debounce,
    normalizeToArray,
    toFormData
}
