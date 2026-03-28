/**
 * Composable for getting student ID consistently across the app
 * Replaces direct localStorage access with centralized logic
 */
import { ref, computed } from 'vue'
import { useAuth } from '@/store/auth'
import { STORAGE_KEYS } from '@/utils/constants/storage'

export function useStudentId() {
    const authStore = useAuth()
    const error = ref(null)

    // Computed property that gets student ID from auth store or falls back gracefully
    const studentId = computed(() => {
        // Try auth store first (preferred)
        if (authStore.user?.id) return authStore.user.id
        if (authStore.user?.student_id) return authStore.user.student_id

        // Fallback to localStorage for backward compatibility during migration
        // This will be removed once all components use auth store
        const localId = localStorage.getItem(STORAGE_KEYS.USER_ID) || localStorage.getItem(STORAGE_KEYS.STUDENT_ID)
        return localId || null
    })

    const isValid = computed(() => {
        const id = studentId.value
        return id && id !== 'undefined' && id !== 'null'
    })

    const getStudentId = () => {
        if (!isValid.value) {
            error.value = 'Student ID not found. Please login again.'
            return null
        }
        error.value = null
        return studentId.value
    }

    return {
        studentId,
        isValid,
        error,
        getStudentId
    }
}

export default useStudentId
