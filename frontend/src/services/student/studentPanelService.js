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
    async getDashboardStats(studentId) {
        if (!studentId) return this._getDefaultStats()

        const cacheKey = getCacheKey(studentId, 'dashboard:stats')
        const cached = cacheService.get(cacheKey)
        if (cached) return cached

        try {
            // Fetch all data once - studentService handles individual caching
            const [subjects, gradeReport, attendance, assignments, announcements] = await Promise.all([
                studentService.getEnrolledSubjects(studentId),
                studentService.getGradeReport(studentId),
                studentService.getAttendance(studentId),
                studentService.getAssignments(studentId),
                studentService.getAnnouncements(studentId)
            ])

            const summary = gradeReport?.summary || {}
            const normalizedSubjects = normalizeToArray(subjects)
            
            // Filter pending logic: subjects that have assignments/components but aren't graded yet
            const gradedCount = Number(summary.total_grades ?? 0)
            const activeSubjects = normalizedSubjects.filter(s => 
                (Number(s.total_components || 0) + Number(s.total_assignments || 0)) > 0
            ).length

            const stats = {
                enrolledCourses: normalizedSubjects.length,
                gpa: String(summary.overall_gpa ?? '0.00'),
                gradingProgress: `${gradedCount}/${activeSubjects}`,
                attendance: `${this._calculateAttendance(attendance)}%`,
                pendingAssignments: this._calculatePendingAssignments(normalizeToArray(assignments)),
                unreadAnnouncements: this._calculateUnreadAnnouncements(normalizeToArray(announcements))
            }

            cacheService.set(cacheKey, stats)
            return stats
        } catch (error) {
            console.error('Dashboard stats error:', error)
            return this._getDefaultStats()
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
            // These will hit cache since getDashboardStats already fetched them
            const [assignments, attendance, grades, subjects] = await Promise.all([
                studentService.getAssignments(studentId),
                studentService.getAttendance(studentId),
                studentService.getGrades(studentId),
                studentService.getEnrolledSubjects(studentId)
            ])

            const activities = []
            const now = new Date()
            const assignmentsList = normalizeToArray(assignments)
            const gradesList = normalizeToArray(grades)
            const subjectsList = normalizeToArray(subjects)

            // Upcoming assignments
            const upcomingAssignments = assignmentsList
                .filter(a => {
                    const dueDate = a.due_date ? new Date(a.due_date) : null
                    return dueDate && dueDate > now && !a.is_submitted
                })
                .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
                .slice(0, 2)

            upcomingAssignments.forEach(a => {
                const dueDate = new Date(a.due_date)
                const daysUntil = Math.ceil((dueDate - now) / (1000 * 60 * 60 * 24))
                const timeText = daysUntil === 0 ? 'Due today' : daysUntil === 1 ? 'Due tomorrow' : `Due in ${daysUntil} days`

                activities.push({
                    title: `Assignment: ${a.title || 'Untitled'}`,
                    description: `${a.subject_name || a.subject?.name || 'Subject'} • ${timeText}`,
                    time: timeText,
                    icon: 'bi bi-clipboard-check',
                    color: daysUntil <= 2 ? 'text-danger' : 'text-warning'
                })
            })

            // Recent attendance
            const attendanceList = normalizeToArray(attendance)
            const recentAttendance = [...attendanceList]
                .sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))
                .slice(0, 1)

            recentAttendance.forEach(record => {
                const statusIcon = record.status === 'present' ? 'bi bi-check-circle-fill' :
                    record.status === 'absent' ? 'bi bi-x-circle-fill' : 'bi bi-dash-circle-fill'
                const statusColor = record.status === 'present' ? 'text-success' :
                    record.status === 'absent' ? 'text-danger' : 'text-warning'

                activities.push({
                    title: `Attendance: ${record.status?.charAt(0).toUpperCase() + record.status?.slice(1) || 'Marked'}`,
                    description: record.subject_name || record.subject?.name || 'Subject',
                    time: getTimeAgo(record.date),
                    icon: statusIcon,
                    color: statusColor
                })
            })

            // Recent grades
            if (gradesList.length > 0 && activities.length < 5) {
                const recentGrades = [...gradesList]
                    .sort((a, b) => new Date(b.created_at || b.graded_at || 0) - new Date(a.created_at || a.graded_at || 0))
                    .slice(0, 2)

                recentGrades.forEach(grade => {
                    activities.push({
                        title: `Grade posted: ${grade.subject_name || grade.submission?.assignment?.subject?.name || 'Subject'}`,
                        description: `Score: ${grade.marks_obtained || grade.grade_value || grade.marks || grade.grade || 'N/A'}`,
                        time: getTimeAgo(grade.created_at || grade.graded_at),
                        icon: 'bi bi-star-fill',
                        color: 'text-success'
                    })
                })
            }

            // Enrolled subjects as fallback
            if (subjectsList.length > 0 && activities.length < 5) {
                subjectsList.slice(0, 5 - activities.length).forEach(subject => {
                    activities.push({
                        title: `Enrolled: ${subject.subject_name || subject.subject?.name || subject.name}`,
                        description: subject.subject_code || subject.subject?.code || '',
                        time: 'This semester',
                        icon: 'bi bi-book-fill',
                        color: 'text-info'
                    })
                })
            }

            const result = activities.slice(0, 5)
            cacheService.set(key, result)
            return result
        } catch (error) {
            console.error('Error generating activities:', error)
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

