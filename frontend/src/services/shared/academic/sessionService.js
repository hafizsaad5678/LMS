import api from '../core/api'

/**
 * Academic Session/Batch Management Service
 * Provides methods for managing academic sessions
 * 
 * NOTE: All methods return response.data for consistency with other services
 */
export default {
    // ==================== BASIC CRUD ====================

    /**
     * Get all sessions with optional filters
     * @param {Object} params - Query parameters (program, start_year, status, etc.)
     * @returns {Promise<Object>}
     */
    async getSessions(params = {}) {
        const response = await api.get('/academic-sessions/', { params })
        return response.data
    },

    /**
     * Get a single session by ID
     * @param {String} id - Session UUID
     * @returns {Promise<Object>}
     */
    async getSession(id) {
        const response = await api.get(`/academic-sessions/${id}/`)
        return response.data
    },

    /**
     * Create a new academic session
     * @param {Object} data - Session data
     * @returns {Promise<Object>}
     */
    async createSession(data) {
        const response = await api.post('/academic-sessions/', data)
        return response.data
    },

    /**
     * Update an existing session
     * @param {String} id - Session UUID
     * @param {Object} data - Updated session data
     * @returns {Promise<Object>}
     */
    async updateSession(id, data) {
        const response = await api.patch(`/academic-sessions/${id}/`, data)
        return response.data
    },

    /**
     * Delete a session
     * @param {String} id - Session UUID
     * @returns {Promise<Object>}
     */
    async deleteSession(id) {
        const response = await api.delete(`/academic-sessions/${id}/`)
        return response.data
    },

    // ==================== SESSION-SPECIFIC ACTIONS ====================

    /**
     * Get all semesters for a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise<Object>}
     */
    async getSessionSemesters(sessionId) {
        const response = await api.get(`/academic-sessions/${sessionId}/semesters/`)
        return response.data
    },

    /**
     * Get all students enrolled in a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise<Object>}
     */
    async getSessionStudents(sessionId) {
        const response = await api.get(`/academic-sessions/${sessionId}/students/`)
        return response.data
    },

    /**
     * Auto-create semesters for a session based on program type
     * @param {String} sessionId - Session UUID
     * @returns {Promise<Object>}
     */
    async setupSemesters(sessionId) {
        const response = await api.post(`/academic-sessions/${sessionId}/setup_semesters/`)
        return response.data
    },

    /**
     * Get all active sessions
     * @returns {Promise<Object>}
     */
    async getActiveSessions() {
        const response = await api.get('/academic-sessions/active_sessions/')
        return response.data
    },

    /**
     * Get all upcoming sessions
     * @returns {Promise<Object>}
     */
    async getUpcomingSessions() {
        const response = await api.get('/academic-sessions/upcoming_sessions/')
        return response.data
    },

    /**
     * Get sessions filtered by program
     * @param {String} programId - Program UUID
     * @returns {Promise<Object>}
     */
    async getSessionsByProgram(programId) {
        const response = await api.get('/academic-sessions/program_sessions/', {
            params: { program: programId }
        })
        return response.data
    },

    /**
     * Get detailed statistics for a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise<Object>}
     */
    async getSessionStatistics(sessionId) {
        const response = await api.get(`/academic-sessions/${sessionId}/statistics/`)
        return response.data
    },

    // ==================== SESSION LIFECYCLE ====================

    /**
     * Activate a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise<Object>}
     */
    async activateSession(sessionId) {
        const response = await api.post(`/academic-sessions/${sessionId}/activate/`)
        return response.data
    },

    /**
     * Mark a session as completed
     * @param {String} sessionId - Session UUID
     * @returns {Promise<Object>}
     */
    async completeSession(sessionId) {
        const response = await api.post(`/academic-sessions/${sessionId}/complete/`)
        return response.data
    },

    /**
     * Archive a session
     * @param {String} sessionId - Session UUID
     * @returns {Promise<Object>}
     */
    async archiveSession(sessionId) {
        const response = await api.post(`/academic-sessions/${sessionId}/archive/`)
        return response.data
    },

    // ==================== UTILITY METHODS ====================

    /**
     * Get available program levels
     * @returns {Promise<Object>}
     */
    async getProgramLevels() {
        const response = await api.get('/academic-sessions/program_levels/')
        return response.data
    }
}


