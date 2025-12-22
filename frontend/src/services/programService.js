import api from './api'

const ENDPOINT = '/programs'

export const programService = {
    // Get all programs (courses)
    getAllPrograms: async (params = {}) => {
        const response = await api.get(`${ENDPOINT}/`, { params })
        return response.data
    },

    // Get program by ID
    getProgramById: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Create new program
    createProgram: async (programData) => {
        const response = await api.post(`${ENDPOINT}/`, programData)
        return response.data
    },

    // Update program
    updateProgram: async (id, programData) => {
        const response = await api.put(`${ENDPOINT}/${id}/`, programData)
        return response.data
    },

    // Partial update program
    patchProgram: async (id, partialData) => {
        const response = await api.patch(`${ENDPOINT}/${id}/`, partialData)
        return response.data
    },

    // Delete program
    deleteProgram: async (id) => {
        const response = await api.delete(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Get program semesters
    getProgramSemesters: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/semesters/`)
        return response.data
    },

    // Get program students
    getProgramStudents: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/students/`)
        return response.data
    }
}

// Alias for course
export const courseService = programService

export default programService
