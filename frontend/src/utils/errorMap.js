/**
 * Centralized Error Mapping Utility
 * Standardizes API error messages for consistent user experience
 */

/**
 * Common error messages mapped by HTTP status codes
 */
const STATUS_MESSAGES = {
    400: 'Invalid request. Please check your input.',
    401: 'Authentication required. Please log in.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    409: 'This action conflicts with existing data.',
    422: 'Validation failed. Please check your input.',
    429: 'Too many requests. Please try again later.',
    500: 'Server error. Please try again later.',
    502: 'Service temporarily unavailable.',
    503: 'Service temporarily unavailable.',
    504: 'Request timeout. Please try again.'
}

/**
 * Entity-specific error messages
 */
const ENTITY_ERRORS = {
    student: {
        create: 'Failed to add student',
        update: 'Failed to update student',
        delete: 'Failed to delete student',
        fetch: 'Failed to load student data',
        duplicate: 'A student with this enrollment number already exists'
    },
    teacher: {
        create: 'Failed to add teacher',
        update: 'Failed to update teacher',
        delete: 'Failed to delete teacher',
        fetch: 'Failed to load teacher data',
        duplicate: 'A teacher with this employee ID already exists'
    },
    subject: {
        create: 'Failed to add subject',
        update: 'Failed to update subject',
        delete: 'Failed to delete subject',
        fetch: 'Failed to load subject data',
        duplicate: 'A subject with this code already exists'
    },
    assignment: {
        create: 'Failed to create assignment',
        update: 'Failed to update assignment',
        delete: 'Failed to delete assignment',
        fetch: 'Failed to load assignments',
        submit: 'Failed to submit assignment'
    },
    attendance: {
        create: 'Failed to mark attendance',
        update: 'Failed to update attendance',
        fetch: 'Failed to load attendance records'
    },
    grade: {
        create: 'Failed to add grade',
        update: 'Failed to update grade',
        fetch: 'Failed to load grades'
    },
    announcement: {
        create: 'Failed to create announcement',
        update: 'Failed to update announcement',
        delete: 'Failed to delete announcement',
        fetch: 'Failed to load announcements'
    },
    material: {
        create: 'Failed to upload material',
        delete: 'Failed to delete material',
        fetch: 'Failed to load materials',
        download: 'Failed to download material'
    },
    expense: {
        create: 'Failed to add expense',
        update: 'Failed to update expense',
        delete: 'Failed to delete expense',
        fetch: 'Failed to load expenses',
        approve: 'Failed to approve expense'
    },
    account: {
        create: 'Failed to add account',
        update: 'Failed to update account',
        delete: 'Failed to delete account',
        fetch: 'Failed to load accounts'
    },
    book: {
        borrow: 'Failed to borrow book',
        return: 'Failed to return book',
        fetch: 'Failed to load books'
    }
}

/**
 * Extract user-friendly error message from API error response
 * @param {Error} error - The error object from API call
 * @param {string} entity - Entity type (e.g., 'student', 'teacher')
 * @param {string} action - Action type (e.g., 'create', 'update', 'delete')
 * @param {string} fallback - Custom fallback message
 * @returns {string} User-friendly error message
 */
export const getErrorMessage = (error, entity = null, action = null, fallback = null) => {
    // Check if error has response from API
    if (error?.response) {
        const { status, data } = error.response

        // Priority 1: Specific error message from API
        if (data?.error) return data.error
        if (data?.detail) return data.detail
        if (data?.message) return data.message

        // Priority 2: Field-specific validation errors
        if (data?.errors && typeof data.errors === 'object') {
            const firstError = Object.values(data.errors)[0]
            if (Array.isArray(firstError)) return firstError[0]
            return firstError
        }

        // Priority 3: Non-field errors
        if (data?.non_field_errors && Array.isArray(data.non_field_errors)) {
            return data.non_field_errors[0]
        }

        // Priority 3.5: Root level field errors/Validation errors
        // This catches { "cnic": ["Error"] } which is common in DRF
        const validationErrors = getValidationErrors(error)
        const firstField = Object.keys(validationErrors)[0]
        if (firstField) {
            return validationErrors[firstField]
        }

        // Priority 4: Entity-specific error
        if (entity && action && ENTITY_ERRORS[entity]?.[action]) {
            return ENTITY_ERRORS[entity][action]
        }

        // Priority 5: Status code message
        if (STATUS_MESSAGES[status]) {
            return STATUS_MESSAGES[status]
        }
    }

    // Priority 6: Network or other errors
    if (error?.message) {
        if (error.message.includes('Network Error')) {
            return 'Network error. Please check your connection.'
        }
        if (error.message.includes('timeout')) {
            return 'Request timeout. Please try again.'
        }
    }

    // Priority 7: Custom fallback or generic message
    return fallback || 'An unexpected error occurred. Please try again.'
}

/**
 * Get success message for an action
 * @param {string} entity - Entity type
 * @param {string} action - Action type
 * @param {string} customMessage - Custom success message
 * @returns {string} Success message
 */
export const getSuccessMessage = (entity, action, customMessage = null) => {
    if (customMessage) return customMessage

    const messages = {
        create: `${capitalize(entity)} added successfully`,
        update: `${capitalize(entity)} updated successfully`,
        delete: `${capitalize(entity)} deleted successfully`,
        submit: `${capitalize(entity)} submitted successfully`,
        approve: `${capitalize(entity)} approved successfully`,
        borrow: `Book borrowed successfully`,
        return: `Book returned successfully`
    }

    return messages[action] || 'Operation completed successfully'
}

/**
 * Capitalize first letter of string
 */
const capitalize = (str) => {
    if (!str) return ''
    return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Check if error is authentication related
 * @param {Error} error - The error object
 * @returns {boolean}
 */
export const isAuthError = (error) => {
    return error?.response?.status === 401 || error?.response?.status === 403
}

/**
 * Check if error is validation related
 * @param {Error} error - The error object
 * @returns {boolean}
 */
export const isValidationError = (error) => {
    return error?.response?.status === 400 || error?.response?.status === 422
}

/**
 * Check if error is not found
 * @param {Error} error - The error object
 * @returns {boolean}
 */
export const isNotFoundError = (error) => {
    return error?.response?.status === 404
}

/**
 * Format validation errors for display
 * @param {Error} error - The error object
 * @returns {Object} Formatted validation errors
 */
export const getValidationErrors = (error) => {
    if (!error?.response?.data) return {}

    const data = error.response.data
    const errors = {}

    // Handle Django REST Framework style errors
    if (data.errors && typeof data.errors === 'object') {
        return data.errors
    }

    // Handle direct field errors
    Object.keys(data).forEach(key => {
        if (Array.isArray(data[key])) {
            errors[key] = data[key][0]
        } else if (typeof data[key] === 'string') {
            errors[key] = data[key]
        }
    })

    return errors
}

export default {
    getErrorMessage,
    getSuccessMessage,
    isAuthError,
    isValidationError,
    isNotFoundError,
    getValidationErrors
}
