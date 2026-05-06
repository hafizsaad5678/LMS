import { api, cacheService } from '@/services/shared'

const pendingRequests = new Map()

/**
 * Generic helper to fetch data with caching and de-duplication
 */
const fetchWithCache = async (key, fetchFn, options = {}) => {
    const { forceRefresh = false, ttl = 300000 } = options // Default 5 mins
    
    if (!forceRefresh) {
        const cached = cacheService.get(key)
        if (cached) return { data: { results: cached, is_cached: true } }
    }

    if (pendingRequests.has(key)) {
        return pendingRequests.get(key)
    }

    const promise = (async () => {
        try {
            const response = await fetchFn()
            // Extract and cache only the results array
            const data = response.data?.results || response.data || []
            cacheService.set(key, data, ttl)
            return response
        } finally {
            pendingRequests.delete(key)
        }
    })()

    pendingRequests.set(key, promise)
    return promise
}

// ==================== Academic Scheduling ====================

export const eventService = {
    getAll: (params = {}, options = {}) => {
        const key = `events:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/events/', { params }), options)
    },
    getById: (id) => api.get(`/events/${id}/`),
    create: (data) => api.post('/events/', data),
    update: (id, data) => api.put(`/events/${id}/`, data),
    delete: (id) => api.delete(`/events/${id}/`),
    upcoming: () => api.get('/events/upcoming/'),
    past: () => api.get('/events/past/'),
    thisMonth: () => api.get('/events/this_month/')
}

export const holidayService = {
    getAll: (params = {}, options = {}) => {
        const key = `holidays:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/holidays/', { params }), options)
    },
    getById: (id) => api.get(`/holidays/${id}/`),
    create: (data) => api.post('/holidays/', data),
    update: (id, data) => api.put(`/holidays/${id}/`, data),
    delete: (id) => api.delete(`/holidays/${id}/`),
    upcoming: () => api.get('/holidays/upcoming/'),
    thisYear: () => api.get('/holidays/this_year/')
}

export const examService = {
    getAll: (params = {}, options = {}) => {
        const key = `exams:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/exams/', { params }), options)
    },
    getById: (id) => api.get(`/exams/${id}/`),
    create: (data) => api.post('/exams/', data),
    update: (id, data) => api.put(`/exams/${id}/`, data),
    delete: (id) => api.delete(`/exams/${id}/`),
    upcoming: () => api.get('/exams/upcoming/'),
    today: () => api.get('/exams/today/'),
    markCompleted: (id) => api.post(`/exams/${id}/mark_completed/`)
}

export const timetableService = {
    getAll: (params = {}, options = {}) => {
        const key = `timetables:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/timetables/', { params }), options)
    },
    getById: (id) => api.get(`/timetables/${id}/`),
    create: (data) => api.post('/timetables/', data),
    update: (id, data) => api.put(`/timetables/${id}/`, data),
    delete: (id) => api.delete(`/timetables/${id}/`),
    byDay: (day) => api.get('/timetables/by_day/', { params: { day } }),
    byTeacher: (teacherId) => api.get('/timetables/by_teacher/', { params: { teacher_id: teacherId } }),
    byRoom: (room) => api.get('/timetables/by_room/', { params: { room } })
}

// ==================== Management/Financial ====================

export const feeService = {
    getAll: (params = {}, options = {}) => {
        const key = `fees:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/fees/', { params }), options)
    },
    getById: (id) => api.get(`/fees/${id}/`),
    create: (data) => api.post('/fees/', data),
    update: (id, data) => api.put(`/fees/${id}/`, data),
    delete: (id) => api.delete(`/fees/${id}/`),
    pending: () => api.get('/fees/pending/'),
    overdue: () => api.get('/fees/overdue/'),
    markPaid: (id) => api.post(`/fees/${id}/mark_paid/`),
    statistics: () => api.get('/fees/statistics/')
}

export const expenseService = {
    getAll: (params = {}, options = {}) => {
        const key = `expenses:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/expenses/', { params }), options)
    },
    getById: (id) => api.get(`/expenses/${id}/`),
    create: (data) => api.post('/expenses/', data),
    update: (id, data) => api.put(`/expenses/${id}/`, data),
    delete: (id) => api.delete(`/expenses/${id}/`),
    approve: (id, adminId) => api.post(`/expenses/${id}/approve/`, { admin_id: adminId }),
    pendingApproval: () => api.get('/expenses/pending_approval/'),
    byCategory: () => api.get('/expenses/by_category/')
}

export const accountService = {
    getAll: (params = {}, options = {}) => {
        const key = `accounts:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/accounts/', { params }), options)
    },
    getById: (id) => api.get(`/accounts/${id}/`),
    create: (data) => api.post('/accounts/', data),
    update: (id, data) => api.put(`/accounts/${id}/`, data),
    delete: (id) => api.delete(`/accounts/${id}/`),
    totalBalance: () => api.get('/accounts/total_balance/')
}

// ==================== Library ====================

export const libraryBookService = {
    getAll: (params = {}, options = {}) => {
        const key = `library-books:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/library-books/', { params }), options)
    },
    getById: (id) => api.get(`/library-books/${id}/`),
    create: (data) => api.post('/library-books/', data),
    update: (id, data) => api.put(`/library-books/${id}/`, data),
    delete: (id) => api.delete(`/library-books/${id}/`),
    available: () => api.get('/library-books/available/'),
    borrowings: (id) => api.get(`/library-books/${id}/borrowings/`)
}

export const bookBorrowingService = {
    getAll: (params = {}, options = {}) => {
        const key = `book-borrowings:all:${JSON.stringify(params)}`
        return fetchWithCache(key, () => api.get('/book-borrowings/', { params }), options)
    },
    getById: (id) => api.get(`/book-borrowings/${id}/`),
    create: (data) => api.post('/book-borrowings/', data),
    update: (id, data) => api.put(`/book-borrowings/${id}/`, data),
    delete: (id) => api.delete(`/book-borrowings/${id}/`),
    overdue: () => api.get('/book-borrowings/overdue/'),
    returnBook: (id) => api.post(`/book-borrowings/${id}/return_book/`)
}

export default {
    eventService,
    holidayService,
    examService,
    timetableService,
    feeService,
    expenseService,
    accountService,
    libraryBookService,
    bookBorrowingService
}

