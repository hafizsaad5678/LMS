/**
 * Badge Helper Utilities
 * Centralized badge class mappings for consistent UI across all panels
 */

/**
 * Get status badge class
 * @param {string} status - Status value
 * @returns {string} Badge class
 */
export const getStatusBadgeClass = (status) => {
    const statusMap = {
        active: 'bg-success',
        inactive: 'bg-warning',
        pending: 'bg-info',
        paid: 'bg-success',
        overdue: 'bg-danger',
        unpaid: 'bg-danger',
        approved: 'bg-success',
        rejected: 'bg-danger',
        completed: 'bg-success',
        cancelled: 'bg-secondary'
    }
    return statusMap[status?.toLowerCase()] || 'bg-secondary'
}

/**
 * Get attendance status badge class
 * @param {string} status - Attendance status
 * @returns {string} Badge class
 */
export const getAttendanceBadgeClass = (status) => {
    const statusMap = {
        present: 'bg-success',
        absent: 'bg-danger',
        late: 'bg-warning',
        excused: 'bg-info'
    }
    return statusMap[status?.toLowerCase()] || 'bg-secondary'
}

/**
 * Get attendance status icon
 * @param {string} status - Attendance status
 * @returns {string} Icon class
 */
export const getAttendanceIcon = (status) => {
    const iconMap = {
        present: 'bi-check-circle-fill',
        absent: 'bi-x-circle-fill',
        late: 'bi-dash-circle-fill',
        excused: 'bi-info-circle-fill'
    }
    return iconMap[status?.toLowerCase()] || 'bi-circle-fill'
}

/**
 * Get priority badge class
 * @param {string} priority - Priority level
 * @returns {string} Badge class
 */
export const getPriorityBadgeClass = (priority) => {
    const priorityMap = {
        high: 'badge-soft-danger',
        urgent: 'badge-soft-danger',
        medium: 'badge-soft-warning',
        normal: 'badge-soft-info',
        low: 'badge-soft-success'
    }
    return priorityMap[priority?.toLowerCase()] || 'badge-soft-secondary'
}

/**
 * Get priority icon
 * @param {string} priority - Priority level
 * @returns {string} Icon class
 */
export const getPriorityIcon = (priority) => {
    const iconMap = {
        high: 'bi bi-exclamation-triangle-fill',
        urgent: 'bi bi-exclamation-octagon-fill',
        medium: 'bi bi-info-circle-fill',
        normal: 'bi bi-circle-fill',
        low: 'bi bi-check-circle-fill'
    }
    return iconMap[priority?.toLowerCase()] || 'bi bi-circle-fill'
}

/**
 * Get assessment type badge class
 * @param {string} type - Assessment type
 * @returns {string} Badge class
 */
export const getAssessmentBadgeClass = (type) => {
    return getAssessmentTypeBadgeClass(type)
}

/**
 * Get assessment type badge class (alias)
 * @param {string} type - Assessment type
 * @returns {string} Badge class
 */
export const getAssessmentTypeBadgeClass = (type) => {
    const typeMap = {
        assignment: 'badge bg-primary-light text-primary px-3',
        quiz: 'badge bg-info-light text-info px-3',
        midterm: 'badge bg-warning-light text-warning px-3',
        final: 'badge bg-danger-light text-danger px-3',
        project: 'badge bg-success-light text-success px-3',
        participation: 'badge bg-light text-muted px-3',
        lab: 'badge bg-purple-light text-purple px-3',
        presentation: 'badge bg-teal-light text-teal px-3'
    }
    return typeMap[type?.toLowerCase()] || 'badge bg-light text-muted px-3'
}

/**
 * Get grade badge class based on percentage or letter grade
 * @param {string|number} grade - Grade value (letter or percentage)
 * @returns {string} Badge class
 */
export const getGradeBadgeClass = (grade) => {
    // Handle letter grades
    if (typeof grade === 'string') {
        if (['A+', 'A', 'A-'].includes(grade)) return 'badge-soft-success'
        if (['B+', 'B', 'B-'].includes(grade)) return 'badge-soft-info'
        if (['C+', 'C', 'C-'].includes(grade)) return 'badge-soft-warning'
        if (['D+', 'D', 'D-'].includes(grade)) return 'badge-soft-orange'
        return 'badge-soft-danger'
    }

    // Handle percentage
    const percentage = Number(grade)
    if (percentage >= 80) return 'badge-soft-success'
    if (percentage >= 60) return 'badge-soft-info'
    if (percentage >= 40) return 'badge-soft-warning'
    return 'badge-soft-danger'
}

/**
 * Calculate letter grade from percentage
 * @param {number} percentage - Percentage value
 * @returns {string} Letter grade
 */
export const calculateLetterGrade = (percentage) => {
    if (percentage >= 90) return 'A+'
    if (percentage >= 85) return 'A'
    if (percentage >= 80) return 'A-'
    if (percentage >= 75) return 'B+'
    if (percentage >= 70) return 'B'
    if (percentage >= 65) return 'B-'
    if (percentage >= 60) return 'C+'
    if (percentage >= 55) return 'C'
    if (percentage >= 50) return 'C-'
    if (percentage >= 45) return 'D+'
    if (percentage >= 40) return 'D'
    return 'F'
}

/**
 * Get progress bar class based on percentage
 * @param {number} percentage - Percentage value
 * @returns {string} Progress bar class
 */
export const getProgressBarClass = (percentage) => {
    if (percentage >= 80) return 'bg-success'
    if (percentage >= 60) return 'bg-info'
    if (percentage >= 40) return 'bg-warning'
    return 'bg-danger'
}

/**
 * Get attendance percentage color class
 * @param {number} percentage - Attendance percentage
 * @returns {string} Color class
 */
export const getAttendanceColorClass = (percentage) => {
    if (percentage >= 85) return 'bg-success'
    if (percentage >= 75) return 'bg-warning'
    return 'bg-danger'
}

/**
 * Get attendance status label
 * @param {number} percentage - Attendance percentage
 * @returns {string} Status label
 */
export const getAttendanceStatusLabel = (percentage) => {
    if (percentage >= 85) return 'Good'
    if (percentage >= 75) return 'Average'
    return 'Poor'
}

/**
 * Format assessment type for display
 * @param {string} type - Assessment type
 * @returns {string} Formatted type
 */
export const formatAssessmentType = (type) => {
    const typeMap = {
        assignment: 'Assignment',
        quiz: 'Quiz',
        midterm: 'Midterm',
        final: 'Final Exam',
        project: 'Project',
        participation: 'Participation',
        lab: 'Lab Work',
        presentation: 'Presentation'
    }
    return typeMap[type?.toLowerCase()] || type || 'N/A'
}

/**
 * Get holiday type badge class
 * @param {string} type - Holiday type
 * @returns {string} Badge class
 */
export const getHolidayBadgeClass = (type) => {
    const typeMap = {
        public: 'bg-admin',
        academic: 'bg-info',
        religious: 'bg-success',
        national: 'bg-warning'
    }
    return typeMap[type?.toLowerCase()] || 'bg-secondary'
}

// ==================== Assignment Status Helpers ====================

/**
 * Check if assignment is submitted
 * @param {Object} assignment - Assignment object
 * @returns {boolean}
 */
export const isAssignmentSubmitted = (assignment) => {
    if (!assignment) return false
    return assignment.is_submitted || !!assignment.submitted_at
}

/**
 * Check if assignment is overdue
 * @param {Object} assignment - Assignment object
 * @returns {boolean}
 */
export const isAssignmentOverdue = (assignment) => {
    if (!assignment || !assignment.due_date) return false
    return new Date(assignment.due_date) < new Date()
}

/**
 * Get assignment status text
 * @param {Object} assignment - Assignment object
 * @returns {string}
 */
export const getAssignmentStatusText = (assignment) => {
    if (!assignment) return ''
    if (isAssignmentSubmitted(assignment)) return 'Submitted'
    if (isAssignmentOverdue(assignment)) return 'Overdue'
    return 'Pending'
}

/**
 * Get assignment status color
 * @param {Object} assignment - Assignment object
 * @returns {string}
 */
export const getAssignmentStatusColor = (assignment) => {
    if (!assignment) return 'secondary'
    if (isAssignmentSubmitted(assignment)) return 'success'
    if (isAssignmentOverdue(assignment)) return 'danger'
    return 'warning'
}

/**
 * Get assignment status background class
 * @param {Object} assignment - Assignment object
 * @returns {string}
 */
export const getAssignmentStatusBgClass = (assignment) => {
    if (!assignment) return ''
    if (isAssignmentSubmitted(assignment)) return 'badge-soft-success'
    if (isAssignmentOverdue(assignment)) return 'badge-soft-danger'
    return 'badge-soft-warning'
}

/**
 * Get assignment status icon
 * @param {Object} assignment - Assignment object
 * @returns {string}
 */
export const getAssignmentStatusIcon = (assignment) => {
    if (!assignment) return 'info'
    if (isAssignmentSubmitted(assignment)) return 'check-circle-fill'
    if (isAssignmentOverdue(assignment)) return 'x-circle-fill'
    return 'clock-fill'
}

/**
 * Get due date text color class
 * @param {Object} assignment - Assignment object
 * @returns {string}
 */
export const getDueDateClass = (assignment) => {
    if (!assignment || !assignment.due_date) return 'text-muted'
    if (isAssignmentOverdue(assignment)) return 'text-danger'
    const daysUntilDue = Math.ceil((new Date(assignment.due_date) - new Date()) / (1000 * 60 * 60 * 24))
    if (daysUntilDue <= 2) return 'text-warning'
    return 'text-dark'
}

/**
 * Get active/inactive status badge class
 * @param {boolean} isActive - Active status
 * @returns {string}
 */
export const getActiveBadgeClass = (isActive) => {
    return isActive ? 'bg-success' : 'bg-warning'
}

/**
 * Get active/inactive status text
 * @param {boolean} isActive - Active status
 * @returns {string}
 */
export const getActiveStatusText = (isActive) => {
    return isActive ? 'Active' : 'Inactive'
}

export default {
    getStatusBadgeClass,
    getAttendanceBadgeClass,
    getAttendanceIcon,
    getPriorityBadgeClass,
    getPriorityIcon,
    getAssessmentBadgeClass,
    getGradeBadgeClass,
    calculateLetterGrade,
    getProgressBarClass,
    getAttendanceColorClass,
    getAttendanceStatusLabel,
    formatAssessmentType,
    getHolidayBadgeClass,
    // Assignment helpers
    isAssignmentSubmitted,
    isAssignmentOverdue,
    getAssignmentStatusText,
    getAssignmentStatusColor,
    getAssignmentStatusBgClass,
    getAssignmentStatusIcon,
    getDueDateClass,
    // Active status helpers
    getActiveBadgeClass,
    getActiveStatusText
}
