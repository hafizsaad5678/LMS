import api from './api'

const ENDPOINT = '/subjects'

export const subjectService = {
    // Get all subjects
    getAllSubjects: async (params = {}) => {
        const response = await api.get(`${ENDPOINT}/`, { params })
        return response.data
    },

    // Get subject by ID
    getSubjectById: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Create new subject
    createSubject: async (subjectData) => {
        const response = await api.post(`${ENDPOINT}/`, subjectData)
        return response.data
    },

    // Update subject
    updateSubject: async (id, subjectData) => {
        const response = await api.put(`${ENDPOINT}/${id}/`, subjectData)
        return response.data
    },

    // Partial update subject
    patchSubject: async (id, partialData) => {
        const response = await api.patch(`${ENDPOINT}/${id}/`, partialData)
        return response.data
    },

    // Delete subject
    deleteSubject: async (id) => {
        const response = await api.delete(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Get subject assignments
    getSubjectAssignments: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/assignments/`)
        return response.data
    },

    // Get enrolled students
    getEnrolledStudents: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/enrolled_students/`)
        return response.data
    },

    // Get assigned teachers
    getAssignedTeachers: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/assigned_teachers/`)
        return response.data
    },

    // Get attendance
    getSubjectAttendance: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/attendance/`)
        return response.data
    }
}

export default subjectService
