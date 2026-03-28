/**
 * Subject Enrollment Composable
 * Shared logic for enrolling students in subjects or assigning subjects to teachers
 */
import { api } from '@/services/shared'

/**
 * Enroll a student in subjects
 * @param {string} studentId - Student ID
 * @param {Array} subjectIds - Array of subject IDs to enroll
 * @returns {Promise<Object>} - Result with success/failed counts
 */
export const enrollStudentInSubjects = async (studentId, subjectIds) => {
    if (!subjectIds || subjectIds.length === 0) {
        return { success: 0, failed: 0 }
    }

    let success = 0
    let failed = 0

    try {
        // Get existing enrollments
        const existingRes = await api.get(`/student-subjects/?student=${studentId}`)
        const existingSubjectIds = new Set(
            (existingRes.data.results || existingRes.data || []).map(e => e.subject)
        )

        for (const subjectId of subjectIds) {
            if (existingSubjectIds.has(subjectId)) {
                continue // Already enrolled
            }

            try {
                const subjectRes = await api.get(`/subjects/${subjectId}/`)
                await api.post('/student-subjects/', {
                    student: studentId,
                    subject: subjectId,
                    semester: subjectRes.data.semester
                })
                success++
            } catch (e) {
                console.warn('Could not enroll in subject:', subjectId, e)
                failed++
            }
        }
    } catch (e) {
        console.warn('Could not check existing enrollments:', e)
    }

    return { success, failed }
}

/**
 * Assign subjects to a teacher
 * @param {string} teacherId - Teacher ID
 * @param {Array} subjectIds - Array of subject IDs to assign
 * @returns {Promise<Object>} - Result with success/failed counts
 */
export const assignSubjectsToTeacher = async (teacherId, subjectIds) => {
    if (!subjectIds || subjectIds.length === 0) {
        return { success: 0, failed: 0 }
    }

    let success = 0
    let failed = 0

    try {
        // Get existing assignments
        const existingRes = await api.get(`/teachers/${teacherId}/teaching_subjects/`)
        const existingData = Array.isArray(existingRes.data) ? existingRes.data : (existingRes.data.results || [])
        const existingSubjectIds = new Set(existingData.map(a => a.subject || a.subject_id || a.id))

        for (const subjectId of subjectIds) {
            if (existingSubjectIds.has(subjectId)) {
                continue // Already assigned
            }

            try {
                await api.post('/teacher-subjects/', {
                    teacher: teacherId,
                    subject: subjectId
                })
                success++
            } catch (e) {
                console.warn('Could not assign subject:', subjectId, e)
                failed++
            }
        }
    } catch (e) {
        console.warn('Could not check existing assignments:', e)
    }

    return { success, failed }
}

/**
 * Sync teacher subjects (add new, remove unselected)
 * @param {string} teacherId - Teacher ID
 * @param {Array} newSubjectIds - New array of subject IDs
 * @returns {Promise<Object>} - Result with added/removed counts
 */
export const syncTeacherSubjects = async (teacherId, newSubjectIds) => {
    let added = 0
    let removed = 0

    try {
        const currentRes = await api.get(`/teachers/${teacherId}/teaching_subjects/`)
        const currentData = Array.isArray(currentRes.data) ? currentRes.data : (currentRes.data.results || [])
        const currentSubjectIds = currentData.map(a => a.subject || a.subject_id || a.id)

        // Add new subjects
        const toAdd = newSubjectIds.filter(id => !currentSubjectIds.includes(id))
        for (const subjectId of toAdd) {
            try {
                await api.post('/teacher-subjects/', { teacher: teacherId, subject: subjectId })
                added++
            } catch (e) {
                console.warn('Could not add subject:', e)
            }
        }

        // Remove unselected subjects
        const toRemove = currentSubjectIds.filter(id => !newSubjectIds.includes(id))
        for (const subjectId of toRemove) {
            try {
                const assignments = await api.get(`/teacher-subjects/?teacher=${teacherId}&subject=${subjectId}`)
                const assignmentData = Array.isArray(assignments.data) ? assignments.data : (assignments.data.results || [])
                if (assignmentData.length > 0) {
                    await api.delete(`/teacher-subjects/${assignmentData[0].id}/`)
                    removed++
                }
            } catch (e) {
                console.warn('Could not remove subject:', e)
            }
        }
    } catch (e) {
        console.warn('Error syncing subjects:', e)
    }

    return { added, removed }
}

/**
 * Get enrolled subjects for a student
 * @param {string} studentId - Student ID
 * @returns {Promise<Array>} - Array of subject IDs
 */
export const getStudentEnrolledSubjectIds = async (studentId) => {
    try {
        const res = await api.get(`/students/${studentId}/enrolled_subjects/`)
        const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
        return data.map(e => e.subject || e.subject_id || e.id)
    } catch (e) {
        console.warn('Could not load enrolled subjects:', e)
        return []
    }
}

/**
 * Get teaching subjects for a teacher
 * @param {string} teacherId - Teacher ID
 * @returns {Promise<Array>} - Array of subject IDs
 */
export const getTeacherSubjectIds = async (teacherId) => {
    try {
        const res = await api.get(`/teachers/${teacherId}/teaching_subjects/`)
        const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
        return data.map(a => a.subject || a.subject_id || a.id)
    } catch (e) {
        console.warn('Could not load teaching subjects:', e)
        return []
    }
}

export default {
    enrollStudentInSubjects,
    assignSubjectsToTeacher,
    syncTeacherSubjects,
    getStudentEnrolledSubjectIds,
    getTeacherSubjectIds
}

