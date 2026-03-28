/**
 * Reusable Entity Form Composable
 * Shared logic for Add/Edit forms across admin views
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { validateCNIC, extractErrorMessage, normalizeToArray, cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'


/**
 * Create form state and handlers for entity CRUD operations
 * @param {Object} options - Configuration options
 * @returns {Object} - Form state and methods
 */
export const useEntityForm = (options = {}) => {
    const {
        entityName = 'Entity',
        listRoute = ADMIN_ROUTES.DASHBOARD.path,
        redirectDelay = 1500,
        theme = 'admin',
        cacheKeys = [] // Array of cache keys to clear after successful operations
    } = options

    const router = useRouter()

    // Alert state
    const alert = ref({
        show: false,
        type: 'success',
        title: '',
        message: ''
    })

    // Confirm dialog state
    const confirmDialog = ref({
        show: false,
        title: 'Confirm Action',
        message: 'Are you sure?',
        type: 'warning',
        loading: false,
        onConfirm: null
    })

    // Loading states
    const loading = ref(false)
    const submitting = ref(false)

    /**
     * Show alert message
     */
    const showAlert = (type, message, title = null) => {
        alert.value = {
            show: true,
            type,
            title: title || (type === 'success' ? 'Success!' : 'Error!'),
            message
        }
    }

    /**
     * Clear alert
     */
    const clearAlert = () => {
        alert.value.show = false
    }

    /**
     * Show confirm dialog (replaces browser confirm)
     */
    const showConfirm = (options = {}) => {
        return new Promise((resolve) => {
            confirmDialog.value = {
                show: true,
                title: options.title || 'Confirm Action',
                message: options.message || 'Are you sure you want to proceed?',
                type: options.type || 'warning',
                loading: false,
                onConfirm: () => {
                    confirmDialog.value.show = false
                    resolve(true)
                },
                onCancel: () => {
                    confirmDialog.value.show = false
                    resolve(false)
                }
            }
        })
    }

    /**
     * Close confirm dialog
     */
    const closeConfirm = () => {
        if (confirmDialog.value.onCancel) {
            confirmDialog.value.onCancel()
        }
        confirmDialog.value.show = false
    }

    /**
     * Handle confirm action
     */
    const handleConfirmAction = () => {
        if (confirmDialog.value.onConfirm) {
            confirmDialog.value.onConfirm()
        }
    }

    /**
     * Validate CNIC field
     */
    const validateCNICField = (cnic) => {
        if (!validateCNIC(cnic)) {
            showAlert('error', 'CNIC must be exactly 13 digits (e.g., 12345-1234567-1)', 'Validation Error!')
            return false
        }
        return true
    }

    /**
     * Clear related caches
     */
    const clearCaches = () => {
        if (cacheKeys.length > 0) {
            cacheKeys.forEach(key => {
                if (key.includes('*')) {
                    // Pattern-based clearing
                    cacheService.clearPattern(key.replace('*', ''))
                } else {
                    // Exact key clearing
                    cacheService.clear(key)
                }
            })
        }
    }

    /**
     * Handle form submission with error handling
     */
    const handleSubmit = async (submitFn, successMessage) => {
        submitting.value = true
        try {
            await submitFn()

            // Clear caches after successful operation
            clearCaches()

            showAlert('success', successMessage || `${entityName} saved successfully!`)
            setTimeout(() => router.push(listRoute), redirectDelay)
            return true
        } catch (error) {
            console.error(`Error saving ${entityName}:`, error)
            const msg = extractErrorMessage(error, `Failed to save ${entityName}.`)
            showAlert('error', msg)
            return false
        } finally {
            submitting.value = false
        }
    }

    /**
     * Handle cancel with confirmation dialog
     */
    const handleCancel = async () => {
        confirmDialog.value = {
            show: true,
            title: 'Discard Changes?',
            message: 'Are you sure? All unsaved changes will be lost.',
            type: 'warning',
            loading: false,
            onConfirm: () => {
                confirmDialog.value.show = false
                router.push(listRoute)
            },
            onCancel: () => {
                confirmDialog.value.show = false
            }
        }
    }

    /**
     * Navigate back to list
     */
    const goToList = () => {
        router.push(listRoute)
    }

    return {
        // State
        alert,
        confirmDialog,
        loading,
        submitting,
        theme,

        // Methods
        showAlert,
        clearAlert,
        showConfirm,
        closeConfirm,
        handleConfirmAction,
        validateCNICField,
        handleSubmit,
        handleCancel,
        goToList,
        clearCaches
    }
}

/**
 * Create dropdown data loaders
 * @deprecated Use useCascadingDropdowns instead - it includes caching
 */
export const useDropdownLoaders = () => {
    console.warn('useDropdownLoaders is deprecated. Use useCascadingDropdowns instead.')
    return {} // Return empty or implement if really needed
}

export default useEntityForm
