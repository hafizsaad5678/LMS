/**
 * Reusable Entity List Composable
 * Shared logic for List views across admin panel
 */
import { ref, computed, watch } from 'vue'
import { cacheService, normalizeToArray } from '@/services/shared'
import { smartSearch } from '@/utils'


/**
 * Create list state and handlers for entity listing
 * @param {Object} options - Configuration options
 * @returns {Object} - List state and methods
 */
export const useEntityList = (options = {}) => {
    const {
        cacheKey = '',
        searchFields = ['name', 'email'],
        statusField = 'is_active',
        debounceMs = 300
    } = options

    // State
    // Optimization: Synchronous cache check during setup to avoid "loading flicker"
    const cachedData = cacheKey ? cacheService.get(cacheKey) : null
    const initialData = cachedData ? normalizeToArray(cachedData) : []

    const loading = ref(!cachedData)
    const error = ref(null)
    const data = ref(initialData)
    const filteredData = ref([])
    const filters = ref({
        search: '',
        status: '',
        ...options.defaultFilters
    })

    // Stats computed
    const stats = computed(() => {
        const total = data.value.length
        const active = data.value.filter(item => item[statusField]).length
        return {
            total,
            active,
            inactive: total - active
        }
    })

    /**
     * Load data with optional caching
     * @param {Function} fetchFn - Async function to fetch data
     * @param {boolean} useCache - Whether to use cache
     */
    const loadData = async (fetchFn, useCache = true) => {
        // Check cache first
        if (useCache && cacheKey) {
            const cached = cacheService.get(cacheKey)
            if (cached) {
                data.value = cached
                applyFilters()
                loading.value = false
                return cached
            }
        }

        loading.value = true
        error.value = null
        try {
            const response = await fetchFn()
            const result = normalizeToArray(response)

            // Store in cache
            if (cacheKey) {
                cacheService.set(cacheKey, result)
            }

            data.value = result
            applyFilters()
            return result
        } catch (err) {
            console.error('Error loading data:', err)
            error.value = err.response?.data?.error || err.message || 'Failed to load data'
            data.value = []
            filteredData.value = []
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Get nested value from object
     */
    const getNestedValue = (obj, path) => {
        if (!path) return ''
        return path.split('.').reduce((acc, part) => acc && acc[part], obj)
    }

    /**
     * Apply filters to data
     * @param {Array} sourceData - Optional source data (defaults to loaded data)
     */
    const applyFilters = (sourceData = null) => {
        const source = sourceData || data.value

        // Ensure source is an array
        if (!Array.isArray(source)) {
            filteredData.value = []
            return
        }

        let result = source

        // Search filter
        const query = filters.value.search
        if (query) {
            result = result.filter(item => smartSearch(item, query, searchFields))
        }

        // Custom filters - Handle ALL other filtering logic (status, category, etc.)
        if (options.customFilter) {
            result = options.customFilter(result, filters.value)
        } else if (filters.value.status) {
            // Fallback for simple active/inactive status if no custom filter provided
            const isActive = filters.value.status === 'active'
            const isInactive = filters.value.status === 'inactive'
            if (isActive || isInactive) {
                result = result.filter(item => !!item[statusField] === isActive)
            }
        }

        filteredData.value = result
    }

    // Apply initial filters if we have data from cache
    if (initialData.length > 0) {
        applyFilters()
    }

    /**
     * Reset all filters
     */
    const resetFilters = () => {
        filters.value = {
            search: '',
            status: '',
            ...options.defaultFilters
        }
        applyFilters()
    }

    /**
     * Clear cache and reload
     */
    const refresh = async (fetchFn) => {
        if (cacheKey) {
            cacheService.clear(cacheKey)
        }
        return loadData(fetchFn, false)
    }

    /**
     * Toggle item status
     */
    const toggleStatus = async (item, toggleFn) => {
        try {
            await toggleFn(item.id)
            if (cacheKey) {
                cacheService.clear(cacheKey)
            }
            // Update local data
            const index = data.value.findIndex(d => d.id === item.id)
            if (index !== -1) {
                data.value[index][statusField] = !data.value[index][statusField]
                applyFilters()
            }
            return true
        } catch (error) {
            console.error('Error toggling status:', error)
            throw error
        }
    }


    // Track search separately for debouncing
    let searchTimeout = null

    // Watch for search changes with debounce
    watch(() => filters.value.search, (newSearch) => {
        clearTimeout(searchTimeout)
        searchTimeout = setTimeout(() => {
            applyFilters()
        }, debounceMs)
    })

    // Watch for ALL other filter changes (immediate)
    // We watch the whole filters object but exclude 'search' from triggering immediate apply if we want to be strict,
    // but usually applying immediately on anything else is fine.
    watch(() => {
        const { search, ...rest } = filters.value
        return rest
    }, () => {
        applyFilters()
    }, { deep: true })

    return {
        // State
        loading,
        error,
        data,
        filteredData,
        filters,
        stats,

        // Methods
        loadData,
        applyFilters,
        resetFilters,
        refresh,
        toggleStatus,
        normalizeResponse: normalizeToArray // Alias for backward compatibility
    }
}

export default useEntityList
