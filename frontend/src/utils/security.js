/**
 * Security Utilities
 * Input sanitization and validation helpers
 */

/**
 * Sanitize string input - removes potential XSS vectors
 * @param {string} input - User input to sanitize
 * @returns {string} Sanitized string
 */
export const sanitizeInput = (input) => {
    if (!input || typeof input !== 'string') return ''
    return input
        .replace(/[<>]/g, '') // Remove angle brackets
        .replace(/javascript:/gi, '') // Remove javascript: protocol
        .replace(/on\w+=/gi, '') // Remove event handlers
        .trim()
}

/**
 * Sanitize rich HTML content while preserving safe formatting tags.
 * @param {string} html - HTML content to sanitize
 * @returns {string} Sanitized HTML
 */
export const sanitizeRichHtml = (html) => {
    if (html === null || html === undefined || html === '') return ''

    let clean = String(html)
    clean = clean.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
    clean = clean.replace(/<style[\s\S]*?>[\s\S]*?<\/style>/gi, '')
    clean = clean.replace(/ on\w+="[^"]*"/gi, '')
    clean = clean.replace(/ on\w+='[^']*'/gi, '')
    clean = clean.replace(/javascript:/gi, '')
    clean = clean.replace(/<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi, '')

    return clean
}

/**
 * Sanitize search query
 * @param {string} query - Search query
 * @returns {string} Sanitized query
 */
export const sanitizeSearchQuery = (query) => {
    if (typeof query !== 'string') return ''
    return query
        .replace(/[<>"'`;]/g, '') // Remove dangerous characters
        .substring(0, 100) // Limit length
}

/**
 * Validate UUID format
 * @param {string} id - ID to validate
 * @returns {boolean} Is valid UUID
 */
export const isValidUUID = (id) => {
    if (!id || typeof id !== 'string') return false
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    return uuidRegex.test(id)
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Is valid email
 */
export const isValidEmail = (email) => {
    if (!email || typeof email !== 'string') return false
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
}

/**
 * Safe localStorage operations with validation
 */
export const safeStorage = {
    get: (key) => {
        try {
            return localStorage.getItem(key)
        } catch {
            return null
        }
    },

    set: (key, value) => {
        try {
            if (value !== null && value !== undefined) {
                localStorage.setItem(key, String(value))
            }
        } catch {
            // Storage full or disabled
        }
    },

    remove: (key) => {
        try {
            localStorage.removeItem(key)
        } catch {
            // Ignore errors
        }
    },

    clear: () => {
        try {
            localStorage.clear()
        } catch {
            // Ignore errors
        }
    }
}

/**
 * Validate user ID before storing
 * @param {string} userId - User ID to validate
 * @returns {boolean} Is valid
 */
export const validateUserId = (userId) => {
    if (!userId) return false
    // Accept UUID or numeric ID
    return isValidUUID(userId) || /^\d+$/.test(userId)
}

export default {
    sanitizeInput,
    sanitizeRichHtml,
    sanitizeSearchQuery,
    isValidUUID,
    isValidEmail,
    safeStorage,
    validateUserId
}
