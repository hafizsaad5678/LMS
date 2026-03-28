/**
 * Composables Index
 * Export all reusable composables organized by purpose
 */

// Data Fetching & Lists
export { useEntityList } from './data/useEntityList'
export { useEntityDelete } from './data/useEntityDelete'
export { usePagination } from './data/usePagination'
export { useAsyncState } from './data/useAsyncState'
export { useCachedData, useCachedDataMultiple } from './data/useCachedData'
export { useCrudModal } from './data/useCrudModal'
export { useProfileLoader } from './data/useProfileLoader'

// Form Logic & Validation
export { useEntityForm } from './form/useEntityForm'
export { useCascadingDropdowns } from './form/useCascadingDropdowns'
export { useNavigateAfterDelay, useAlert, createForm, resetForm, FORM_DEFAULTS, useFormSubmit } from './form/useFormHelpers'

// Domain Specific Logic
export { useStudentId } from './domain/useStudentId'
export {
    enrollStudentInSubjects,
    assignSubjectsToTeacher,
    syncTeacherSubjects,
    getStudentEnrolledSubjectIds,
    getTeacherSubjectIds
} from './domain/useSubjectEnrollment'
