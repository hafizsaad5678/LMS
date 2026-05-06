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
import api from '@/services/shared/core/api'
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

const pendingRequests = new Map()

export const adminPanelService = {
    /**
     * Get dashboard statistics with caching
     */
    async getDashboardStats(forceRefresh = false) {
        if (!forceRefresh) {
            const stats = cacheService.get(CACHE_KEYS.DASHBOARD_STATS)
            if (stats) {
                const activities = cacheService.get(CACHE_KEYS.ACTIVITIES_RECENT) || []
                return { stats, activities }
            }
        }

        if (pendingRequests.has(CACHE_KEYS.DASHBOARD_STATS)) {
            return pendingRequests.get(CACHE_KEYS.DASHBOARD_STATS)
        }

        const fetchPromise = (async () => {
            try {
                const response = await api.get('/admin/dashboard-stats/')
                const data = response.data

                const stats = {
                    students: data.counts.students,
                    teachers: data.counts.teachers,
                    departments: data.counts.departments,
                    revenue: data.revenue || 0,
                    sessions: data.counts.sessions,
                    programs: data.counts.programs,
                    subjects: data.counts.subjects,
                    // Extended management counts
                    holidays: data.counts.holidays,
                    exams: data.counts.exams,
                    events: data.counts.events,
                    timetables: data.counts.timetables,
                    expenses: data.counts.expenses,
                    accounts: data.counts.accounts,
                    library_books: data.counts.library_books,
                    borrowings: data.counts.borrowings
                }

                let activities = []
                if (data.recent_activities) {
                    activities = data.recent_activities.map(a => ({
                        ...a,
                        time: getTimeAgo(a.time_iso)
                    }))
                    cacheService.set(CACHE_KEYS.ACTIVITIES_RECENT, activities)
                }

                cacheService.set(CACHE_KEYS.DASHBOARD_STATS, stats)
                
                // Populate individual counts in cache too to prevent redundant separate calls
                cacheService.set(CACHE_KEYS.STUDENTS_COUNT, stats.students)
                cacheService.set(CACHE_KEYS.TEACHERS_COUNT, stats.teachers)
                cacheService.set(CACHE_KEYS.DEPARTMENTS_COUNT, stats.departments)
                cacheService.set(CACHE_KEYS.SESSIONS_COUNT, stats.sessions)
                cacheService.set(CACHE_KEYS.PROGRAMS_COUNT, stats.programs)
                cacheService.set(CACHE_KEYS.SUBJECTS_COUNT, stats.subjects)

                return { stats, activities }
            } catch (error) {
                console.error('Dashboard stats error:', error)
                return {
                    stats: {
                        students: 0, teachers: 0, departments: 0,
                        revenue: 0, sessions: 0, programs: 0, subjects: 0,
                        holidays: 0, exams: 0, events: 0, timetables: 0,
                        expenses: 0, accounts: 0, library_books: 0, borrowings: 0
                    },
                    activities: []
                }
            } finally {
                pendingRequests.delete(CACHE_KEYS.DASHBOARD_STATS)
            }
        })()

        pendingRequests.set(CACHE_KEYS.DASHBOARD_STATS, fetchPromise)
        return fetchPromise
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
            // Usually dashboard stats call already populated this, 
            // but if called directly we fetch from the same unified endpoint
            const response = await api.get('/admin/dashboard-stats/')
            const data = response.data

            const activities = (data.recent_activities || []).map(a => ({
                ...a,
                time: getTimeAgo(a.time_iso)
            }))

            cacheService.set(CACHE_KEYS.ACTIVITIES_RECENT, activities)
            return activities
        } catch (error) {
            console.error('Recent activities error:', error)
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

