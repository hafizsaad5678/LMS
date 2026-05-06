/**
 * Student Panel Service
 * Orchestration layer for student dashboard
 * Note: Caching is handled by studentService - no duplicate caching here
 */
import { api, cacheService, getTimeAgo, normalizeToArray, studentService } from '@/services/shared'
import { getFileUrl as _getFileUrl } from '@/utils/constants/config'
import { STORAGE_KEYS } from '@/utils/constants/storage'

// Cache key helper
const getCacheKey = (studentId, type) => `student:${studentId}:${type}`

const normalizeMaterialRecord = (material) => {
    if (!material || typeof material !== 'object') return material

    const normalized = { ...material }
    const title = (normalized.title || '').trim()
    const description = (normalized.description || '').trim()

    if (normalized.material_type === 'assignment') {
        if (title.endsWith(' (Attachment)')) {
            normalized.title = title.slice(0, -13).trim()
        }

        if (description.toLowerCase().startsWith('attachment from assignment:')) {
            normalized.description = 'Material record uploaded by teacher.'
        }

        normalized.material_type = 'outline'
    }

    return normalized
}

export const studentPanelService = {
    /**
     * Get dashboard statistics with caching
     */
    async getDashboardStats(studentId, options = {}) {
        if (!studentId) return { stats: this._getDefaultStats(), activities: [] }
        const { forceRefresh = false } = options
        const cacheKey = getCacheKey(studentId, 'dashboard:stats')

        if (!forceRefresh) {
            const stats = cacheService.get(cacheKey)
            if (stats) {
                const activities = cacheService.get(getCacheKey(studentId, 'activities')) || []
                return { stats, activities }
            }
        }

        try {
            const response = await api.get('/student/dashboard-stats/')
            const { stats, activities } = response.data

            cacheService.set(cacheKey, stats)
            cacheService.set(getCacheKey(studentId, 'activities'), activities)

            return { stats, activities }
        } catch (error) {
            console.error('Dashboard stats error:', error)
            return { stats: this._getDefaultStats(), activities: [] }
        }
    },

    /**
     * Get cached dashboard stats synchronously
     */
    getCachedStats(studentId) {
        if (!studentId) return null
        return cacheService.get(getCacheKey(studentId, 'dashboard:stats'))
    },

    async getStudentProfile(studentId) {
        return studentService.getStudent(studentId)
    },

    /**
     * Generate activities for student dashboard
     */
    async getActivities(studentId) {
        const key = getCacheKey(studentId, 'activities')
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            // Usually dashboard stats call already populated this
            const response = await api.get('/student/dashboard-stats/')
            const activities = response.data.activities || []

            cacheService.set(key, activities)
            return activities
        } catch (error) {
            console.error('Error fetching activities:', error)
            return []
        }
    },

    /**
     * Find student ID by username/email
     */
    async findStudentId(username, email) {
        try {
            let student = null

            if (email) {
                const emailRes = await studentService.getAllStudents({ search: email })
                const emailStudents = normalizeToArray(emailRes)
                student = emailStudents.find(s => s.email === email)
            }

            if (!student && username) {
                const usernameRes = await studentService.getAllStudents({ search: username })
                const usernameStudents = normalizeToArray(usernameRes)
                student = usernameStudents.find(s =>
                    s.user?.username === username || s.enrollment_number === username
                )
            }

            return student?.id || null
        } catch {
            return null
        }
    },

    /**
     * Get class schedule for student
     */
    async getClassSchedule(studentId) {
        if (!studentId) throw new Error('Student ID is required')

        const key = getCacheKey(studentId, 'schedule')
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            const response = await api.get(`/students/${studentId}/class_schedule/`)
            const data = Array.isArray(response.data) ? response.data : (response.data.results || [])
            cacheService.set(key, data)
            return data
        } catch (error) {
            console.error('Error loading class schedule:', error)
            return []
        }
    },

    /**
     * Get exam schedule for student
     */
    async getExamSchedule(studentId) {
        if (!studentId) throw new Error('Student ID is required')

        const key = getCacheKey(studentId, 'exams')
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            const response = await api.get(`/students/${studentId}/exam_schedule/`)
            const data = Array.isArray(response.data) ? response.data : (response.data.results || [])
            cacheService.set(key, data)
            return data
        } catch (error) {
            console.error('Error loading exam schedule:', error)
            return []
        }
    },

    async getLibraryBooks(params = {}) {
        const key = `student:library_books:${JSON.stringify(params)}`
        if (!params._t) {
            const cached = cacheService.get(key)
            if (cached) return cached
        }

        try {
            const response = await api.get('/library-books/', { params })
            const data = response.data.results || response.data || []
            if (!params._t) cacheService.set(key, data)
            return data
        } catch (error) {
            console.error('Error loading library books:', error)
            return []
        }
    },

    /**
     * Get borrowed books for student
     */
    async getBorrowedBooks(params = {}) {
        const key = 'student:borrowedBooks'
        if (!params._t) {
            const cached = cacheService.get(key)
            if (cached) return cached
        }

        try {
            const response = await api.get('/book-borrowings/', { params })
            const data = response.data.results || response.data || []
            if (!params._t) cacheService.set(key, data)
            return data
        } catch (error) {
            console.error('Error loading borrowed books:', error)
            return []
        }
    },

    async getBorrowPolicy(params = {}) {
        const key = 'student:borrowPolicy'
        if (!params._t) {
            const cached = cacheService.get(key)
            if (cached) return cached
        }

        try {
            const response = await api.get('/book-borrowings/borrow_policy/')
            const data = response.data || { free_days: 5, fine_per_day: 10, max_request_days: 30 }
            if (!params._t) cacheService.set(key, data)
            return data
        } catch (error) {
            console.error('Error loading borrow policy:', error)
            return { free_days: 5, fine_per_day: 10, max_request_days: 30 }
        }
    },

    async requestBookBorrow(bookId, requestedDays) {
        try {
            const payload = { book: bookId }
            if (Number.isFinite(requestedDays)) {
                payload.requested_days = requestedDays
            }

            const response = await api.post('/book-borrowings/request_borrow/', payload)
            this.clearCache() // Clear borrowed books cache
            return response.data
        } catch (error) {
            console.error('Error borrowing book:', error)
            throw error
        }
    },

    async returnBook(borrowingId) {
        try {
            const response = await api.post(`/book-borrowings/${borrowingId}/return_book/`)
            this.clearCache() // Clear borrowed books cache
            return response.data
        } catch (error) {
            console.error('Error returning book:', error)
            throw error
        }
    },

    /**
     * Get material details
     */
    async getMaterialDetails(materialId) {
        if (!materialId) throw new Error('Material ID is required')

        const key = `student:material:${materialId}`
        const cached = cacheService.get(key)
        if (cached) return normalizeMaterialRecord(cached)

        try {
            const response = await api.get(`/materials/${materialId}/`)
            const normalized = normalizeMaterialRecord(response.data)
            cacheService.set(key, normalized)
            return normalized
        } catch (error) {
            console.error('Error loading material:', error)
            throw error
        }
    },

    /**
     * Get materials by subject IDs
     */
    async getMaterialsBySubjects(subjectIds) {
        if (!subjectIds || subjectIds.length === 0) return []

        const key = `student:materials:${subjectIds.join(',')}`
        const cached = cacheService.get(key)
        if (cached) return normalizeToArray(cached).map(normalizeMaterialRecord)

        try {
            const response = await api.get('/materials/', {
                params: { subject__in: subjectIds.join(',') }
            })
            const data = normalizeToArray(response.data.results || response.data || []).map(normalizeMaterialRecord)
            cacheService.set(key, data)
            return data
        } catch (error) {
            console.error('Error loading materials:', error)
            return []
        }
    },

    /**
     * Track material download
     */
    async trackMaterialDownload(materialId) {
        try {
            await api.post(`/materials/${materialId}/download/`)
        } catch (error) {
            console.error('Error tracking download:', error)
        }
    },

    // ==================== Quiz Methods ====================
    async getAvailableQuizzes() {
        const key = 'student:quizzes'
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            const response = await api.get('/quizzes/', { params: { is_published: true } })
            const data = response.data.results || response.data || []
            cacheService.set(key, data)
            return data
        } catch (error) {
            console.error('Error loading quizzes:', error)
            return []
        }
    },

    async getQuizDetails(quizId) {
        if (!quizId) throw new Error('Quiz ID is required')

        const key = `student:quiz:${quizId}`
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            const response = await api.get(`/quizzes/${quizId}/`)
            cacheService.set(key, response.data)
            return response.data
        } catch (error) {
            console.error('Error loading quiz details:', error)
            throw error
        }
    },

    async startQuiz(quizId) {
        try {
            const response = await api.post(`/quizzes/${quizId}/start/`)
            // Clear quizzes list cache to update "In Progress" status
            cacheService.clear('student:quizzes')
            return response.data
        } catch (error) {
            console.error('Error starting quiz:', error)
            throw error
        }
    },

    async getQuizAttemptState(attemptId) {
        if (!attemptId) throw new Error('Attempt ID is required')
        try {
            const response = await api.get(`/quiz-attempts/${attemptId}/state/`)
            return response.data
        } catch (error) {
            console.error('Error loading quiz attempt state:', error)
            throw error
        }
    },

    async autosaveQuizAnswer(attemptId, payload) {
        if (!attemptId) throw new Error('Attempt ID is required')
        try {
            const response = await api.patch(`/quiz-attempts/${attemptId}/autosave/`, payload)
            return response.data
        } catch (error) {
            console.error('Error autosaving quiz answer:', error)
            throw error
        }
    },

    async getQuizAttemptSummary(attemptId) {
        if (!attemptId) throw new Error('Attempt ID is required')
        try {
            const response = await api.get(`/quiz-attempts/${attemptId}/summary/`)
            return response.data
        } catch (error) {
            console.error('Error loading quiz summary:', error)
            throw error
        }
    },

    async submitQuizAttemptById(attemptId) {
        if (!attemptId) throw new Error('Attempt ID is required')
        try {
            const response = await api.post(`/quiz-attempts/${attemptId}/submit/`)
            cacheService.clear('student:quizzes')
            return response.data
        } catch (error) {
            console.error('Error submitting quiz attempt:', error)
            throw error
        }
    },

    async getQuizReview(attemptId) {
        if (!attemptId) throw new Error('Attempt ID is required')
        try {
            const response = await api.get(`/quiz-attempts/${attemptId}/review/`)
            return response.data
        } catch (error) {
            console.error('Error loading quiz review:', error)
            throw error
        }
    },

    async getQuizStatus(quizId) {
        try {
            const response = await api.get(`/quizzes/${quizId}/get_status/`)
            return response.data
        } catch (error) {
            console.error('Error getting quiz status:', error)
            throw error
        }
    },

    async submitQuizAttempt(quizId, data) {
        const attemptId = data?.attemptId
        if (attemptId) {
            return this.submitQuizAttemptById(attemptId)
        }
        throw new Error('attemptId is required for submitQuizAttempt')
    },

    clearCache(studentId) {
        studentService.clearCache(studentId)
        if (studentId) {
            cacheService.clear(getCacheKey(studentId, 'dashboard:stats'))
            cacheService.clear(getCacheKey(studentId, 'activities'))
            cacheService.clear(getCacheKey(studentId, 'schedule'))
            cacheService.clear(getCacheKey(studentId, 'exams'))
        }
        cacheService.clear('student:borrowedBooks')
    },

    _getDefaultStats() {
        return { enrolledCourses: 0, gpa: '0.00', gradingProgress: '0/0', attendance: '0%', pendingAssignments: 0, unreadAnnouncements: 0 }
    },

    calculateAttendance(attendance) {
        return this._calculateAttendance(attendance)
    },

    calculatePendingAssignments(assignments) {
        return this._calculatePendingAssignments(assignments)
    },

    async getSubmissions(studentId) {
        if (!studentId) return []
        const key = getCacheKey(studentId, 'submissions')
        const cached = cacheService.get(key)
        if (cached) return cached

        const response = await api.get('/submissions/', { params: { student: studentId, ordering: '-submitted_at' } })
        const data = response.data.results || response.data || []
        cacheService.set(key, data)
        return data
    },

    async submitAssignment(formData) {
        try {
            const response = await api.post('/submissions/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            // Clear stats cache as pending assignments count may change
            const studentId = formData.get('student')
            if (studentId) cacheService.clear(getCacheKey(studentId, 'dashboard:stats'))
            return response.data
        } catch (error) {
            console.error('Error submitting assignment:', error)
            throw error
        }
    },

    /**
     * Helper to get full file URL
     */
    getFileUrl(url) {
        return _getFileUrl(url)
    },

    _calculateAttendance(attendance) {
        if (Array.isArray(attendance) && attendance.length > 0) {
            const total = attendance.length
            const present = attendance.filter(r => r.status?.toLowerCase() === 'present' || r.is_present === true).length
            return Math.round((present / total) * 100)
        }
        if (attendance && !Array.isArray(attendance)) {
            const total = attendance.total_classes || attendance.total || 0
            const present = attendance.present_count || attendance.present || 0
            if (total > 0) return Math.round((present / total) * 100)
        }
        return 0
    },

    _calculatePendingAssignments(assignments) {
        const now = new Date()
        return assignments.filter(a => {
            const dueDate = a.due_date ? new Date(a.due_date) : null
            return dueDate && dueDate > now && !a.is_submitted
        }).length
    },

    _calculateUnreadAnnouncements(announcements) {
        // Read/view tracking is intentionally disabled for announcements.
        return announcements.length
    }
}

export default studentPanelService

