import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export const teacherService = {
    /**
     * Get all teachers with optional filters
     * @param {Object} params - Query parameters for filtering
     * @returns {Promise<Object>} List of teachers
     */
    async getAllTeachers(params = {}) {
        try {
            const response = await apiClient.get('/teachers/', { params });
            return response.data;
        } catch (error) {
            console.error('Error fetching teachers:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Get single teacher by ID
     * @param {string|number} id - Teacher ID
     * @returns {Promise<Object>} Teacher details
     */
    async getTeacher(id) {
        try {
            const response = await apiClient.get(`/teachers/${id}/`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Create a new teacher
     * @param {Object} data - Teacher data
     * @returns {Promise<Object>} Created teacher
     */
    async createTeacher(data) {
        try {
            const response = await apiClient.post('/teachers/', data);
            return response.data;
        } catch (error) {
            console.error('Error creating teacher:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Update teacher (full update)
     * @param {string|number} id - Teacher ID
     * @param {Object} data - Complete teacher data
     * @returns {Promise<Object>} Updated teacher
     */
    async updateTeacher(id, data) {
        try {
            const response = await apiClient.put(`/teachers/${id}/`, data);
            return response.data;
        } catch (error) {
            console.error(`Error updating teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Partial update teacher
     * @param {string|number} id - Teacher ID
     * @param {Object} data - Partial teacher data
     * @returns {Promise<Object>} Updated teacher
     */
    async patchTeacher(id, data) {
        try {
            const response = await apiClient.patch(`/teachers/${id}/`, data);
            return response.data;
        } catch (error) {
            console.error(`Error patching teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Delete teacher
     * @param {string|number} id - Teacher ID
     * @returns {Promise<void>}
     */
    async deleteTeacher(id) {
        try {
            const response = await apiClient.delete(`/teachers/${id}/`);
            return response.data;
        } catch (error) {
            console.error(`Error deleting teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Get only active teachers
     * @returns {Promise<Object>} List of active teachers
     */
    async getActiveTeachers() {
        try {
            const response = await apiClient.get('/teachers/active/');
            return response.data;
        } catch (error) {
            console.error('Error fetching active teachers:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Activate a teacher
     * @param {string|number} id - Teacher ID
     * @returns {Promise<Object>} Updated teacher
     */
    async activateTeacher(id) {
        try {
            const response = await apiClient.post(`/teachers/${id}/activate/`);
            return response.data;
        } catch (error) {
            console.error(`Error activating teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Deactivate a teacher
     * @param {string|number} id - Teacher ID
     * @returns {Promise<Object>} Updated teacher
     */
    async deactivateTeacher(id) {
        try {
            const response = await apiClient.post(`/teachers/${id}/deactivate/`);
            return response.data;
        } catch (error) {
            console.error(`Error deactivating teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Toggle teacher status (activate/deactivate)
     * @param {string|number} id - Teacher ID
     * @returns {Promise<Object>} Updated teacher with new status
     */
    async toggleStatus(id) {
        try {
            // First, get the current teacher status
            const teacher = await this.getTeacher(id);

            // Toggle based on current is_active status
            if (teacher.is_active) {
                return await this.deactivateTeacher(id);
            } else {
                return await this.activateTeacher(id);
            }
        } catch (error) {
            console.error(`Error toggling status for teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Upload profile image for teacher
     * @param {string|number} id - Teacher ID
     * @param {File} imageFile - Image file to upload
     * @returns {Promise<Object>} Updated teacher with new profile image
     */
    async uploadProfileImage(id, imageFile) {
        try {
            const formData = new FormData();
            formData.append('profile_image', imageFile);

            const response = await apiClient.post(`/teachers/${id}/upload_profile/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            return response.data;
        } catch (error) {
            console.error(`Error uploading profile image for teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Search teachers by query
     * @param {string} query - Search query
     * @returns {Promise<Object>} Search results
     */
    async searchTeachers(query) {
        try {
            const response = await apiClient.get('/teachers/search/', { params: { q: query } });
            return response.data;
        } catch (error) {
            console.error('Error searching teachers:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Get subjects assigned to a teacher
     * @param {string|number} id - Teacher ID
     * @returns {Promise<Array>} List of assigned subjects
     */
    async getTeacherSubjects(id) {
        try {
            const response = await apiClient.get(`/teachers/${id}/teaching_subjects/`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching subjects for teacher ${id}:`, error.response?.data || error.message);
            throw error;
        }
    },
};
