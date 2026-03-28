/**
 * Form Helpers Composable
 * Shared utilities for form handling across all panels
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'

/**
 * Navigate after delay with optional callback
 */
export const useNavigateAfterDelay = () => {
    const router = useRouter()

    const navigateAfterDelay = (route, delay = 1500, callback = null) => {
        setTimeout(() => {
            if (callback) callback()
            router.push(route)
        }, delay)
    }

    return { navigateAfterDelay }
}

/**
 * Standardized Alert state management
 * Use this in ALL components for consistent alert behavior
 */
export const useAlert = () => {
    const alert = ref({ show: false, type: 'success', title: '', message: '' })

    const showAlert = (type, message, title = null) => {
        alert.value = {
            show: true,
            type,
            title: title || (type === 'success' ? 'Success!' : type === 'error' ? 'Error!' : 'Notice'),
            message
        }

        // Auto-hide success alerts after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                clearAlert()
            }, 5000)
        }
    }

    const clearAlert = () => {
        alert.value.show = false
    }

    const showSuccess = (message, title = 'Success!') => showAlert('success', message, title)
    const showError = (message, title = 'Error!') => showAlert('error', message, title)
    const showWarning = (message, title = 'Warning!') => showAlert('warning', message, title)
    const showInfo = (message, title = 'Info') => showAlert('info', message, title)

    return { alert, showAlert, clearAlert, showSuccess, showError, showWarning, showInfo }
}

/**
 * Form factory - creates initial form state
 */
export const createFormFactory = (defaultValues) => {
    return () => ref({ ...defaultValues })
}

// Common form defaults
export const FORM_DEFAULTS = {
    institution: {
        name: '', short_name: '', code: '', established_year: null, website: '',
        email: '', phone: '', address: '', city: '', state: '', postal_code: '',
        country: 'Pakistan', description: '', is_active: true
    },
    department: {
        name: '', code: '', institution: '', head_of_department: '',
        email: '', phone: '', description: '', is_active: true
    },
    course: {
        name: '', code: '', department: '', duration_years: 4, description: ''
    },
    subject: {
        name: '', code: '', semester: '', credit_hours: 3, description: ''
    },
    student: {
        full_name: '', email: '', phone: '', date_of_birth: '', gender: '', cnic: '',
        program: '', session: '', enrollment_year: new Date().getFullYear(),
        current_semester: 1, enrolled_subjects: [], father_name: '',
        guardian_phone: '', address: '', city: ''
    },
    teacher: {
        full_name: '', email: '', phone: '', date_of_birth: '', gender: '', cnic: '',
        department: '', designation: '', qualification: '', specialization: '',
        joining_date: '', experience_years: 0, teaching_subjects: [], address: '', city: ''
    },
    semester: {
        name: '', number: 1, program: '', start_date: '', end_date: '', is_active: true
    },
    session: {
        name: '', program: '', start_date: '', end_date: '', is_active: true
    },
    expense: {
        title: '', description: '', category: 'utilities', amount: 0,
        expense_date: '', vendor: ''
    },
    account: {
        name: '', account_type: 'bank', account_number: '',
        balance: 0, description: '', is_active: true
    },
    announcement: {
        title: '', content: '', subject: '', priority: 'normal',
        is_active: true
    },
    assignment: {
        title: '', description: '', subject: '', due_date: '',
        total_marks: 100, is_active: true
    },
    grade: {
        student: '', subject: '', component: '', marks_obtained: 0,
        total_marks: 100, remarks: ''
    }
}

/**
 * Create form with defaults
 * Usage: const form = createForm('student')
 */
export const createForm = (type) => {
    if (!FORM_DEFAULTS[type]) {
        console.warn(`Unknown form type: ${type}. Available types:`, Object.keys(FORM_DEFAULTS))
        return ref({})
    }
    return ref({ ...FORM_DEFAULTS[type] })
}

/**
 * Reset form to defaults
 * Usage: resetForm(formRef, 'student')
 */
export const resetForm = (formRef, type) => {
    if (FORM_DEFAULTS[type]) {
        Object.assign(formRef.value, FORM_DEFAULTS[type])
    } else {
        console.warn(`Cannot reset form. Unknown type: ${type}`)
    }
}

/**
 * Validate form fields
 * Returns { valid: boolean, errors: object }
 */
export const validateForm = (formData, requiredFields = []) => {
    const errors = {}

    requiredFields.forEach(field => {
        if (!formData[field] || formData[field] === '') {
            errors[field] = `${field.replace(/_/g, ' ')} is required`
        }
    })

    return {
        valid: Object.keys(errors).length === 0,
        errors
    }
}

/**
 * Form submission helper with loading state
 */
export const useFormSubmit = () => {
    const submitting = ref(false)

    const handleSubmit = async (submitFunction, successCallback = null, errorCallback = null) => {
        submitting.value = true
        try {
            const result = await submitFunction()
            if (successCallback) successCallback(result)
            return result
        } catch (error) {
            if (errorCallback) errorCallback(error)
            throw error
        } finally {
            submitting.value = false
        }
    }

    return { submitting, handleSubmit }
}

export default {
    useNavigateAfterDelay,
    useAlert,
    createFormFactory,
    createForm,
    resetForm,
    validateForm,
    useFormSubmit,
    FORM_DEFAULTS
}
