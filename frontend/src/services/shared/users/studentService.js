/**
 * Student Service - Refactored with unified API wrapper and caching
 */
import { apiGet, apiPost, apiPut, apiPatch, apiDelete } from '../core/apiWrapper'
import cacheService from '../core/cacheService'

// Cache key helper
const getCacheKey = (studentId, type) => `student:${studentId}:${type}`

// In-flight request tracking to prevent duplicate calls
const pendingRequests = new Map()

const dedupeRequest = async (key, requestFn) => {
    if (pendingRequests.has(key)) {
        return pendingRequests.get(key)
    }

    const cached = cacheService.get(key)
    if (cached) return cached

    const promise = requestFn().then(data => {
        cacheService.set(key, data)
        pendingRequests.delete(key)
        return data
    }).catch(err => {
        pendingRequests.delete(key)
        throw err
    })

    pendingRequests.set(key, promise)
    return promise
}

export const studentService = {
    getAllStudents: (params = {}) =>
        apiGet('/students/', params, 'fetching students'),

    async getStudent(id) {
        return dedupeRequest(getCacheKey(id, 'profile'), () =>
            apiGet(`/students/${id}/`, null, `fetching student ${id}`)
        )
    },

    createStudent: (data) =>
        apiPost('/students/', data, 'creating student'),

    updateStudent: (id, data) => {
        cacheService.clearPattern(`student:${id}:`)
        return apiPut(`/students/${id}/`, data, `updating student ${id}`)
    },

    patchStudent: (id, data) => {
        cacheService.clearPattern(`student:${id}:`)
        return apiPatch(`/students/${id}/`, data, `patching student ${id}`)
    },

    deleteStudent: (id) => {
        cacheService.clearPattern(`student:${id}:`)
        return apiDelete(`/students/${id}/`, `deleting student ${id}`)
    },

    async getEnrolledSubjects(id) {
        return dedupeRequest(getCacheKey(id, 'subjects'), () =>
            apiGet(`/students/${id}/enrolled_subjects/`, null, `fetching enrolled subjects for student ${id}`)
        )
    },

    getSubjectDetails: (id) =>
        apiGet(`/subjects/${id}/`, null, `fetching subject details ${id}`),

    getStudentSubjects(id) {
        return this.getEnrolledSubjects(id)
    },

    async getAttendance(id) {
        return dedupeRequest(getCacheKey(id, 'attendance'), () =>
            apiGet(`/students/${id}/attendance/`, null, `fetching attendance for student ${id}`)
        )
    },

    async getGrades(id) {
        return dedupeRequest(getCacheKey(id, 'grades'), () =>
            apiGet(`/students/${id}/grades/`, null, `fetching grades for student ${id}`)
        )
    },

    async getGradeReport(id) {
        return dedupeRequest(getCacheKey(id, 'grade-report'), () =>
            apiGet(`/students/${id}/grade-report/`, null, `fetching grade report for student ${id}`)
        )
    },

    async getAssignments(id) {
        return dedupeRequest(getCacheKey(id, 'assignments'), () =>
            apiGet(`/students/${id}/assignments/`, null, `fetching assignments for student ${id}`)
        )
    },

    async getAnnouncements(id) {
        return dedupeRequest(getCacheKey(id, 'announcements'), () =>
            apiGet(`/students/${id}/announcements/`, null, `fetching announcements for student ${id}`)
        )
    },

    async toggleStatus(id) {
        const student = await this.getStudent(id)
        const endpoint = student.is_active ? 'deactivate' : 'activate'
        cacheService.clearPattern(`student:${id}:`)
        return apiPost(`/students/${id}/${endpoint}/`, null, `toggling status for student ${id}`)
    },

    // Clear cache for a student (call after mutations)
    clearCache(id) {
        if (id) {
            cacheService.clearPattern(`student:${id}:`)
        } else {
            cacheService.clearPattern('student:')
        }
    }
}

export default studentService


