/**
 * Cached Data Composable
 * Reusable caching pattern for data fetching
 */
import { ref } from 'vue'
import { cacheService } from '@/services/shared'

/**
 * Create cached data management
 * @param {string} cacheKey - Cache key for storing data
 * @param {Function} fetchFn - Async function to fetch data
 * @param {object} options - Configuration options
 * @returns {object} Cached data state and methods
 */
export const useCachedData = (cacheKey, fetchFn, options = {}) => {
    const {
        initialLoading = true,
        transform = (data) => data, // Transform function for fetched data
        ttl = null // Cache TTL in ms (null = use default)
    } = options

    const data = ref(null)
    const loading = ref(initialLoading)
    const error = ref(null)

    /**
     * Load data with cache support
     * @param {boolean} forceRefresh - Skip cache and fetch fresh data
     * @returns {Promise<any>} Fetched data
     */
    const load = async (forceRefresh = false) => {
        loading.value = true
        error.value = null

        try {
            // Check cache first (unless force refresh)
            if (!forceRefresh) {
                const cached = cacheService.get(cacheKey)
                if (cached) {
                    data.value = cached
                    loading.value = false
                    return cached
                }
            }

            // Fetch fresh data
            const result = await fetchFn()
            const transformed = transform(result)

            // Cache the data
            if (ttl) {
                cacheService.set(cacheKey, transformed, ttl)
            } else {
                cacheService.set(cacheKey, transformed)
            }

            data.value = transformed
            return transformed
        } catch (err) {
            console.error(`Error loading cached data (${cacheKey}):`, err)
            error.value = err.response?.data?.detail ||
                err.response?.data?.message ||
                err.message ||
                'Failed to load data'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Refresh data (force fetch)
     */
    const refresh = () => load(true)

    /**
     * Clear cache for this key
     */
    const clearCache = () => {
        cacheService.clear(cacheKey)
    }

    /**
     * Clear cache by pattern
     * @param {string} pattern - Pattern to match cache keys
     */
    const clearCachePattern = (pattern) => {
        cacheService.clearPattern(pattern)
    }

    /**
     * Update cached data manually
     * @param {any} newData - New data to cache
     */
    const updateCache = (newData) => {
        data.value = newData
        if (ttl) {
            cacheService.set(cacheKey, newData, ttl)
        } else {
            cacheService.set(cacheKey, newData)
        }
    }

    return {
        // State
        data,
        loading,
        error,

        // Methods
        load,
        refresh,
        clearCache,
        clearCachePattern,
        updateCache
    }
}

/**
 * Create multiple cached data loaders
 * @param {object} config - Configuration object { key: { cacheKey, fetchFn, options } }
 * @returns {object} Object with loaders for each key
 */
export const useCachedDataMultiple = (config) => {
    const loaders = {}

    for (const [key, { cacheKey, fetchFn, options = {} }] of Object.entries(config)) {
        loaders[key] = useCachedData(cacheKey, fetchFn, options)
    }

    /**
     * Load all data
     * @param {boolean} forceRefresh - Skip cache for all
     */
    const loadAll = async (forceRefresh = false) => {
        const promises = Object.values(loaders).map(loader =>
            loader.load(forceRefresh).catch(() => null) // Don't fail all if one fails
        )
        await Promise.all(promises)
    }

    /**
     * Check if any loader is loading
     */
    const isAnyLoading = () => Object.values(loaders).some(l => l.loading.value)

    return {
        ...loaders,
        loadAll,
        isAnyLoading
    }
}

export default useCachedData

