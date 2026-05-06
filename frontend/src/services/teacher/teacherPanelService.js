/**
 * Teacher Panel Service
 * Orchestration layer for teacher dashboard with centralized caching
 */
import { api, cacheService, getTimeAgo, normalizeToArray } from '@/services/shared'
import { isDateWithinNextDays } from '@/utils/formatters'

// Cache key constants
const CACHE_KEYS = {
    DASHBOARD_STATS: 'teacher:dashboard:stats',
    MY_CLASSES: 'teacher:myClasses',
    MY_ASSIGNMENTS: 'teacher:myAssignments',
    ACTIVITIES_RECENT: 'teacher:activities:recent'
}

// In-flight request tracking to prevent duplicate calls
const pendingRequests = new Map()

const dedupeRequest = async (key, requestFn) => {
    // If request is already in-flight, return the same promise
    if (pendingRequests.has(key)) {
        return pendingRequests.get(key)
    }

    // Check cache first
    const cached = cacheService.get(key)
    if (cached) return cached

    // Create new request and track it
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

const toAssignmentPayload = (data = {}) => {
    if (data instanceof FormData) return data

    const hasMaterialFile = data?.material_file instanceof File
    if (!hasMaterialFile) return data

    const formData = new FormData()
    Object.entries(data).forEach(([key, value]) => {
        if (value === undefined || value === null || value === '') return
        formData.append(key, value)
    })

    return formData
}

export const teacherPanelService = {
    // ==================== Dashboard Stats ====================
    async getDashboardStats(options = {}) {
        const { forceRefresh = false } = options

        if (!forceRefresh) {
            const stats = cacheService.get(CACHE_KEYS.DASHBOARD_STATS)
            if (stats) {
                const activities = cacheService.get(CACHE_KEYS.ACTIVITIES_RECENT) || []
                return { stats, activities }
            }
        }

        try {
            const response = await api.get('/teacher/dashboard-stats/')
            const data = response.data
            
            const stats = {
                totalClasses: data.counts.classes,
                totalStudents: data.counts.students,
                totalAssignments: data.counts.assignments,
                pendingReviews: data.counts.pending_reviews,
                upcomingDeadlines: data.counts.upcoming_deadlines
            }

            const activities = (data.recent_activities || []).map(a => ({
                ...a,
                time: getTimeAgo(a.time_iso)
            }))

            cacheService.set(CACHE_KEYS.DASHBOARD_STATS, stats)
            cacheService.set(CACHE_KEYS.ACTIVITIES_RECENT, activities)
            
            return { stats, activities }
        } catch (error) {
            console.error('Dashboard stats error:', error)
            return {
                stats: { totalClasses: 0, totalStudents: 0, totalAssignments: 0, pendingReviews: 0, upcomingDeadlines: 0 },
                activities: []
            }
        }
    },

    /**
     * Get cached dashboard stats synchronously
     */
    getCachedStats() {
        return cacheService.get(CACHE_KEYS.DASHBOARD_STATS)
    },

    // ==================== Classes/Subjects ====================
    async getMyClasses(params = {}, options = {}) {
        const { forceRefresh = false } = options
        const normalizedParams = {}
        if (params.session) normalizedParams.session = params.session
        if (params.subject) normalizedParams.subject = params.subject

        const key = `${CACHE_KEYS.MY_CLASSES}:${JSON.stringify(normalizedParams)}`

        if (forceRefresh) {
            cacheService.clear(key)
            pendingRequests.delete(key)

            const response = await api.get('/teacher/my-classes/', {
                params: Object.keys(normalizedParams).length ? normalizedParams : undefined
            })
            cacheService.set(key, response.data)
            return response.data
        }

        return dedupeRequest(key, async () => {
            const response = await api.get('/teacher/my-classes/', {
                params: Object.keys(normalizedParams).length ? normalizedParams : undefined
            })
            return response.data
        })
    },

    async getClassStudents(classId, params = {}) {
        if (!classId) throw new Error('Class ID is required')

        const key = `teacher:class:${classId}:students:${JSON.stringify(params)}`
        return dedupeRequest(key, async () => {
            try {
                const response = await api.get(`/teacher/class/${classId}/students/`, { params })
                return response.data
            } catch (error) {
                if (error.response?.status === 404) {
                    throw new Error('Class not found or not assigned to you')
                }
                throw error
            }
        })
    },

    async getStudentDetail(studentId) {
        if (!studentId) throw new Error('Student ID is required')

        const key = `teacher:student:${studentId}:detail`
        return dedupeRequest(key, async () => {
            try {
                // Teachers can access student details via the main students endpoint 
                // because CanManageStudents permission allows read access for teachers.
                const response = await api.get(`/students/${studentId}/`)
                return response.data
            } catch (error) {
                if (error.response?.status === 404) {
                    throw new Error('Student not found')
                }
                throw error
            }
        })
    },

    // ==================== Assignments ====================
    async getMyAssignments(options = {}) {
        const { forceRefresh = false } = options

        if (forceRefresh) {
            cacheService.clear(CACHE_KEYS.MY_ASSIGNMENTS)
            pendingRequests.delete(CACHE_KEYS.MY_ASSIGNMENTS)

            const response = await api.get('/teacher/my-assignments/')
            cacheService.set(CACHE_KEYS.MY_ASSIGNMENTS, response.data)
            return response.data
        }

        return dedupeRequest(CACHE_KEYS.MY_ASSIGNMENTS, async () => {
            const response = await api.get('/teacher/my-assignments/')
            return response.data
        })
    },

    async getAssignment(id) {
        const response = await api.get(`/assignments/${id}/`)
        return response.data
    },

    async createAssignment(data) {
        const response = await api.post('/assignments/', toAssignmentPayload(data))
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        cacheService.clearPattern('teacher_materials')
        return response.data
    },

    async updateAssignment(id, data) {
        const response = await api.patch(`/assignments/${id}/`, toAssignmentPayload(data))
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        cacheService.clearPattern('teacher_materials')
        return response.data
    },

    async deleteAssignment(id) {
        const response = await api.delete(`/assignments/${id}/`)
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        cacheService.clearPattern('teacher_materials')
        return response.data
    },

    async getAssignmentSubmissions(assignmentId) {
        const response = await api.get(`/assignments/${assignmentId}/submissions/`)
        return response.data
    },

    async markZeroForMissingSubmission(assignmentId, studentId) {
        const response = await api.post(`/assignments/${assignmentId}/mark_zero/`, { student: studentId })
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        cacheService.clearPattern('teacher:activities')
        return response.data
    },

    // ==================== Grade Components (Canonical) ====================
    async getComponents(params) {
        if (!params) return { results: [] }
        const response = await api.get('/grade-components/', { params })
        return response.data
    },

    async createComponent(data) {
        const response = await api.post('/grade-components/', data)
        return response.data
    },

    async updateComponent(id, data) {
        const response = await api.patch(`/grade-components/${id}/`, data)
        return response.data
    },

    async deleteComponent(id) {
        const response = await api.delete(`/grade-components/${id}/`)
        return response.data
    },

    async getComponentMarks(id) {
        const response = await api.get(`/grade-components/${id}/marks/`)
        return response.data
    },

    async bulkUpdateMarks(id, data) {
        const response = await api.post(`/grade-components/${id}/bulk_marks/`, data)
        return response.data
    },

    async initializeStudents(id) {
        const response = await api.post(`/grade-components/${id}/initialize_students/`)
        return response.data
    },

    async getAllMarks(params) {
        const response = await api.get('/student-marks/', { params })
        return response.data
    },

    // ==================== Attendance ====================
    async markAttendance(data) {
        const response = await api.post('/attendance/', data)
        cacheService.clearPattern('teacher:attendance:')
        return response.data
    },

    async bulkMarkAttendance(attendanceData) {
        const response = await api.post('/attendance/bulk_create/', attendanceData)
        cacheService.clearPattern('teacher:attendance:')
        return response.data
    },

    async getAttendanceReport(classId, params = {}) {
        const response = await api.get('/attendance/', { params: { class_id: classId, ...params } })
        return response.data
    },

    async getAllAttendance(params = {}, options = {}) {
        const { forceRefresh = false } = options
        const key = `teacher:attendance:v2:${JSON.stringify(params)}`

        if (!forceRefresh) {
            const cached = cacheService.get(key)
            if (cached) return cached
        } else {
            cacheService.clear(key)
            pendingRequests.delete(key)
        }

        try {
            const baseParams = { ...params }
            const allRows = []
            let page = 1

            while (true) {
                const response = await api.get('/attendance/', { params: { ...baseParams, page } })
                const payload = response.data

                // Non-paginated response fallback
                if (Array.isArray(payload)) {
                    allRows.push(...payload)
                    break
                }

                const pageRows = payload?.results || []
                allRows.push(...pageRows)

                // DRF paginated response uses `next`; stop when it ends
                if (!payload?.next) break
                page += 1
            }

            const data = allRows
            cacheService.set(key, data)
            return data
        } catch (error) {
            console.error('Error loading attendance:', error)
            return []
        }
    },

    // ==================== Grades ====================
    async submitGrades(data) {
        const response = await api.post('/grades/', data)
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        cacheService.clearPattern('teacher:activities')
        return response.data
    },

    async updateGrade(gradeId, data) {
        const response = await api.patch(`/grades/${gradeId}/`, data)
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        cacheService.clearPattern('teacher:activities')
        return response.data
    },

    async getGradeReport(params) {
        // Backward-compatible alias for getAllMarks
        return this.getAllMarks(params)
    },

    // ==================== Quiz Management ====================
    async getQuizzes(params) {
        const response = await api.get('/quizzes/', { params })
        return response.data
    },

    async createQuiz(data) {
        const response = await api.post('/quizzes/', data)
        return response.data
    },

    async updateQuiz(id, data) {
        const response = await api.patch(`/quizzes/${id}/`, data)
        return response.data
    },

    async deleteQuiz(id) {
        const response = await api.delete(`/quizzes/${id}/`)
        return response.data
    },

    async getQuizDetails(id) {
        const response = await api.get(`/quizzes/${id}/`)
        return response.data
    },

    async addQuizQuestion(data) {
        const response = await api.post('/quiz-questions/', data)
        return response.data
    },

    async updateQuizQuestion(questionId, data) {
        const response = await api.patch(`/quiz-questions/${questionId}/`, data)
        return response.data
    },

    async deleteQuizQuestion(questionId) {
        const response = await api.delete(`/quiz-questions/${questionId}/`)
        return response.data
    },

    async publishQuiz(id) {
        const response = await api.post(`/quizzes/${id}/publish/`)
        return response.data
    },

    async unpublishQuiz(id) {
        const response = await api.post(`/quizzes/${id}/unpublish/`)
        return response.data
    },

    async getQuizAttempts(quizId) {
        const response = await api.get(`/quiz-attempts/`, { 
            params: { 
                quiz: quizId,
                latest_only: 'true' // Group by student to avoid repeated entries
            } 
        })
        return response.data
    },

    async getGradeComponents(subjectId = '') {
        const params = subjectId ? { subject: subjectId } : {}
        const response = await api.get('/grade-components/', { params })
        return response.data
    },

    async createGradeComponent(data) {
        // Backward-compatible alias for createComponent
        const response = await api.post('/grade-components/', data)
        return response.data
    },

    async updateGradeComponent(id, data) {
        // Backward-compatible alias for updateComponent
        const response = await api.patch(`/grade-components/${id}/`, data)
        return response.data
    },

    async deleteGradeComponent(id) {
        // Backward-compatible alias for deleteComponent
        const response = await api.delete(`/grade-components/${id}/`)
        return response.data
    },

    async bulkUpdateComponentMarks(componentId, marksData) {
        const response = await api.post(`/grade-components/${componentId}/bulk_marks/`, marksData)
        return response.data
    },

    async getStudentsBySubject(subjectId) {
        const response = await api.get('/student-subjects/', { params: { subject: subjectId } })
        const studentSubjects = response.data.results || response.data || []
        return studentSubjects.map(ss => ({
            id: ss.student_id || ss.student,  // student is the UUID directly
            full_name: ss.student_name || 'Unknown',
            name: ss.student_name || 'Unknown',
            enrollment_number: ss.student_enrollment || ss.student_roll_no,
            roll_no: ss.student_enrollment || ss.student_roll_no,
            email: ss.student_email,
            phone: ss.student?.phone
        }))
    },

    // ==================== Timetable & Exams ====================
    async getTimetable() {
        const response = await api.get('/teacher/timetable/')
        return response.data
    },

    async getExams() {
        const response = await api.get('/teacher/exams/')
        return response.data
    },

    async createExam(data) {
        const response = await api.post('/exams/', data)
        return response.data
    },

    // ==================== Materials ====================
    async getMaterials() {
        const response = await api.get('/teacher/materials/')
        return response.data
    },

    async createMaterial(data) {
        const response = await api.post('/teacher/materials/create/', data)
        return response.data
    },

    async deleteMaterial(id) {
        const response = await api.delete(`/materials/${id}/`)
        return response.data
    },

    async incrementDownloadCount(id) {
        try {
            const response = await api.post(`/materials/${id}/download/`)
            return response.data
        } catch {
            return null
        }
    },

    // ==================== Announcements ====================
    async getAnnouncements() {
        const response = await api.get('/announcements/')
        return response.data
    },

    async createAnnouncement(data) {
        const response = await api.post('/announcements/', data)
        return response.data
    },

    async updateAnnouncement(id, data) {
        const response = await api.patch(`/announcements/${id}/`, data)
        return response.data
    },

    async deleteAnnouncement(id) {
        const response = await api.delete(`/announcements/${id}/`)
        return response.data
    },

    // ==================== Subject Statistics ====================
    async getSubjectStatistics(subjectId) {
        if (!subjectId) throw new Error('Subject ID is required')

        const key = `teacher:subject:${subjectId}:stats`
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            const [assignmentsRes, attendanceRes, gradesRes] = await Promise.allSettled([
                api.get('/assignments/', { params: { subject: subjectId } }),
                api.get('/attendance/', { params: { subject: subjectId } }),
                api.get('/grades/', { params: { submission__assignment__subject: subjectId } })
            ])

            let assignmentCount = 0
            if (assignmentsRes.status === 'fulfilled') {
                const assignments = assignmentsRes.value.data.results || assignmentsRes.value.data || []
                assignmentCount = assignments.length
            }

            let attendanceRate = 0
            if (attendanceRes.status === 'fulfilled') {
                const attendanceRecords = attendanceRes.value.data.results || attendanceRes.value.data || []
                if (attendanceRecords.length > 0) {
                    const presentCount = attendanceRecords.filter(a => a.status === 'present').length
                    attendanceRate = Math.round((presentCount / attendanceRecords.length) * 100)
                }
            }

            let averageGrade = 'N/A'
            if (gradesRes.status === 'fulfilled') {
                const grades = gradesRes.value.data.results || gradesRes.value.data || []
                if (grades.length > 0) {
                    let totalMarksObtained = 0
                    let totalMarksPossible = 0

                    for (const grade of grades) {
                        totalMarksObtained += parseFloat(grade.marks_obtained || 0)
                        totalMarksPossible += parseFloat(grade.total_marks || 0)
                    }

                    if (totalMarksPossible > 0) {
                        averageGrade = ((totalMarksObtained / totalMarksPossible) * 100).toFixed(1) + '%'
                    }
                }
            }

            const stats = { assignmentCount, attendanceRate, averageGrade }
            cacheService.set(key, stats)
            return stats
        } catch (error) {
            console.error('Subject statistics error:', error)
            return { assignmentCount: 0, attendanceRate: 0, averageGrade: 'N/A' }
        }
    },

    // ==================== Student Profile ====================
    async getStudentFromClasses(studentId) {
        if (!studentId) throw new Error('Student ID is required')

        const key = `teacher:student:${studentId}:profile`
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            const classesResponse = await this.getMyClasses()
            const classes = classesResponse.results || classesResponse || []

            for (const cls of classes) {
                try {
                    const studentsResponse = await this.getClassStudents(cls.id)
                    const classStudents = studentsResponse.results || studentsResponse || []

                    const student = classStudents.find(s => s.id.toString() === studentId.toString())
                    if (student) {
                        const result = { ...student, class: cls }
                        cacheService.set(key, result)
                        return result
                    }
                } catch (err) {
                    console.warn(`Error loading students for class ${cls.id}:`, err)
                }
            }

            return null
        } catch (error) {
            console.error('Error finding student:', error)
            return null
        }
    },

    async getAllStudentsFromClasses(options = {}) {
        const {
            session = null,
            subject = null,
            dedupe = false
        } = options

        const key = `teacher:allStudents:${JSON.stringify({ session, subject, dedupe })}`
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            const classParams = {}
            if (session) classParams.session = session
            if (subject) classParams.subject = subject

            const classesResponse = await this.getMyClasses(classParams)
            const classes = classesResponse.results || classesResponse || []
            const uniqueClasses = Array.from(new Map(classes.filter(cls => cls?.id).map(cls => [cls.id, cls])).values())

            const allStudents = []
            for (const cls of uniqueClasses) {
                try {
                    const studentParams = {}
                    if (session) studentParams.session = session

                    const studentsResponse = await this.getClassStudents(cls.id, studentParams)
                    const classStudents = studentsResponse.results || studentsResponse || []

                    classStudents.forEach(student => {
                        allStudents.push({ ...student, class: cls })
                    })
                } catch (err) {
                    console.warn(`Error loading students for class ${cls.id}:`, err)
                }
            }

            if (!dedupe) {
                cacheService.set(key, allStudents)
                return allStudents
            }

            const studentMap = new Map()

            allStudents.forEach(student => {
                const studentId = student.id
                const classInfo = student.class || {}
                const classId = classInfo.id
                const subjectId = classInfo.subject_id || student.subject_id
                const sessionId = classInfo.session_id || student.session_id

                if (!studentMap.has(studentId)) {
                    studentMap.set(studentId, {
                        ...student,
                        class: classInfo,
                        class_ids: classId ? [classId] : [],
                        subject_ids: subjectId ? [subjectId] : [],
                        session_ids: sessionId ? [sessionId] : [],
                        subjects: subjectId ? [{
                            id: subjectId,
                            name: classInfo.subject_name || student.subject_name,
                            code: classInfo.subject_code || student.subject_code
                        }] : [],
                        sessions: sessionId ? [{
                            id: sessionId,
                            name: classInfo.session_name || student.session_name || null,
                            code: classInfo.session_code || null
                        }] : []
                    })
                    return
                }

                const existing = studentMap.get(studentId)

                if (classId && !existing.class_ids.includes(classId)) {
                    existing.class_ids.push(classId)
                }

                if (subjectId && !existing.subject_ids.includes(subjectId)) {
                    existing.subject_ids.push(subjectId)
                    existing.subjects.push({
                        id: subjectId,
                        name: classInfo.subject_name || student.subject_name,
                        code: classInfo.subject_code || student.subject_code
                    })
                }

                if (sessionId && !existing.session_ids.includes(sessionId)) {
                    existing.session_ids.push(sessionId)
                    existing.sessions.push({
                        id: sessionId,
                        name: classInfo.session_name || student.session_name || null,
                        code: classInfo.session_code || null
                    })
                }
            })

            const dedupedStudents = Array.from(studentMap.values())

            cacheService.set(key, dedupedStudents)
            return dedupedStudents
        } catch (error) {
            console.error('Error loading all students:', error)
            return []
        }
    },

    // ==================== Activities ====================
    async getRecentActivities() {
        const cached = cacheService.get(CACHE_KEYS.ACTIVITIES_RECENT)
        if (cached) return cached

        try {
            // Usually dashboard stats call already populated this
            const response = await api.get('/teacher/dashboard-stats/')
            const activities = (response.data.recent_activities || []).map(a => ({
                ...a,
                time: getTimeAgo(a.time_iso)
            }))

            cacheService.set(CACHE_KEYS.ACTIVITIES_RECENT, activities)
            return activities
        } catch {
            return []
        }
    },

    async getActivityLogs() {
        try {
            const response = await api.get('/admin/activity-logs/')
            return response.data.results || []
        } catch {
            return []
        }
    },

    // ==================== Cache Management ====================
    clearCache() {
        cacheService.clearPattern('teacher:')
    }
}

export default teacherPanelService

