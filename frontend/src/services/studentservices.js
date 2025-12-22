import api from './api'

export const studentService = {
  /**
   * Get all students with optional filters
   */
  async getAllStudents(params = {}) {
    try {
      const response = await api.get('/students/', { params })
      return response.data
    } catch (error) {
      console.error('Error fetching students:', error.response?.data || error.message)
      throw error
    }
  },

  /**
   * Get single student by ID
   */
  async getStudent(id) {
    try {
      const response = await api.get(`/students/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching student ${id}:`, error.response?.data || error.message)
      throw error
    }
  },

  /**
   * Create a new student
   */
  async createStudent(data) {
    try {
      const response = await api.post('/students/', data)
      return response.data
    } catch (error) {
      console.error('Error creating student:', error.response?.data || error.message)
      throw error
    }
  },

  /**
   * Update student
   */
  async updateStudent(id, data) {
    try {
      const response = await api.put(`/students/${id}/`, data)
      return response.data
    } catch (error) {
      console.error(`Error updating student ${id}:`, error.response?.data || error.message)
      throw error
    }
  },

  /**
   * Delete student
   */
  async deleteStudent(id) {
    try {
      const response = await api.delete(`/students/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Error deleting student ${id}:`, error.response?.data || error.message)
      throw error
    }
  },

  /**
   * Get enrolled subjects for a student
   */
  async getEnrolledSubjects(id) {
    try {
      const response = await api.get(`/students/${id}/enrolled_subjects/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching enrolled subjects for student ${id}:`, error.response?.data || error.message)
      throw error
    }
  },

  getStudentSubjects(id) {
    return this.getEnrolledSubjects(id)
  },

  /**
   * Get attendance for a student
   */
  async getAttendance(id) {
    try {
      const response = await api.get(`/students/${id}/attendance/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching attendance for student ${id}:`, error.response?.data || error.message)
      throw error
    }
  },

  /**
   * Get grades for a student
   */
  async getGrades(id) {
    try {
      const response = await api.get(`/students/${id}/grades/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching grades for student ${id}:`, error.response?.data || error.message)
      throw error
    }
  },

  /**
   * Toggle student active status
   */
  async toggleStatus(id) {
    try {
      // Get current student to check status
      const student = await this.getStudent(id)

      // Toggle based on current is_active status
      if (student.is_active) {
        const response = await api.post(`/students/${id}/deactivate/`)
        return response.data
      } else {
        const response = await api.post(`/students/${id}/activate/`)
        return response.data
      }
    } catch (error) {
      console.error(`Error toggling status for student ${id}:`, error.response?.data || error.message)
      throw error
    }
  }
}