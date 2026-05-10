/**
 * Composable for loading teacher classes and building subject/program options.
 */
import { computed, unref } from 'vue'
import { useCachedData, useFilterOptions } from '@/composables/shared'
import teacherPanelService from '@/services/teacher/teacherPanelService'

const toArray = (value) => (Array.isArray(value) ? value : [])

export function useTeacherSubjectOptions(options = {}) {
    const {
        includeOther = false,
        maxOptions = 100,
        programFilter = null,
        cacheKey = 'teacher_subjects_list'
    } = options

    const { data, load, loading, error } = useCachedData(
        cacheKey,
        async () => {
            const response = await teacherPanelService.getMyClasses()
            return response.results || response || []
        },
        { initialLoading: false }
    )

    const subjects = computed(() => toArray(data.value))

    const filteredSubjects = computed(() => {
        const programName = String(unref(programFilter) || '').trim()
        if (!programName) return subjects.value
        return subjects.value.filter(subject => String(subject.program_name || '') === programName)
    })

    const { createObjectOptions: createSubjectOptions } = useFilterOptions(filteredSubjects)
    const baseSubjectOptions = createSubjectOptions({
        value: (item) => `${item.subject_id || item.id}`,
        label: (item) => `${item.subject_name} (${item.subject_code})`,
        uniqueBy: (item) => item.subject_id || item.id
    })

    const subjectOptions = computed(() => {
        const limited = baseSubjectOptions.value.slice(0, maxOptions)
        if (!includeOther) return limited
        return [...limited, { value: 'other', label: 'Other' }]
    })

    const { createObjectOptions: createProgramOptions } = useFilterOptions(subjects)
    const baseProgramOptions = createProgramOptions({
        value: 'program_name',
        label: 'program_name',
        uniqueBy: 'program_name'
    })

    const programOptions = computed(() => baseProgramOptions.value.slice(0, maxOptions))

    return {
        subjects,
        subjectOptions,
        programOptions,
        loadSubjects: load,
        subjectsLoading: loading,
        subjectsError: error
    }
}
