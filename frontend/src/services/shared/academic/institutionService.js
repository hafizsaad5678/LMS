import api from '../core/api'

export const institutionService = {
    /**
     * Get all institutions with optional filters
     */
    async getAllInstitutions(params = {}) {
        try {
            const response = await api.get('/institutions/', { params })
            return response.data
        } catch (error) {
            console.error('Error fetching institutions:', error.response?.data || error.message)
            throw error
        }
    },

    /**
     * Get single institution by ID
     */
    async getInstitutionById(id) {
        try {
            const response = await api.get(`/institutions/${id}/`)
            return response.data
        } catch (error) {
            console.error(`Error fetching institution ${id}:`, error.response?.data || error.message)
            throw error
        }
    },

    /**
     * Create a new institution
     */
    async createInstitution(data) {
        try {
            const response = await api.post('/institutions/', data)
            return response.data
        } catch (error) {
            console.error('Error creating institution:', error.response?.data || error.message)
            throw error
        }
    },

    /**
     * Update institution
     */
    async updateInstitution(id, data) {
        try {
            const response = await api.put(`/institutions/${id}/`, data)
            return response.data
        } catch (error) {
            console.error(`Error updating institution ${id}:`, error.response?.data || error.message)
            throw error
        }
    },

    /**
     * Delete institution
     */
    async deleteInstitution(id) {
        try {
            const response = await api.delete(`/institutions/${id}/`)
            return response.data
        } catch (error) {
            console.error(`Error deleting institution ${id}:`, error.response?.data || error.message)
            throw error
        }
    },

    /**
     * Get departments for an institution
     */
    async getDepartments(id) {
        try {
            const response = await api.get(`/institutions/${id}/departments/`)
            return response.data
        } catch (error) {
            console.error(`Error fetching departments for institution ${id}:`, error.response?.data || error.message)
            throw error
        }
    },

    /**
     * Get institution statistics
     */
    async getStatistics(id) {
        try {
            const response = await api.get(`/institutions/${id}/statistics/`)
            return response.data
        } catch (error) {
            console.error(`Error fetching statistics for institution ${id}:`, error.response?.data || error.message)
            throw error
        }
    },

    /**
     * Toggle active status
     */
    async toggleActive(id) {
        try {
            const response = await api.post(`/institutions/${id}/toggle_active/`)
            return response.data
        } catch (error) {
            console.error(`Error toggling institution ${id}:`, error.response?.data || error.message)
            throw error
        }
    }
}


