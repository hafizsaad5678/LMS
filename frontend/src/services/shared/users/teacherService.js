/**
 * Teacher Service - Refactored with unified API wrapper
 */
import api from '../core/api'
import { apiGet, apiPost, apiPut, apiPatch, apiDelete, handleRequest } from '../core/apiWrapper'

export const teacherService = {
    getAllTeachers: (params = {}) =>
        apiGet('/teachers/', params, 'fetching teachers'),

    getTeacher: (id) =>
        apiGet(`/teachers/${id}/`, null, `fetching teacher ${id}`),

    createTeacher: (data) =>
        apiPost('/teachers/', data, 'creating teacher'),

    updateTeacher: (id, data) =>
        apiPut(`/teachers/${id}/`, data, `updating teacher ${id}`),

    patchTeacher: (id, data) =>
        apiPatch(`/teachers/${id}/`, data, `patching teacher ${id}`),

    deleteTeacher: (id) =>
        apiDelete(`/teachers/${id}/`, `deleting teacher ${id}`),

    getActiveTeachers: () =>
        apiGet('/teachers/active/', null, 'fetching active teachers'),

    activateTeacher: (id) =>
        apiPost(`/teachers/${id}/activate/`, null, `activating teacher ${id}`),

    deactivateTeacher: (id) =>
        apiPost(`/teachers/${id}/deactivate/`, null, `deactivating teacher ${id}`),

    async toggleStatus(id) {
        const teacher = await teacherService.getTeacher(id)
        return teacher.is_active ? teacherService.deactivateTeacher(id) : teacherService.activateTeacher(id)
    },

    uploadProfileImage: (id, imageFile) => {
        const formData = new FormData()
        formData.append('profile_image', imageFile)
        return handleRequest(
            () => api.post(`/teachers/${id}/upload_profile/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            }),
            `uploading profile image for teacher ${id}`
        )
    },

    searchTeachers: (query) =>
        apiGet('/teachers/search/', { q: query }, 'searching teachers'),

    getTeacherSubjects: (id) =>
        apiGet(`/teachers/${id}/teaching_subjects/`, null, `fetching subjects for teacher ${id}`)
};


