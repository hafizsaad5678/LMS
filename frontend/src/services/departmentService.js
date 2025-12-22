import api from './api'

const ENDPOINT = '/departments'

export const departmentService = {
    // Get all departments
    getAllDepartments: async (params = {}) => {
        const response = await api.get(`${ENDPOINT}/`, { params })
        return response.data
    },

    // Get department by ID
    getDepartmentById: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Create new department
    createDepartment: async (departmentData) => {
        const response = await api.post(`${ENDPOINT}/`, departmentData)
        return response.data
    },

    // Update department
    updateDepartment: async (id, departmentData) => {
        const response = await api.put(`${ENDPOINT}/${id}/`, departmentData)
        return response.data
    },

    // Partial update department
    patchDepartment: async (id, partialData) => {
        const response = await api.patch(`${ENDPOINT}/${id}/`, partialData)
        return response.data
    },

    // Delete department
    deleteDepartment: async (id) => {
        const response = await api.delete(`${ENDPOINT}/${id}/`)
        return response.data
    },

    // Get department programs
    getDepartmentPrograms: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/programs/`)
        return response.data
    },

    // Get department teachers
    getDepartmentTeachers: async (id) => {
        const response = await api.get(`${ENDPOINT}/${id}/teachers/`)
        return response.data
    },

    // Toggle active status
    toggleStatus: async (id) => {
        const department = await departmentService.getDepartmentById(id)
        const response = await api.patch(`${ENDPOINT}/${id}/`, {
            is_active: !department.is_active
        })
        return response.data
    }
}

export default departmentService
