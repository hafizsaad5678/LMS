/**
 * Composable for Grade Management
 * Provides reusable grade calculation and management logic
 */
import { ref, computed } from 'vue'
import teacherPanelService from '@/services/teacher/teacherPanelService'

export function useGradeManagement() {
    const components = ref([])
    const loading = ref(false)
    const error = ref(null)

    /**
     * Calculate letter grade from percentage
     */
    const calculateGrade = (percentage) => {
        if (percentage >= 90) return 'A+'
        if (percentage >= 85) return 'A'
        if (percentage >= 80) return 'A-'
        if (percentage >= 75) return 'B+'
        if (percentage >= 70) return 'B'
        if (percentage >= 65) return 'B-'
        if (percentage >= 60) return 'C+'
        if (percentage >= 55) return 'C'
        if (percentage >= 50) return 'C-'
        if (percentage >= 40) return 'D'
        return 'F'
    }

    /**
     * Get grade color class
     */
    const getGradeColor = (grade) => {
        if (grade.includes('A')) return 'bg-success'
        if (grade.includes('B')) return 'bg-info'
        if (grade.includes('C')) return 'bg-warning'
        return 'bg-danger'
    }

    /**
     * Get grade badge class
     */
    const getGradeBadge = (grade) => {
        if (grade.startsWith('A')) return 'bg-success-light text-success'
        if (grade.startsWith('B')) return 'bg-info-light text-info'
        if (grade.startsWith('C')) return 'bg-warning-light text-warning'
        return 'bg-danger-light text-danger'
    }

    /**
     * Calculate progress percentage
     */
    const getProgressPercentage = (studentsGraded, totalStudents) => {
        if (!totalStudents) return 0
        return Math.round((studentsGraded / totalStudents) * 100)
    }

    /**
     * Load grade components for a subject
     */
    const loadComponents = async (subjectId) => {
        loading.value = true
        error.value = null
        try {
            const params = subjectId ? { subject: subjectId } : {}
            const res = await teacherPanelService.getComponents(params)
            components.value = res.results || res || []
            return components.value
        } catch (e) {
            error.value = e.message
            console.error('Error loading components:', e)
            return []
        } finally {
            loading.value = false
        }
    }

    /**
     * Create a new grade component
     */
    const createComponent = async (componentData) => {
        try {
            const result = await teacherPanelService.createComponent(componentData)
            return { success: true, data: result }
        } catch (e) {
            return { success: false, error: e.message }
        }
    }

    /**
     * Update a grade component
     */
    const updateComponent = async (componentId, componentData) => {
        try {
            const result = await teacherPanelService.updateComponent(componentId, componentData)
            return { success: true, data: result }
        } catch (e) {
            return { success: false, error: e.message }
        }
    }

    /**
     * Delete a grade component
     */
    const deleteComponent = async (componentId) => {
        try {
            await teacherPanelService.deleteComponent(componentId)
            return { success: true }
        } catch (e) {
            return { success: false, error: e.message }
        }
    }

    return {
        components,
        loading,
        error,
        calculateGrade,
        getGradeColor,
        getGradeBadge,
        getProgressPercentage,
        loadComponents,
        createComponent,
        updateComponent,
        deleteComponent
    }
}
