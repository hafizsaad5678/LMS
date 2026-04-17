/**
 * Reusable Entity Delete Composable
 * Reduces duplicate code across all Delete views
 */
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { cacheService } from '@/services/shared'

/**
 * Create delete state and handlers for entity deletion
 * @param {Object} options - Configuration options
 * @returns {Object} - Delete state and methods
 */
export const useEntityDelete = (options) => {
    const {
        entityName,
        service,
        listRoute,
        cacheKeys = [],
        getInfoItems = () => []
    } = options

    const router = useRouter()
    const route = useRoute()

    const entityId = computed(() => route.params.id)
    const loading = ref(true)
    const submitting = ref(false)
    const entity = ref({})
    const alert = ref({ show: false, type: 'success', title: '', message: '' })

    const infoItems = computed(() => getInfoItems(entity.value))

    const showAlert = (type, message, title = null) => {
        alert.value = { show: true, type, title, message }
    }

    const getListRouteWithRefresh = () => {
        if (typeof listRoute === 'string') {
            return { path: listRoute, query: { refresh: Date.now() } }
        }

        if (listRoute && typeof listRoute === 'object') {
            return {
                ...listRoute,
                query: {
                    ...(listRoute.query || {}),
                    refresh: Date.now()
                }
            }
        }

        return listRoute
    }

    const loadEntity = async () => {
        if (!entityId.value) {
            loading.value = false
            return
        }
        loading.value = true
        try {
            entity.value = await service.get(entityId.value)
        } catch {
            showAlert('error', `Failed to load ${entityName} details`, 'Error')
            setTimeout(() => router.push(getListRouteWithRefresh()), 2000)
        } finally {
            loading.value = false
        }
    }

    const handleDelete = async () => {
        submitting.value = true
        try {
            await service.delete(entityId.value)

            // Clear caches
            cacheKeys.forEach(key => {
                if (key.includes('*')) {
                    cacheService.clearPattern(key.replace('*', ''))
                } else {
                    cacheService.clear(key)
                }
            })

            showAlert('success', `${entityName} deleted successfully`, 'Success')
            setTimeout(() => router.push(getListRouteWithRefresh()), 1500)
        } catch {
            showAlert('error', `Failed to delete ${entityName}`, 'Error')
        } finally {
            submitting.value = false
        }
    }

    const handleCancel = () => router.push(getListRouteWithRefresh())

    // Watch for route param changes
    watch(() => route.params.id, (newId) => {
        if (newId) loadEntity()
    }, { immediate: false })

    onMounted(() => {
        if (entityId.value) loadEntity()
        else loading.value = false
    })

    return {
        entityId,
        loading,
        submitting,
        entity,
        alert,
        infoItems,
        showAlert,
        loadEntity,
        handleDelete,
        handleCancel
    }
}

export default useEntityDelete

