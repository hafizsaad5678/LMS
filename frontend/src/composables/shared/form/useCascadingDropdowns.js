/**
 * Cascading Dropdowns Composable
 * Handles Department → Program → Semester cascading selection
 */
import { ref, computed } from 'vue'
import { api, cacheService } from '@/services/shared'


export const useCascadingDropdowns = (options = {}) => {
    const { cacheEnabled = true } = options

    // State
    const departments = ref([])
    const programs = ref([])
    const semesters = ref([])
    const sessions = ref([])
    const institutions = ref([])

    const selectedDepartment = ref('')
    const selectedProgram = ref('')
    const selectedSemester = ref('')

    const loadingDepartments = ref(false)
    const loadingPrograms = ref(false)
    const loadingSemesters = ref(false)
    const loadingSessions = ref(false)
    const loadingInstitutions = ref(false)

    // Computed filtered programs based on department
    const filteredPrograms = computed(() => {
        if (!selectedDepartment.value) return programs.value
        return programs.value.filter(p =>
            String(p.department) === String(selectedDepartment.value) ||
            p.department?.id === selectedDepartment.value
        )
    })

    // Helper to normalize API response
    const normalize = (data) => Array.isArray(data) ? data : (data?.results || [])
    const activeOnly = (items) => normalize(items).filter(item => item?.is_active !== false)

    // Load Institutions
    const loadInstitutions = async () => {
        if (cacheEnabled) {
            const cached = cacheService.get('institutions_dropdown')
            if (cached) {
                institutions.value = activeOnly(cached)
                return institutions.value
            }
        }
        loadingInstitutions.value = true
        try {
            const response = await api.get('/institutions/', { params: { is_active: true } })
            institutions.value = activeOnly(response.data)
            if (cacheEnabled) cacheService.set('institutions_dropdown', institutions.value)
            return institutions.value
        } catch (error) {
            console.error('Error loading institutions:', error)
            return []
        } finally {
            loadingInstitutions.value = false
        }
    }

    // Load Departments
    const loadDepartments = async () => {
        if (cacheEnabled) {
            const cached = cacheService.get('departments_dropdown')
            if (cached) {
                departments.value = activeOnly(cached)
                return departments.value
            }
        }
        loadingDepartments.value = true
        try {
            const response = await api.get('/departments/', { params: { is_active: true } })
            departments.value = activeOnly(response.data)
            if (cacheEnabled) cacheService.set('departments_dropdown', departments.value)
            return departments.value
        } catch (error) {
            console.error('Error loading departments:', error)
            return []
        } finally {
            loadingDepartments.value = false
        }
    }

    // Load Programs
    const loadPrograms = async () => {
        if (cacheEnabled) {
            const cached = cacheService.get('programs_dropdown')
            if (cached) {
                programs.value = activeOnly(cached)
                return programs.value
            }
        }
        loadingPrograms.value = true
        try {
            const response = await api.get('/programs/', { params: { is_active: true } })
            programs.value = activeOnly(response.data)
            if (cacheEnabled) cacheService.set('programs_dropdown', programs.value)
            return programs.value
        } catch (error) {
            console.error('Error loading programs:', error)
            return []
        } finally {
            loadingPrograms.value = false
        }
    }

    // Load Semesters for a specific program
    const loadSemesters = async (programId) => {
        if (!programId) { semesters.value = []; return [] }
        loadingSemesters.value = true
        try {
            const response = await api.get(`/programs/${programId}/semesters/`)
            semesters.value = normalize(response.data)
            return semesters.value
        } catch (error) {
            // Fallback to filtered query
            try {
                const res = await api.get('/semesters/', { params: { program: programId } })
                semesters.value = normalize(res.data)
                return semesters.value
            } catch (e) {
                console.error('Error loading semesters:', e)
                return []
            }
        } finally {
            loadingSemesters.value = false
        }
    }

    // Load Sessions
    const loadSessions = async (programId = null) => {
        if (cacheEnabled && !programId) {
            const cached = cacheService.get('sessions_dropdown')
            if (cached) {
                sessions.value = activeOnly(cached)
                return sessions.value
            }
        }
        loadingSessions.value = true
        try {
            const params = programId ? { program: programId, is_active: true } : { is_active: true }
            const response = await api.get('/academic-sessions/', { params })
            sessions.value = activeOnly(response.data)
            if (cacheEnabled && !programId) cacheService.set('sessions_dropdown', sessions.value)
            return sessions.value
        } catch (error) {
            console.error('Error loading sessions:', error)
            return []
        } finally {
            loadingSessions.value = false
        }
    }

    // Handle department change
    const onDepartmentChange = (deptId) => {
        selectedDepartment.value = deptId
        selectedProgram.value = ''
        selectedSemester.value = ''
        semesters.value = []
    }

    // Handle program change
    const onProgramChange = async (progId) => {
        selectedProgram.value = progId
        selectedSemester.value = ''
        if (progId) {
            await loadSemesters(progId)
        } else {
            semesters.value = []
        }
    }

    // Load all dropdowns at once
    const loadAllDropdowns = async () => {
        await Promise.all([
            loadDepartments(),
            loadPrograms(),
            loadSessions()
        ])
    }

    // Set initial values (for edit mode)
    const setInitialValues = async (dept, prog, sem) => {
        if (dept) selectedDepartment.value = String(dept)
        if (prog) {
            selectedProgram.value = String(prog)
            await loadSemesters(prog)
        }
        if (sem) selectedSemester.value = String(sem)
    }

    // Clear dropdown caches
    const clearCaches = () => {
        cacheService.clear('departments_dropdown')
        cacheService.clear('programs_dropdown')
        cacheService.clear('sessions_dropdown')
        cacheService.clear('institutions_dropdown')
    }

    return {
        // Data
        departments,
        programs,
        semesters,
        sessions,
        institutions,
        filteredPrograms,

        // Selected values
        selectedDepartment,
        selectedProgram,
        selectedSemester,

        // Loading states
        loadingDepartments,
        loadingPrograms,
        loadingSemesters,
        loadingSessions,
        loadingInstitutions,

        // Methods
        loadInstitutions,
        loadDepartments,
        loadPrograms,
        loadSemesters,
        loadSessions,
        loadAllDropdowns,
        onDepartmentChange,
        onProgramChange,
        setInitialValues,
        clearCaches
    }
}

export default useCascadingDropdowns
