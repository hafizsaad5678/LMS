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
    SESSIONS_COUNT: 'admin:sessions:count',
    PROGRAMS_COUNT: 'admin:programs:count',
    SUBJECTS_COUNT: 'admin:subjects:count',
    ACTIVITIES_RECENT: 'admin:activities:recent'
}

export const adminPanelService = {
    /**
     * Get dashboard statistics with caching
     */
    async getDashboardStats(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.DASHBOARD_STATS)
        if (cached) return cached

        try {
            const [studentsRes, teachersRes, deptsRes, feeStatsRes, sessionsRes, programsRes, subjectsRes] = await Promise.allSettled([
                this.getStudentCount(forceRefresh),
                this.getTeacherCount(forceRefresh),
                this.getDepartmentCount(forceRefresh),
                this.getFeeStatistics(forceRefresh),
                this.getSessionCount(forceRefresh),
                this.getProgramCount(forceRefresh),
                this.getSubjectCount(forceRefresh)
            ])

            const students = studentsRes.status === 'fulfilled' ? studentsRes.value : 0
            const teachers = teachersRes.status === 'fulfilled' ? teachersRes.value : 0
            const depts = deptsRes.status === 'fulfilled' ? deptsRes.value : 0
            const feeStats = feeStatsRes.status === 'fulfilled' ? feeStatsRes.value : { total_collected: 0 }
            const sessions = sessionsRes.status === 'fulfilled' ? sessionsRes.value : 0
            const programs = programsRes.status === 'fulfilled' ? programsRes.value : 0
            const subjects = subjectsRes.status === 'fulfilled' ? subjectsRes.value : 0

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

    async getStudentCount(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.STUDENTS_COUNT)
        if (cached !== null) return cached

        const res = await studentService.getAllStudents({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.STUDENTS_COUNT, count)
        return count
    },

    async getTeacherCount(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.TEACHERS_COUNT)
        if (cached !== null) return cached

        const res = await teacherService.getAllTeachers({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.TEACHERS_COUNT, count)
        return count
    },

    async getDepartmentCount(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.DEPARTMENTS_COUNT)
        if (cached !== null) return cached

        const res = await departmentService.getAllDepartments({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.DEPARTMENTS_COUNT, count)
        return count
    },

    async getFeeStatistics(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.FEES_STATS)
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

    async getSessionCount(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.SESSIONS_COUNT)
        if (cached !== null) return cached

        try {
            const data = await sessionService.getSessions({ page_size: 1 })
            const count = data?.count ?? normalizeToArray(data).length
            cacheService.set(CACHE_KEYS.SESSIONS_COUNT, count)
            return count
        } catch {
            return 0
        }
    },

    async getProgramCount(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.PROGRAMS_COUNT)
        if (cached !== null) return cached

        const res = await programService.getAllPrograms({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.PROGRAMS_COUNT, count)
        return count
    },

    async getSubjectCount(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.SUBJECTS_COUNT)
        if (cached !== null) return cached

        const res = await subjectService.getAllSubjects({ page_size: 1 })
        const count = res.count || normalizeToArray(res).length || 0
        cacheService.set(CACHE_KEYS.SUBJECTS_COUNT, count)
        return count
    },

    /**
     * Get recent activities for dashboard
     */
    async getRecentActivities(forceRefresh = false) {
        const cached = forceRefresh ? null : cacheService.get(CACHE_KEYS.ACTIVITIES_RECENT)
        if (cached) return cached

        try {
            const [
                recentStudentsRes,
                recentTeachersRes,
                recentDepartmentsRes,
                recentProgramsRes,
                recentSessionsRes,
                recentSubjectsRes,
                recentFeesRes,
                recentAssignmentsRes
            ] = await Promise.allSettled([
                studentService.getAllStudents({ ordering: '-updated_at', page_size: 5 }),
                teacherService.getAllTeachers({ ordering: '-updated_at', page_size: 5 }),
                departmentService.getAllDepartments({ ordering: '-updated_at', page_size: 5 }),
                programService.getAllPrograms({ ordering: '-updated_at', page_size: 5 }),
                sessionService.getSessions({ ordering: '-updated_at', page_size: 5 }),
                subjectService.getAllSubjects({ ordering: '-updated_at', page_size: 5 }),
                feeService.getAll({ ordering: '-updated_at', page_size: 5 }),
                assignmentService.getAllAssignments({ ordering: '-updated_at', page_size: 5 })
            ])

            const safeArray = (result, extractor = (v) => v) => {
                if (!result || result.status !== 'fulfilled') return []
                return normalizeToArray(extractor(result.value))
            }

            const toDate = (value) => {
                const date = value ? new Date(value) : null
                return date && !Number.isNaN(date.getTime()) ? date : null
            }

            const getEntityTimestamp = (item) => {
                return (
                    toDate(item.updated_at) ||
                    toDate(item.created_at) ||
                    toDate(item.payment_date) ||
                    null
                )
            }

            const activityAction = (item) => {
                const editCount = Number(item.edit_count || 0)
                const createdAt = toDate(item.created_at)
                const updatedAt = toDate(item.updated_at)
                if (editCount > 0) return 'updated'
                if (createdAt && updatedAt && updatedAt.getTime() - createdAt.getTime() > 1500) return 'updated'
                return 'created'
            }

            const activities = []

            const addEntityActivities = ({ items, type, label, nameFields, icon, color }) => {
                items.forEach((item) => {
                    const timestamp = getEntityTimestamp(item)
                    if (!timestamp) return

                    const action = activityAction(item)
                    const displayName = nameFields
                        .map((field) => item?.[field])
                        .find((v) => typeof v === 'string' && v.trim().length > 0) || `#${item?.id || 'N/A'}`

                    activities.push({
                        id: `${type}-${item.id}-${action}`,
                        message: `${label} ${action}: ${displayName}`,
                        time: getTimeAgo(timestamp.toISOString()),
                        timestamp,
                        type,
                        icon,
                        color
                    })
                })
            }

            addEntityActivities({
                items: safeArray(recentStudentsRes),
                type: 'student',
                label: 'Student',
                nameFields: ['full_name', 'enrollment_number'],
                icon: 'bi bi-person-plus',
                color: 'text-success'
            })

            addEntityActivities({
                items: safeArray(recentTeachersRes),
                type: 'teacher',
                label: 'Teacher',
                nameFields: ['full_name', 'employee_id'],
                icon: 'bi bi-person-badge',
                color: 'text-primary'
            })

            addEntityActivities({
                items: safeArray(recentDepartmentsRes),
                type: 'department',
                label: 'Department',
                nameFields: ['name', 'code'],
                icon: 'bi bi-building',
                color: 'text-info'
            })

            addEntityActivities({
                items: safeArray(recentProgramsRes),
                type: 'program',
                label: 'Program',
                nameFields: ['name', 'code'],
                icon: 'bi bi-mortarboard',
                color: 'text-secondary'
            })

            addEntityActivities({
                items: safeArray(recentSessionsRes),
                type: 'session',
                label: 'Session',
                nameFields: ['session_name', 'session_code'],
                icon: 'bi bi-calendar-event',
                color: 'text-warning'
            })

            addEntityActivities({
                items: safeArray(recentSubjectsRes),
                type: 'subject',
                label: 'Subject',
                nameFields: ['name', 'code'],
                icon: 'bi bi-book',
                color: 'text-dark'
            })

            // Fee payments are useful admin actions; keep explicit status-based message.
            const fees = safeArray(recentFeesRes, (v) => v?.data)
            fees.filter(f => f.status === 'paid').forEach((f) => {
                const timestamp = getEntityTimestamp(f)
                if (!timestamp) return
                activities.push({
                    id: `fee-${f.id}-paid`,
                    message: `Fee payment received: ${f.student_name || 'Student'}`,
                    time: getTimeAgo(timestamp.toISOString()),
                    timestamp,
                    type: 'fee',
                    icon: 'bi bi-cash-coin',
                    color: 'text-success'
                })
            })

            addEntityActivities({
                items: safeArray(recentAssignmentsRes),
                type: 'assignment',
                label: 'Assignment',
                nameFields: ['title'],
                icon: 'bi bi-journal-check',
                color: 'text-primary'
            })

            const sorted = activities.sort((a, b) => b.timestamp - a.timestamp).slice(0, 8)
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

