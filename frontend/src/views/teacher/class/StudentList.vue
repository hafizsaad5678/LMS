<template>
  <TeacherPageTemplate title="My Students" subtitle="View and manage students in your classes" icon="bi bi-people"
    :breadcrumbs="breadcrumbs" :actions="actions">
    <template #stats>
      <div class="row g-3 g-lg-4 mb-4">
        <div v-for="stat in statsCards" :key="stat.title" class="col-6 col-md-3">
          <StatCard v-bind="stat" />
        </div>
      </div>
    </template>

    <template #filters>
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-center">
            <div class="col-md-5">
              <SelectInput v-model="filters.subject" :options="subjectOptions" placeholder="All Subjects"
                :no-margin="true" />
            </div>
            <div class="col-md-4">
              <SelectInput v-model="filters.program" :options="programOptions" placeholder="All Programs"
                :no-margin="true" />
            </div>
            <div class="col-md-3 text-end d-flex justify-content-md-end gap-2">
              <button @click="loadStudents(true)" class="btn btn-teacher-outline flex-fill flex-md-grow-0"><i
                  class="bi bi-arrow-clockwise me-1"></i>Refresh</button>
              <button @click="resetFilters" class="btn btn-outline-secondary flex-fill flex-md-grow-0"><i
                  class="bi bi-x-circle me-1"></i>Reset</button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <LoadingSpinner v-if="loading" message="Loading students..." />

    <div v-else-if="error" class="text-center py-5">
      <AlertMessage type="error" :message="error" title="Unable to Load Students" />
      <button @click="loadStudents()" class="btn btn-teacher-primary mt-3"><i class="bi bi-arrow-clockwise me-2"></i>Try
        Again</button>
    </div>

    <EmptyState v-else-if="filteredStudents.length === 0" icon="bi bi-people" title="No Students Found" :message="noStudentsMessage">
      <button v-if="hasActiveFilters" @click="resetFilters" class="btn btn-teacher-outline"><i class="bi bi-x-circle me-2"></i>Clear Filters</button>
    </EmptyState>

    <div v-else class="row g-4">
      <div v-for="student in filteredStudents" :key="student.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-card">
          <div class="card-body">
            <div class="d-flex align-items-start mb-3">
              <div class="avatar-circle avatar-circle-teacher me-3">
                <span class="fw-bold text-teacher">{{ student.name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="flex-grow-1">
                <h6 class="fw-bold mb-1">{{ student.name }}</h6>
                <p class="text-muted small mb-1">{{ student.roll_no }}</p>
                <p class="text-muted small mb-0">{{ student.email }}</p>
              </div>
            </div>
            <div class="mb-3">
              <div class="d-flex align-items-center gap-2 mb-1"><i class="bi bi-building text-muted small"></i><small
                  class="text-muted">{{ student.department_name }}</small></div>
              <div class="d-flex align-items-center gap-2 mb-1"><i class="bi bi-mortarboard text-muted small"></i><small
                  class="text-muted">{{ student.program_name }}</small></div>
              <div class="d-flex align-items-center gap-2 mb-1"><i class="bi bi-book text-muted small"></i><small
                  class="text-muted">{{ getSubjectSummary(student) }}</small></div>
            </div>
            <div class="d-flex gap-2">
              <button @click="router.push({ name: TEACHER_ROUTES.STUDENT_PROFILE.name, params: { id: student.id } })"
                class="btn btn-sm btn-teacher-primary flex-grow-1"><i class="bi bi-eye me-1"></i>View Profile</button>
              <button
                @click="router.push({ name: TEACHER_ROUTES.MARK_ATTENDANCE.name, query: { student: student.id, class: student.class_ids?.[0] || student.class_id } })"
                class="btn btn-sm btn-teacher-outline"><i class="bi bi-calendar-check"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { smartSearch } from '@/utils'
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { StatCard, AlertMessage, SelectInput, LoadingSpinner, EmptyState } from '@/components/shared/common'
import { useTeacherSubjectOptions } from '@/composables/teacher/useTeacherSubjectOptions'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { cacheService } from '@/services/shared'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const CACHE_KEY_PREFIX = 'teacher_students'
const router = useRouter()
const route = useRoute()

const breadcrumbs = [{ name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path }, { name: 'Students' }]
const actions = [{ label: 'Back to Classes', icon: 'bi bi-arrow-left', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.CLASS_LIST.name }) }]

const loading = ref(false)
const filters = ref({ subject: '', program: '', search: '' })
const students = ref([])
const error = ref(null)

const { subjectOptions, programOptions, loadSubjects } = useTeacherSubjectOptions({
  programFilter: computed(() => filters.value.program)
})

onMounted(() => {
  if (route.query.subject) filters.value.subject = route.query.subject
  if (route.query.search) filters.value.search = String(route.query.search)
  loadSubjects()
})

const hasActiveFilters = computed(() => filters.value.subject || filters.value.program || filters.value.search)

const noStudentsMessage = computed(() => {
  return hasActiveFilters.value
    ? 'No students match your filter criteria.'
    : 'No students enrolled in your subjects yet.'
})

const filteredStudents = computed(() => {
  // Note: Complex nested dropdowns and array fields (subject_ids, session_ids) require manual filtering. 
  // useFilterLogic omitted to preserve core features. smartSearch used cleanly.
  return students.value.filter(s => {
    if (filters.value.search) {
      const searchFields = ['name', 'email', 'roll_no', 'enrollment_number', 'program_name', 'department_name']
      if (!smartSearch(s, filters.value.search, searchFields)) return false
    }
    if (filters.value.subject) {
      const subjectIds = Array.isArray(s.subject_ids) ? s.subject_ids : [s.subject_id]
      if (!subjectIds.filter(Boolean).some(id => `${id}` === `${filters.value.subject}`)) return false
    }
    if (filters.value.program && s.program_name !== filters.value.program) return false
    return true
  })
})

const filteredUniqueSubjects = computed(() => {
  const seen = new Set()
  const subjectList = []

  filteredStudents.value.forEach(student => {
    const subjectsForStudent = Array.isArray(student.subjects)
      ? student.subjects
      : (student.subject_id ? [{ id: student.subject_id, name: student.subject_name, code: student.subject_code }] : [])

    subjectsForStudent.forEach(subject => {
      if (!subject?.id || seen.has(subject.id)) return
      seen.add(subject.id)
      subjectList.push(subject)
    })
  })

  return subjectList
})

const filteredUniquePrograms = computed(() => [...new Set(filteredStudents.value.map(s => s.program_name).filter(Boolean))])
const filteredUniqueDepartments = computed(() => [...new Set(filteredStudents.value.map(s => s.department_name).filter(Boolean))])

const statsCards = computed(() => [
  { title: 'Total Students', value: filteredStudents.value.length, icon: 'bi bi-people', bgColor: 'bg-admin-light', iconColor: 'text-admin' },
  { title: 'Subjects', value: filteredUniqueSubjects.value.length, icon: 'bi bi-book-half', bgColor: 'bg-success-light', iconColor: 'text-success' },
  { title: 'Programs', value: filteredUniquePrograms.value.length, icon: 'bi bi-mortarboard', bgColor: 'bg-info-light', iconColor: 'text-info' },
  { title: 'Departments', value: filteredUniqueDepartments.value.length, icon: 'bi bi-building', bgColor: 'bg-purple-light', iconColor: 'text-purple' }
])

function getStudentsCacheKey() {
  const subject = filters.value.subject || 'all'
  return `${CACHE_KEY_PREFIX}:${subject}`
}

function getSubjectSummary(student) {
  const subjectsList = Array.isArray(student.subjects) ? student.subjects : []
  if (!subjectsList.length) {
    if (student.subject_name && student.subject_code) return `${student.subject_name} (${student.subject_code})`
    if (student.subject_name) return student.subject_name
    return 'No subject assigned'
  }

  const labels = subjectsList
    .filter(s => s?.name)
    .map(s => s.code ? `${s.name} (${s.code})` : s.name)

  if (labels.length <= 2) return labels.join(', ')
  return `${labels.slice(0, 2).join(', ')} +${labels.length - 2} more`
}

async function loadStudents(forceRefresh = false) {
  loading.value = true
  error.value = null
  try {
    const cacheKey = getStudentsCacheKey()

    if (!forceRefresh) {
      const cached = cacheService.get(cacheKey)
      if (cached) { students.value = cached; loading.value = false; return }
    }
    const allStudents = await teacherPanelService.getAllStudentsFromClasses({
      dedupe: true,
      subject: filters.value.subject || null
    })
    students.value = allStudents.map(student => ({
      ...student,
      subject_id: student.class?.subject_id || student.subject_id,
      subject_name: student.class?.subject_name || student.subject_name,
      subject_code: student.class?.subject_code || student.subject_code,
      program_name: student.class?.program_name || student.program_name,
      department_name: student.class?.department_name || student.department_name,
      session_id: student.class?.session_id || student.session_id,
      session_name: student.class?.session_name || student.session_name,
      class_id: student.class?.id
    }))
    cacheService.set(cacheKey, students.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load students'
    students.value = []
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.value = { subject: '', program: '', search: '' }
  router.replace({ query: {} })
}

onMounted(() => loadStudents())

watch(
  () => filters.value.subject,
  () => {
    loadStudents(false)
  }
)

watch(
  () => route.query.search,
  (newSearch) => {
    filters.value.search = newSearch ? String(newSearch) : ''
  }
)

watch(subjectOptions, (options) => {
  if (!filters.value.subject) return
  const allowed = options.some(option => `${option.value}` === `${filters.value.subject}`)
  if (!allowed) filters.value.subject = ''
})

watch(programOptions, (options) => {
  if (!filters.value.program) return
  const allowed = options.some(option => option.value === filters.value.program)
  if (!allowed) filters.value.program = ''
})

</script>
