/**
 * Teacher Panel Service
 * Orchestration layer for teacher dashboard with centralized caching
 */
import { api, cacheService, getTimeAgo, normalizeToArray } from '@/services/shared'

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

export const teacherPanelService = {
    // ==================== Dashboard Stats ====================
    async getDashboardStats() {
        const cached = cacheService.get(CACHE_KEYS.DASHBOARD_STATS)
        if (cached) return cached

        try {
            const [classesResult, assignmentsResult] = await Promise.allSettled([
                this.getMyClasses(),
                this.getMyAssignments()
            ])

            let totalClasses = 0, totalStudents = 0
            if (classesResult.status === 'fulfilled') {
                const classes = classesResult.value
                const classesArray = normalizeToArray(classes)
                totalClasses = classes.count || classesArray.length || 0
                totalStudents = classesArray.reduce((sum, cls) => sum + (cls.student_count || 0), 0)
            }

            let totalAssignments = 0, pendingReviews = 0, upcomingDeadlines = 0
            if (assignmentsResult.status === 'fulfilled') {
                const assignments = assignmentsResult.value
                const assignmentsArray = normalizeToArray(assignments)
                totalAssignments = assignments.count || assignmentsArray.length || 0

                pendingReviews = assignmentsArray.reduce((sum, a) => {
                    const pending = (a.total_students || 0) - (a.submitted || 0)
                    return sum + Math.max(0, pending)
                }, 0)

                const today = new Date()
                const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
                upcomingDeadlines = assignmentsArray.filter(a => {
                    if (!a.due_date) return false
                    const dueDate = new Date(a.due_date)
                    return dueDate >= today && dueDate <= weekFromNow && a.status !== 'closed'
                }).length
            }

            const stats = { totalClasses, totalStudents, totalAssignments, pendingReviews, upcomingDeadlines }
            cacheService.set(CACHE_KEYS.DASHBOARD_STATS, stats)
            return stats
        } catch (error) {
            console.error('Dashboard stats error:', error)
            return { totalClasses: 0, totalStudents: 0, totalAssignments: 0, pendingReviews: 0, upcomingDeadlines: 0 }
        }
    },

    /**
     * Get cached dashboard stats synchronously
     */
    getCachedStats() {
        return cacheService.get(CACHE_KEYS.DASHBOARD_STATS)
    },

    // ==================== Classes/Subjects ====================
    async getMyClasses(params = {}) {
        const normalizedParams = {}
        if (params.session) normalizedParams.session = params.session
        if (params.subject) normalizedParams.subject = params.subject

        const key = `${CACHE_KEYS.MY_CLASSES}:${JSON.stringify(normalizedParams)}`

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
    async getMyAssignments() {
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
        const response = await api.post('/assignments/', data)
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        return response.data
    },

    async updateAssignment(id, data) {
        const response = await api.patch(`/assignments/${id}/`, data)
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        return response.data
    },

    async deleteAssignment(id) {
        const response = await api.delete(`/assignments/${id}/`)
        cacheService.clearPattern('teacher:myAssignments')
        cacheService.clearPattern('teacher:dashboard')
        return response.data
    },

    async getAssignmentSubmissions(assignmentId) {
        const response = await api.get(`/assignments/${assignmentId}/submissions/`)
        return response.data
    },

    // ==================== Grade Components ====================
    async getComponents(params) {
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
        return response.data
    },

    async bulkMarkAttendance(attendanceData) {
        const response = await api.post('/attendance/bulk_create/', attendanceData)
        return response.data
    },

    async getAttendanceReport(classId, params = {}) {
        const response = await api.get('/attendance/', { params: { class_id: classId, ...params } })
        return response.data
    },

    async getAllAttendance(params = {}) {
        const key = `teacher:attendance:${JSON.stringify(params)}`
        const cached = cacheService.get(key)
        if (cached) return cached

        try {
            const response = await api.get('/attendance/', { params: { page_size: 1000, ...params } })
            const data = response.data.results || response.data || []
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
        return response.data
    },

    async updateGrade(gradeId, data) {
        const response = await api.patch(`/grades/${gradeId}/`, data)
        return response.data
    },

    async getGradeReport(params) {
        const response = await api.get('/student-marks/', { params })
        return response.data
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

    async getGradeComponents(subjectId = '') {
        const params = subjectId ? { subject: subjectId } : {}
        const response = await api.get('/grade-components/', { params })
        return response.data
    },

    async createGradeComponent(data) {
        const response = await api.post('/grade-components/', data)
        return response.data
    },

    async updateGradeComponent(id, data) {
        const response = await api.patch(`/grade-components/${id}/`, data)
        return response.data
    },

    async deleteGradeComponent(id) {
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
            // These should hit cache if getDashboardStats was called first
            const [assignmentsRes, classesRes] = await Promise.all([
                this.getMyAssignments(),
                this.getMyClasses()
            ])

            const activities = []
            const assignmentsArray = normalizeToArray(assignmentsRes)
            const classesArray = normalizeToArray(classesRes)

            assignmentsArray.slice(0, 3).forEach(a => {
                activities.push({
                    id: `assign-${a.id}`,
                    message: `Assignment "${a.title}" - ${a.submission_count || a.submitted || 0}/${a.total_students} submitted`,
                    time: getTimeAgo(a.created_at)
                })
            })

            classesArray.slice(0, 2).forEach(c => {
                activities.push({
                    id: `class-${c.id}`,
                    message: `${c.subject_name} - ${c.student_count} students enrolled`,
                    time: 'Active'
                })
            })

            const result = activities.slice(0, 5)
            cacheService.set(CACHE_KEYS.ACTIVITIES_RECENT, result)
            return result
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

