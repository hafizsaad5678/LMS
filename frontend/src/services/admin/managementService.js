import { api } from '@/services/shared'

// ==================== Academic Scheduling ====================

export const eventService = {
    getAll: (params = {}) => api.get('/events/', { params }),
    getById: (id) => api.get(`/events/${id}/`),
    create: (data) => api.post('/events/', data),
    update: (id, data) => api.put(`/events/${id}/`, data),
    delete: (id) => api.delete(`/events/${id}/`),
    upcoming: () => api.get('/events/upcoming/'),
    past: () => api.get('/events/past/'),
    thisMonth: () => api.get('/events/this_month/')
}

export const holidayService = {
    getAll: (params = {}) => api.get('/holidays/', { params }),
    getById: (id) => api.get(`/holidays/${id}/`),
    create: (data) => api.post('/holidays/', data),
    update: (id, data) => api.put(`/holidays/${id}/`, data),
    delete: (id) => api.delete(`/holidays/${id}/`),
    upcoming: () => api.get('/holidays/upcoming/'),
    thisYear: () => api.get('/holidays/this_year/')
}

export const examService = {
    getAll: (params = {}) => api.get('/exams/', { params }),
    getById: (id) => api.get(`/exams/${id}/`),
    create: (data) => api.post('/exams/', data),
    update: (id, data) => api.put(`/exams/${id}/`, data),
    delete: (id) => api.delete(`/exams/${id}/`),
    upcoming: () => api.get('/exams/upcoming/'),
    today: () => api.get('/exams/today/'),
    markCompleted: (id) => api.post(`/exams/${id}/mark_completed/`)
}

export const timetableService = {
    getAll: (params = {}) => api.get('/timetables/', { params }),
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
    getAll: (params = {}) => api.get('/fees/', { params }),
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
    getAll: (params = {}) => api.get('/expenses/', { params }),
    getById: (id) => api.get(`/expenses/${id}/`),
    create: (data) => api.post('/expenses/', data),
    update: (id, data) => api.put(`/expenses/${id}/`, data),
    delete: (id) => api.delete(`/expenses/${id}/`),
    approve: (id, adminId) => api.post(`/expenses/${id}/approve/`, { admin_id: adminId }),
    pendingApproval: () => api.get('/expenses/pending_approval/'),
    byCategory: () => api.get('/expenses/by_category/')
}



export const accountService = {
    getAll: (params = {}) => api.get('/accounts/', { params }),
    getById: (id) => api.get(`/accounts/${id}/`),
    create: (data) => api.post('/accounts/', data),
    update: (id, data) => api.put(`/accounts/${id}/`, data),
    delete: (id) => api.delete(`/accounts/${id}/`),
    totalBalance: () => api.get('/accounts/total_balance/')
}

// ==================== Library ====================

export const libraryBookService = {
    getAll: (params = {}) => api.get('/library-books/', { params }),
    getById: (id) => api.get(`/library-books/${id}/`),
    create: (data) => api.post('/library-books/', data),
    update: (id, data) => api.put(`/library-books/${id}/`, data),
    delete: (id) => api.delete(`/library-books/${id}/`),
    available: () => api.get('/library-books/available/'),
    borrowings: (id) => api.get(`/library-books/${id}/borrowings/`)
}

export const bookBorrowingService = {
    getAll: (params = {}) => api.get('/book-borrowings/', { params }),
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

