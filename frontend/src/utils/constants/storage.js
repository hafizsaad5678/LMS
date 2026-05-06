/**
 * LocalStorage Keys Constants
 * Centralized storage key management
 */

export const STORAGE_KEYS = {
    // Auth
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    USER_ID: 'userId',
    STUDENT_ID: 'student_id',
    USERNAME: 'username',
    USER_EMAIL: 'userEmail',
    USER_ROLE: 'userRole',

    // Announcement helpers (prefix templates – call with userId)
    READ_ANNOUNCEMENTS: (userId) => `read_announcements_${userId}`,
    VISITED_ANNOUNCEMENTS: (userId) => `visited_announcements_${userId}`,
    CURRENT_GPA: (userId) => `current_gpa_${userId}`,
    TODO_LIST: (userId) => `student_todo_list_${userId}`,

    // Cache prefixes
    CACHE_PREFIX: {
        STUDENTS: 'students_list',
        TEACHERS: 'teachers_list',
        DEPARTMENTS: 'departments_list',
        COURSES: 'courses_list',
        SUBJECTS: 'subjects_list',
        SEMESTERS: 'semesters_list',
        SESSIONS: 'sessions_list',
        INSTITUTIONS: 'institutions_list',
        ASSIGNMENTS: 'assignments_list',
        TEACHER_ASSIGNMENTS: 'teacher_assignments_list',
        STUDENT_ASSIGNMENTS: 'student_assignments',
        STUDENT_GRADES: 'student_grades'
    }
}

/**
 * Get user ID from storage with validation
 */
export const getUserId = () => {
    let userId = localStorage.getItem(STORAGE_KEYS.USER_ID)
    if (!userId || userId === 'undefined' || userId === 'null') {
        userId = localStorage.getItem(STORAGE_KEYS.STUDENT_ID)
    }
    if (!userId || userId === 'undefined' || userId === 'null') {
        return null
    }
    return userId
}

/**
 * Set user ID in storage
 */
export const setUserId = (id) => {
    if (id && id !== 'undefined' && id !== 'null') {
        localStorage.setItem(STORAGE_KEYS.USER_ID, id)
    }
}

/**
 * Clear all auth data without nuking user-specific productivity data
 */
export const clearAuthData = () => {
    // Clear top-level string keys
    Object.values(STORAGE_KEYS).forEach(value => {
        if (typeof value === 'string') {
            localStorage.removeItem(value)
        }
    })

    // Clear cache prefixes
    if (STORAGE_KEYS.CACHE_PREFIX) {
        Object.values(STORAGE_KEYS.CACHE_PREFIX).forEach(prefix => {
            localStorage.removeItem(prefix)
        })
    }
}

export default STORAGE_KEYS
