/**
 * Cache Service
 * Centralized caching with optional sessionStorage persistence
 */

class CacheService {
    constructor() {
        this.cache = new Map()
        this.CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
        // Static data that should persist across page refreshes
        this.PERSISTENT_KEYS = [
            'departments_dropdown',
            'programs_dropdown',
            'institutions_dropdown',
            'sessions_dropdown',
            'subjects_dropdown',
            'teachers_dropdown'
        ]
        this._loadFromStorage()
    }

    /**
     * Load persistent data from sessionStorage
     */
    _loadFromStorage() {
        try {
            this.PERSISTENT_KEYS.forEach(key => {
                const stored = sessionStorage.getItem(`cache_${key}`)
                if (stored) {
                    const parsed = JSON.parse(stored)
                    if (Date.now() - parsed.timestamp < this.CACHE_DURATION) {
                        this.cache.set(key, parsed)
                    } else {
                        sessionStorage.removeItem(`cache_${key}`)
                    }
                }
            })
        } catch (e) {
            console.warn('Failed to load cache from storage:', e)
        }
    }

    /**
     * Save to sessionStorage if key is persistent
     */
    _saveToStorage(key, data) {
        if (this.PERSISTENT_KEYS.includes(key)) {
            try {
                sessionStorage.setItem(`cache_${key}`, JSON.stringify(data))
            } catch (e) {
                console.warn('Failed to save cache to storage:', e)
            }
        }
    }

    /**
     * Get cached data
     */
    get(key) {
        const cached = this.cache.get(key)
        if (!cached) return null

        if (Date.now() - cached.timestamp > this.CACHE_DURATION) {
            this.cache.delete(key)
            if (this.PERSISTENT_KEYS.includes(key)) {
                sessionStorage.removeItem(`cache_${key}`)
            }
            return null
        }
        return cached.data
    }

    /**
     * Set cache data
     */
    set(key, data) {
        const cacheEntry = { data, timestamp: Date.now() }
        this.cache.set(key, cacheEntry)
        this._saveToStorage(key, cacheEntry)
    }

    /**
     * Clear specific cache key
     */
    clear(key) {
        this.cache.delete(key)
        if (this.PERSISTENT_KEYS.includes(key)) {
            sessionStorage.removeItem(`cache_${key}`)
        }
    }

    /**
     * Clear all cache
     */
    clearAll() {
        this.cache.clear()
        this.PERSISTENT_KEYS.forEach(key => sessionStorage.removeItem(`cache_${key}`))
    }

    /**
     * Clear cache by pattern
     */
    clearPattern(pattern) {
        if (typeof pattern !== 'string' || pattern.length === 0) return

        Array.from(this.cache.keys()).forEach(key => {
            const keyStr = typeof key === 'string' ? key : String(key)
            if (keyStr.includes(pattern)) {
                this.clear(key)
            }
        })
    }

    has(key) { return this.get(key) !== null }

    getStats() {
        return { size: this.cache.size, keys: Array.from(this.cache.keys()) }
    }

    setCacheDuration(duration) { this.CACHE_DURATION = duration }

    async warmCache(keys, fetchFunctions) {
        return Promise.allSettled(
            keys.map((key, i) =>
                fetchFunctions[i]()
                    .then(data => { this.set(key, data); return { key, success: true } })
                    .catch(error => ({ key, success: false, error }))
            )
        )
    }
}

// Export singleton instance
export default new CacheService()
