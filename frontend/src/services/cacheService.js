/**
 * Cache Service
 * Centralized caching for API responses
 */

class CacheService {
    constructor() {
        this.cache = new Map()
        this.CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
    }

    /**
     * Get cached data
     * @param {string} key - Cache key
     * @returns {any|null} - Cached data or null if expired/not found
     */
    get(key) {
        const cached = this.cache.get(key)

        if (!cached) return null

        const now = Date.now()
        if (now - cached.timestamp > this.CACHE_DURATION) {
            this.cache.delete(key)
            return null
        }

        return cached.data
    }

    /**
     * Set cache data
     * @param {string} key - Cache key
     * @param {any} data - Data to cache
     */
    set(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        })
    }

    /**
     * Clear specific cache key
     * @param {string} key - Cache key to clear
     */
    clear(key) {
        this.cache.delete(key)
    }

    /**
     * Clear all cache
     */
    clearAll() {
        this.cache.clear()
    }

    /**
     * Clear cache by pattern
     * @param {string} pattern - Pattern to match (e.g., 'teachers')
     */
    clearPattern(pattern) {
        const keys = Array.from(this.cache.keys())
        keys.forEach(key => {
            if (key.includes(pattern)) {
                this.cache.delete(key)
            }
        })
    }

    /**
     * Check if cache exists and is valid
     * @param {string} key - Cache key
     * @returns {boolean}
     */
    has(key) {
        return this.get(key) !== null
    }

    /**
     * Get cache statistics
     * @returns {object}
     */
    getStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        }
    }
}

// Export singleton instance
export default new CacheService()
