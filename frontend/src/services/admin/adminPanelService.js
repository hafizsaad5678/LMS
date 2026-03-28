/**
 * Admin Panel Service
 * Orchestration layer for admin dashboard with centralized caching
 */
import {
    cacheService,
    getTimeAgo,
    normalizeToArray,
    studentService,
    teacherService,
    departmentService,
    assignmentService,
    sessionService,
    programService,
    subjectService
} from '@/services/shared'
import { feeService } from './managementService'

// Cache key constants for consistency
const CACHE_KEYS = {
    DASHBOARD_STATS: 'admin:dashboard:stats',
    STUDENTS_COUNT: 'admin:students:count',
    TEACHERS_COUNT: 'admin:teachers:count',
    DEPARTMENTS_COUNT: 'admin:departments:count',
    FEES_STATS: 'admin:fees:stats',
    SESSIONS_ACTIVE: 'admin:sessions:active',
    PROGRAMS_COUNT: 'admin:programs:count',
    SUBJECTS_COUNT: 'admin:subjects:count',
    ACTIVITIES_RECENT: 'admin:activities:recent'
}

export const adminPanelService = {
    /**
     * Get dashboard statistics with caching
     */
    async getDashboardStats() {
        const cached = cacheService.get(CACHE_KEYS.DASHBOARD_STATS)
        if (cached) return cached

        try {
            const [students, teachers, depts, feeStats, sessions, programs, subjects] = await Promise.all([
                this.getStudentCount(),
                this.getTeacherCount(),
                this.getDepartmentCount(),
                this.getFeeStatistics(),
                this.getActiveSessions(),
                this.getProgramCount(),
                this.getSubjectCount()
            ])

            const stats = {
                students,
                teachers,
                departments: depts,
                revenue: feeStats.total_collected || 0,
                sessions,
                programs,
                subjects
            }

            cacheService.set(CACHE_KEYS.DASHBOARD_STATS, stats)
            return stats
        } catch (error) {
            console.error('Dashboard stats error:', error)
            return {
                students: 0, teachers: 0, departments: 0,
                revenue: 0, sessions: 0, programs: 0, subjects: 0
            }
        }
    },

    /**
     * Get cached dashboard stats synchronously
     */
    getCachedStats() {
        return cacheService.get(CACHE_KEYS.DASHBOARD_STATS)
    },

    async getStudentCount() {
        const cached = cacheService.get(CACHE_KEYS.STUDENTS_COUNT)
        if (cached !== null) return cached

        const res = await studentService.getAllStudents({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.STUDENTS_COUNT, count)
        return count
    },

    async getTeacherCount() {
        const cached = cacheService.get(CACHE_KEYS.TEACHERS_COUNT)
        if (cached !== null) return cached

        const res = await teacherService.getAllTeachers({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.TEACHERS_COUNT, count)
        return count
    },

    async getDepartmentCount() {
        const cached = cacheService.get(CACHE_KEYS.DEPARTMENTS_COUNT)
        if (cached !== null) return cached

        const res = await departmentService.getAllDepartments({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.DEPARTMENTS_COUNT, count)
        return count
    },

    async getFeeStatistics() {
        const cached = cacheService.get(CACHE_KEYS.FEES_STATS)
        if (cached) return cached

        try {
            const res = await feeService.statistics()
            const data = res.data || {}
            cacheService.set(CACHE_KEYS.FEES_STATS, data)
            return data
        } catch {
            return { total_collected: 0 }
        }
    },

    async getActiveSessions() {
        const cached = cacheService.get(CACHE_KEYS.SESSIONS_ACTIVE)
        if (cached !== null) return cached

        try {
            const data = await sessionService.getSessions({ status: 'active' })
            const count = normalizeToArray(data).length
            cacheService.set(CACHE_KEYS.SESSIONS_ACTIVE, count)
            return count
        } catch {
            return 0
        }
    },

    async getProgramCount() {
        const cached = cacheService.get(CACHE_KEYS.PROGRAMS_COUNT)
        if (cached !== null) return cached

        const res = await programService.getAllPrograms({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.PROGRAMS_COUNT, count)
        return count
    },

    async getSubjectCount() {
        const cached = cacheService.get(CACHE_KEYS.SUBJECTS_COUNT)
        if (cached !== null) return cached

        const res = await subjectService.getAllSubjects({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.SUBJECTS_COUNT, count)
        return count
    },

    /**
     * Get recent activities for dashboard
     */
    async getRecentActivities() {
        const cached = cacheService.get(CACHE_KEYS.ACTIVITIES_RECENT)
        if (cached) return cached

        try {
            const [recentStudents, recentFees, recentAssignments] = await Promise.all([
                studentService.getAllStudents({ ordering: '-created_at', page_size: 3 }),
                feeService.getAll({ ordering: '-created_at', page_size: 3 }),
                assignmentService.getAllAssignments({ ordering: '-created_at', page_size: 3 })
            ])

            const activities = []

            // Student enrollments
            const students = normalizeToArray(recentStudents)
            students.forEach(s => {
                activities.push({
                    id: `student-${s.id}`,
                    message: `New student enrolled: ${s.full_name}`,
                    time: getTimeAgo(s.created_at),
                    timestamp: new Date(s.created_at),
                    type: 'student'
                })
            })

            // Fee payments
            const fees = normalizeToArray(recentFees.data)
            fees.filter(f => f.status === 'paid').forEach(f => {
                activities.push({
                    id: `fee-${f.id}`,
                    message: `Fee payment received from ${f.student_name}`,
                    time: getTimeAgo(f.payment_date || f.updated_at),
                    timestamp: new Date(f.payment_date || f.updated_at),
                    type: 'fee'
                })
            })

            // Assignments
            const assignments = normalizeToArray(recentAssignments)
            assignments.forEach(a => {
                activities.push({
                    id: `assign-${a.id}`,
                    message: `New assignment created: ${a.title}`,
                    time: getTimeAgo(a.created_at),
                    timestamp: new Date(a.created_at),
                    type: 'assignment'
                })
            })

            const sorted = activities.sort((a, b) => b.timestamp - a.timestamp).slice(0, 5)
            cacheService.set(CACHE_KEYS.ACTIVITIES_RECENT, sorted)
            return sorted
        } catch (error) {
            console.error('Error loading activities:', error)
            return []
        }
    },

    /**
     * Search profiles (students/teachers)
     */
    async searchProfiles(query) {
        if (!query?.trim()) return { students: [], teachers: [] }

        const [studentsRes, teachersRes] = await Promise.all([
            studentService.getAllStudents({ search: query }),
            teacherService.getAllTeachers({ search: query })
        ])

        return {
            students: normalizeToArray(studentsRes),
            teachers: normalizeToArray(teachersRes)
        }
    },

    /**
     * Clear all admin cache
     */
    clearCache() {
        cacheService.clearPattern('admin:')
    }
}

export default adminPanelService

