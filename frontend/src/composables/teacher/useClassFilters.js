/**
 * Composable for Class/Subject Filtering
 * Provides reusable filtering logic for department, program, and subject selection
 */
import { ref, computed } from 'vue'
import teacherPanelService from '@/services/teacher/teacherPanelService'

export function useClassFilters() {
    const allClasses = ref([])
    const departments = ref([])
    const programs = ref([])
    const selectedDepartment = ref('')
    const selectedProgram = ref('')
    const selectedSubject = ref('')
    const loading = ref(false)

    /**
     * Filter subjects based on selected department and program
     */
    const filteredSubjects = computed(() => {
        return allClasses.value.filter(c => {
            let match = true
            if (selectedDepartment.value) {
                match = match && c.department_id === selectedDepartment.value
            }
            if (selectedProgram.value) {
                match = match && c.program_id === selectedProgram.value
            }
            return match
        }).map(s => ({
            id: s.subject_id,
            name: `${s.subject_name} (${s.subject_code})`
        }))
    })

    /**
     * Load all classes and extract unique departments and programs
     */
    const loadClasses = async () => {
        loading.value = true
        try {
            const res = await teacherPanelService.getMyClasses()
            allClasses.value = res.results || res || []

            // Extract unique departments
            const deptMap = new Map()
            allClasses.value.forEach(c => {
                const deptId = c.department_id || c.department
                if (deptId) {
                    deptMap.set(deptId, c.department_name || c.department)
                }
            })
            departments.value = Array.from(deptMap.entries()).map(([id, name]) => ({ id, name }))

            // Extract unique programs
            const progMap = new Map()
            allClasses.value.forEach(c => {
                const progId = c.program_id || c.program
                if (progId) {
                    progMap.set(progId, c.program_name || c.program)
                }
            })
            programs.value = Array.from(progMap.entries()).map(([id, name]) => ({ id, name }))

            return allClasses.value
        } catch (e) {
            console.error('Error loading classes:', e)
            return []
        } finally {
            loading.value = false
        }
    }

    /**
     * Reset all filters
     */
    const resetFilters = () => {
        selectedDepartment.value = ''
        selectedProgram.value = ''
        selectedSubject.value = ''
    }

    return {
        allClasses,
        departments,
        programs,
        selectedDepartment,
        selectedProgram,
        selectedSubject,
        filteredSubjects,
        loading,
        loadClasses,
        resetFilters
    }
}
