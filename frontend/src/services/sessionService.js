import api from './api'

/**
 * Academic Session/Batch Management Service
 * Provides methods for managing academic sessions
 */
export default {
    // ==================== BASIC CRUD ====================

    /**
     * Get all sessions with optional filters
     * @param {Object} params - Query parameters (program, start_year, status, etc.)
     * @returns {Promise}
     */
    getSessions(params = {}) {
        return api.get('/academic-sessions/', { params })
    },

    /**
     * Get a single session by ID
     * @param {String} id - Session UUID
     * @returns {Promise}
     */
    getSession(id) {
        return api.get(`/academic-sessions/${id}/`)
    },

    /**
     * Create a new academic session
     * @param {Object} data - Session data
     * @returns {Promise}
     */
    createSession(data) {
        return api.post('/academic-sessions/', data)
    },

    /**
     * Update an existing session
     * @param {String} id - Session UUID
     * @param {Object} data - Updated session data
     * @returns {Promise}
     */
    updateSession(id, data) {
        return api.patch(`/academic-sessions/${id}/`, data)
    },

    /**
     * Delete a session
     * @param {String} id - Session UUID
     * @returns {Promise}
     */
    deleteSession(id) {
        return api.delete(`/academic-sessions/${id}/`)
    },

    // ==================== SESSION-SPECIFIC ACTIONS ====================

    /**
     * Get all semesters for a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise}
     */
    getSessionSemesters(sessionId) {
        return api.get(`/academic-sessions/${sessionId}/semesters/`)
    },

    /**
     * Get all students enrolled in a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise}
     */
    getSessionStudents(sessionId) {
        return api.get(`/academic-sessions/${sessionId}/students/`)
    },

    /**
     * Auto-create semesters for a session based on program type
     * This is a powerful feature that creates all semesters in one call!
     * @param {String} sessionId - Session UUID
     * @returns {Promise}
     */
    setupSemesters(sessionId) {
        return api.post(`/academic-sessions/${sessionId}/setup_semesters/`)
    },

    /**
     * Get all active sessions
     * @returns {Promise}
     */
    getActiveSessions() {
        return api.get('/academic-sessions/active_sessions/')
    },

    /**
     * Get all upcoming sessions
     * @returns {Promise}
     */
    getUpcomingSessions() {
        return api.get('/academic-sessions/upcoming_sessions/')
    },

    /**
     * Get sessions filtered by program
     * @param {String} programId - Program UUID
     * @returns {Promise}
     */
    getSessionsByProgram(programId) {
        return api.get('/academic-sessions/program_sessions/', {
            params: { program: programId }
        })
    },

    /**
     * Get detailed statistics for a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise}
     */
    getSessionStatistics(sessionId) {
        return api.get(`/academic-sessions/${sessionId}/statistics/`)
    },

    // ==================== SESSION LIFECYCLE ====================

    /**
     * Activate a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise}
     */
    activateSession(sessionId) {
        return api.post(`/academic-sessions/${sessionId}/activate/`)
    },

    /**
     * Mark a session as completed
     * @param {String} sessionId - Session UUID
     * @returns {Promise}
     */
    completeSession(sessionId) {
        return api.post(`/academic-sessions/${sessionId}/complete/`)
    },

    /**
     * Archive a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise}
     */
    archiveSession(sessionId) {
        return api.post(`/academic-sessions/${sessionId}/archive/`)
    },

    // ==================== UTILITY METHODS ====================

    /**
     * Get available program levels
     * @returns {Promise}
     */
    getProgramLevels() {
        return api.get('/academic-sessions/program_levels/')
    }
}
