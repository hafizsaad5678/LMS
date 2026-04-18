/**
 * Reusable Entity List Composable
 * Shared logic for List views across admin panel
 */
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
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

    const route = useRoute()

    // State
    // Optimization: Synchronous cache check during setup to avoid "loading flicker"
    const cachedData = cacheKey ? cacheService.get(cacheKey) : null
    const initialData = cachedData ? normalizeToArray(cachedData) : []
    let hasLoadedOnce = false

    const loading = ref(!cachedData)
    const error = ref(null)
    const data = ref(initialData)
    const filteredData = ref([])
    const buildDefaultFilters = () => ({
        search: '',
        status: '',
        ...options.defaultFilters,
        ...options.resetToDefaults
    })

    const filters = ref(buildDefaultFilters())
    const compareValues = (left, right, operator = 'eq') => {
        switch (operator) {
        case 'contains':
            return String(left || '').toLowerCase().includes(String(right || '').toLowerCase())
        case 'in':
            return Array.isArray(right) && right.includes(left)
        case 'gte':
            return Number(left) >= Number(right)
        case 'lte':
            return Number(left) <= Number(right)
        case 'dateGte':
            return new Date(left).getTime() >= new Date(right).getTime()
        case 'dateLt':
            return new Date(left).getTime() < new Date(right).getTime()
        case 'eq':
        default:
            return String(left) === String(right)
        }
    }

    const applySchemaFilters = (source, schema, activeFilters) => {
        if (!Array.isArray(schema) || schema.length === 0) return source

        return schema.reduce((result, rule) => {
            if (!rule || !rule.key) return result

            const rawFilterValue = activeFilters[rule.key]
            const isRuleActive = typeof rule.isActive === 'function'
                ? rule.isActive(rawFilterValue, activeFilters)
                : rawFilterValue !== '' && rawFilterValue !== null && rawFilterValue !== undefined

            if (!isRuleActive) return result

            return result.filter((item) => {
                if (typeof rule.predicate === 'function') {
                    return rule.predicate(item, rawFilterValue, activeFilters)
                }

                const itemValue = typeof rule.itemValue === 'function'
                    ? rule.itemValue(item, activeFilters)
                    : getNestedValue(item, rule.itemValue || rule.key)

                const filterValue = typeof rule.filterValue === 'function'
                    ? rule.filterValue(rawFilterValue, activeFilters)
                    : rawFilterValue

                const normalize = rule.normalize || ((value) => value)
                return compareValues(
                    normalize(itemValue, item, activeFilters),
                    normalize(filterValue, item, activeFilters),
                    rule.operator || 'eq'
                )
            })
        }, source)
    }


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
        const hasRefreshQuery = !!route.query?.refresh
        const forceFreshFirstLoad = options.forceFreshOnMount && !hasLoadedOnce

        if ((hasRefreshQuery || forceFreshFirstLoad) && cacheKey) {
            cacheService.clear(cacheKey)
        }

        const shouldUseCache = useCache && !forceFreshFirstLoad

        // Check cache first
        if (shouldUseCache && cacheKey && !hasRefreshQuery) {
            const cached = cacheService.get(cacheKey)
            if (cached) {
                const normalizedCached = normalizeToArray(cached)
                data.value = normalizedCached
                applyFilters()
                loading.value = false
                hasLoadedOnce = true

                // Stale-while-revalidate: keep UI fast, then update with latest server data.
                if (options.revalidateOnLoad !== false) {
                    void (async () => {
                        try {
                            const response = await fetchFn()
                            const freshResult = normalizeToArray(response)
                            if (cacheKey) {
                                cacheService.set(cacheKey, freshResult)
                            }
                            data.value = freshResult
                            applyFilters()
                        } catch (revalidateError) {
                            console.warn('Background revalidation failed:', revalidateError)
                        }
                    })()
                }

                return normalizedCached
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
            hasLoadedOnce = true
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
        // Ignore DOM Events passed accidentally via @change="applyFilters"
        const source = Array.isArray(sourceData) ? sourceData : data.value

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

        // Schema-based filter engine for common list filtering patterns.
        if (options.filterSchema) {
            result = applySchemaFilters(result, options.filterSchema, filters.value)
        }

        // Custom filters for special-case rules.
        if (options.customFilter) {
            result = options.customFilter(result, filters.value)
        } else if (filters.value.status) {
            // Fallback for simple active/inactive status if no custom filter provided
            const isHandledBySchema = Array.isArray(options.filterSchema) && options.filterSchema.some(f => f.key === 'status')
            if (!isHandledBySchema) {
                const isActive = filters.value.status === 'active'
                const isInactive = filters.value.status === 'inactive'
                if (isActive || isInactive) {
                    result = result.filter(item => !!item[statusField] === isActive)
                }
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
        filters.value = buildDefaultFilters()
        applyFilters()
    }

    /**
     * Clear cache and reload
     */
    const refresh = async (fetchFn, refreshOptions = {}) => {
        const shouldReset = refreshOptions.reset ?? options.refreshResetsFilters ?? false

        if (shouldReset) {
            resetFilters()
        }

        if (cacheKey) {
            cacheService.clear(cacheKey)
        }
        return loadData(fetchFn, false)
    }

    const refreshAndReset = async (fetchFn) => refresh(fetchFn, { reset: true })

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
        refreshAndReset,
        toggleStatus,
        normalizeResponse: normalizeToArray // Alias for backward compatibility
    }
}

export default useEntityList
