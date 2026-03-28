import api from '../core/api'

const ENDPOINT = '/semesters'

export const semesterService = {
    // Get all semesters
    getAll: async (params = {}) => {
        const response = await api.get(`${ENDPOINT}/`, { params })
        return response.data
    },

    // Get semester by ID
    getById: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Create new semester
    create: async (data) => {
        const response = await api.post(`${ENDPOINT}/`, data)
        return response.data
    },

    // Bulk create semesters
    bulkCreate: async (semesters) => {
        const response = await api.post(`${ENDPOINT}/bulk_create/`, { semesters })
        return response.data
    },

    // Update semester
    update: async (id, data) => {
        const response = await api.put(`${ENDPOINT}/${id}/`, data)
        return response.data
    },

    // Delete semester
    delete: async (id) => {
        const response = await api.delete(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Get semester subjects
    getSubjects: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/subjects/`)
        return response.data
    },

    // Activate semester (change status to active)
    activate: async (id) => {
        const response = await api.patch(`${ENDPOINT}/${id}/`, { status: 'active' })
        return response.data
    }
}

export default semesterService


