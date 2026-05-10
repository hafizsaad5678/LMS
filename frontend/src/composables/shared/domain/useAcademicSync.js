import { ref, watch } from 'vue'
import { semesterService, normalizeToArray } from '@/services/shared'

/**
 * Composable for synchronizing academic sessions and semesters
 */
export function useAcademicSync(formData, sessions) {
  const activeSemesterId = ref('')
  const sessionSemesters = ref([])
  const loadingSessionSemester = ref(false)

  /**
   * Sync academic fields when a session is selected
   */
  const syncAcademicFieldsFromSession = async (sessionId) => {
    if (!sessionId) {
      activeSemesterId.value = ''
      sessionSemesters.value = []
      formData.value.current_semester = ''
      return
    }

    const selectedSession = sessions.value.find((sess) => String(sess.id) === String(sessionId))
    if (selectedSession?.start_year != null) {
      formData.value.enrollment_year = Number(selectedSession.start_year)
    }

    loadingSessionSemester.value = true
    try {
      const responseData = await semesterService.getAll({ session: sessionId })
      const allSemesters = normalizeToArray(responseData)
      
      const sortedSemesters = [...allSemesters].sort((a, b) => {
        const numA = parseInt(a.number) || 0
        const numB = parseInt(b.number) || 0
        return numA - numB
      })

      const activeOnes = sortedSemesters.filter(s => 
        s.status && String(s.status).toLowerCase() === 'active'
      )
      
      if (activeOnes.length > 0) {
        sessionSemesters.value = activeOnes
      } else {
        sessionSemesters.value = sortedSemesters
      }

      if (!sessionSemesters.value.length) {
        activeSemesterId.value = ''
        formData.value.current_semester = ''
        return
      }

      const target = activeOnes.length > 0 ? activeOnes[0] : sortedSemesters[0]
      
      activeSemesterId.value = String(target.id)
      formData.value.current_semester = parseInt(target.number) || 1
      
      return target
    } catch (error) {
      console.error('Error syncing academic fields:', error)
      activeSemesterId.value = ''
      sessionSemesters.value = []
      formData.value.current_semester = ''
      return null
    } finally {
      loadingSessionSemester.value = false
    }
  }

  return {
    activeSemesterId,
    sessionSemesters,
    loadingSessionSemester,
    syncAcademicFieldsFromSession
  }
}
