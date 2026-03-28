import { ref, onMounted } from 'vue'
import { studentService } from '@/services/shared'
import { STORAGE_KEYS } from '@/utils/constants/storage'

/**
 * Common student identity logic used across student panel views
 */
export function useStudentBase() {
    const studentName = ref('')
    const studentEnrollment = ref('')
    const studentId = localStorage.getItem(STORAGE_KEYS.USER_ID)
    const loading = ref(false)

    const loadProfile = async (force = false) => {
        if (!studentId) return
        if (!force && studentName.value) return

        try {
            loading.value = true
            const profile = await studentService.getStudent(studentId)
            studentName.value = profile.full_name || profile.name
            studentEnrollment.value = profile.enrollment_number || profile.roll_no
        } catch (err) {
            console.warn('Fail to fetch student profile:', err)
        } finally {
            loading.value = false
        }
    }

    return {
        studentId,
        studentName,
        studentEnrollment,
        loadProfile,
        loadingProfile: loading
    }
}
