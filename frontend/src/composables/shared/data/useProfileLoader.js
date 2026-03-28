/**
 * Profile Loader Composable
 * Reusable logic for profile/detail pages across all panels
 * 
 * Handles:
 * - Route ID extraction (reactive, handles 'profile' placeholder)
 * - Loading state management
 * - Main entity fetch + sub-resource fetches
 * - Response normalization (Array.isArray / .results)
 * - Watch for route param changes
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { normalizeToArray } from '@/services/shared'

/**
 * Create profile loader state and methods
 * @param {Object} options - Configuration
 * @param {Function} options.fetchMain - Async fn(id) → main entity data
 * @param {Array<Object>} options.subResources - [{key, fetch}] sub-resource fetchers
 * @param {string} options.idParam - Route param name (default: 'id')
 * @returns {Object} - { entityId, loading, entity, subData, reload }
 */
export const useProfileLoader = (options = {}) => {
    const {
        fetchMain,
        subResources = [],
        idParam = 'id'
    } = options

    const route = useRoute()

    // Reactive ID — handles 'profile' placeholder from route config
    const entityId = computed(() => {
        const raw = route.params[idParam]
        return raw && raw !== 'profile' ? raw : null
    })

    const loading = ref(true)
    const entity = ref({})
    const subData = ref(
        Object.fromEntries(subResources.map(r => [r.key, []]))
    )

    /**
     * Load the main entity + all sub-resources
     */
    const load = async () => {
        if (!entityId.value) {
            loading.value = false
            return
        }

        loading.value = true
        try {
            entity.value = await fetchMain(entityId.value)

            // Fetch sub-resources in parallel, silently catch individual failures
            const results = await Promise.allSettled(
                subResources.map(r => r.fetch(entityId.value))
            )

            subResources.forEach((r, i) => {
                if (results[i].status === 'fulfilled') {
                    subData.value[r.key] = normalizeToArray(results[i].value)
                }
            })
        } catch (error) {
            console.error('Error loading profile:', error)
            entity.value = {}
        } finally {
            loading.value = false
        }
    }

    // Watch for route ID changes (in-page navigation)
    watch(entityId, (newId, oldId) => {
        if (newId && newId !== oldId) load()
    })

    onMounted(load)

    return {
        entityId,
        loading,
        entity,
        subData,
        reload: load
    }
}

export default useProfileLoader
