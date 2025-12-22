import api from './api'

const ENDPOINT = '/assignments'

export const assignmentService = {
    // Get all assignments
    getAllAssignments: async (params = {}) => {
        const response = await api.get(`${ENDPOINT}/`, { params })
        return response.data
    },

    // Get assignment by ID
    getAssignmentById: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Create new assignment
    createAssignment: async (assignmentData) => {
        const response = await api.post(`${ENDPOINT}/`, assignmentData)
        return response.data
    },

    // Update assignment
    updateAssignment: async (id, assignmentData) => {
        const response = await api.put(`${ENDPOINT}/${id}/`, assignmentData)
        return response.data
    },

    // Partial update assignment
    patchAssignment: async (id, partialData) => {
        const response = await api.patch(`${ENDPOINT}/${id}/`, partialData)
        return response.data
    },

    // Delete assignment
    deleteAssignment: async (id) => {
        const response = await api.delete(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Get assignment submissions
    getSubmissions: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/submissions/`)
        return response.data
    }
}

export default assignmentService
