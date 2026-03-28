/**
 * Async State Composable
 * Reusable loading/error state management
 */
import { ref } from 'vue'

/**
 * Create async state management
 * @param {object} options - Configuration options
 * @returns {object} Async state and methods
 */
export const useAsyncState = (options = {}) => {
    const { initialLoading = true } = options

    const loading = ref(initialLoading)
    const error = ref(null)
    const data = ref(null)

    /**
     * Execute async function with loading/error handling
     * @param {Function} asyncFn - Async function to execute
     * @param {object} opts - Options
     * @returns {Promise<any>} Result of async function
     */
    const execute = async (asyncFn, opts = {}) => {
        const { showLoading = true, resetError = true } = opts

        if (showLoading) loading.value = true
        if (resetError) error.value = null

        try {
            const result = await asyncFn()
            data.value = result
            return result
        } catch (err) {
            console.error('Async operation failed:', err)
            error.value = err.response?.data?.detail ||
                err.response?.data?.message ||
                err.message ||
                'An error occurred'
            throw err
        } finally {
            if (showLoading) loading.value = false
        }
    }

    /**
     * Reset state
     */
    const reset = () => {
        loading.value = initialLoading
        error.value = null
        data.value = null
    }

    /**
     * Clear error
     */
    const clearError = () => {
        error.value = null
    }

    /**
     * Set loading state
     * @param {boolean} state - Loading state
     */
    const setLoading = (state) => {
        loading.value = state
    }

    /**
     * Set error
     * @param {string} message - Error message
     */
    const setError = (message) => {
        error.value = message
    }

    return {
        // State
        loading,
        error,
        data,

        // Methods
        execute,
        reset,
        clearError,
        setLoading,
        setError
    }
}

export default useAsyncState
