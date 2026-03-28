<template>
  <TeacherPageTemplate
    title="My Classes"
    subtitle="Manage your assigned classes and subjects"
    icon="bi bi-book-half"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <template #stats>
      <div class="row g-3 g-lg-4 mb-4">
        <div class="col-6 col-md-3">
          <StatCard 
            title="Total Classes" 
            :value="classes?.length || 0" 
            icon="bi bi-book-half" 
            bg-color="bg-teacher-light" 
            icon-color="text-teacher"
            @click="viewAllClasses"
          />
        </div>
        <div class="col-6 col-md-3">
          <StatCard 
            title="Total Students" 
            :value="totalStudents" 
            icon="bi bi-people" 
            bg-color="bg-success-light" 
            icon-color="text-success"
            @click="viewAllStudents"
          />
        </div>
        <div class="col-6 col-md-3">
          <StatCard 
            title="Classes Today" 
            :value="todayClasses" 
            icon="bi bi-calendar-event" 
            bg-color="bg-warning-light" 
            icon-color="text-warning"
            @click="viewTodaySchedule"
          />
        </div>
        <div class="col-6 col-md-3">
          <StatCard 
            title="Pending Reviews" 
            :value="pendingAssignments" 
            icon="bi bi-clipboard-check" 
            bg-color="bg-info-light" 
            icon-color="text-info"
            @click="viewPendingReviews"
          />
        </div>
      </div>
    </template>

    <template #filters>
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-center">
            <div class="col-md-3">
              <input 
                v-model="searchQuery" 
                type="text" 
                class="form-control" 
                placeholder="Search classes, subjects, codes..."
              >
            </div>
            <div class="col-md-2">
              <SelectInput
                v-model="filters.department"
                :options="(departments || []).map(d => ({ value: d, label: d }))"
                placeholder="All Departments"
                :no-margin="true"
              />
            </div>
            <div class="col-md-2">
              <SelectInput
                v-model="filters.program"
                :options="(programs || []).map(p => ({ value: p, label: p }))"
                placeholder="All Programs"
                :no-margin="true"
              />
            </div>
            <div class="col-md-2">
              <SelectInput
                v-model="filters.semester"
                :options="(semesters || []).map(s => ({ value: s, label: s }))"
                placeholder="All Semesters"
                :no-margin="true"
              />
            </div>
            <div class="col-md-3 text-end">
              <button @click="refresh" class="btn btn-teacher-outline me-2">
                <i class="bi bi-arrow-clockwise me-1"></i>Refresh
              </button>
              <button @click="resetFilters" class="btn btn-outline-secondary">
                <i class="bi bi-x-circle me-1"></i>Reset
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <LoadingSpinner v-if="loading" message="Loading classes..." />

    <div v-else-if="error" class="text-center py-5">
      <AlertMessage
        type="error"
        :message="error"
        title="Unable to Load Classes"
      />
      <button @click="refresh" class="btn btn-teacher-primary mt-3">
        <i class="bi bi-arrow-clockwise me-2"></i>Try Again
      </button>
    </div>

    <EmptyState v-else-if="filteredClasses.length === 0" icon="bi bi-book" title="No Classes Found"
      :message="filters.department || filters.program || filters.semester ? 'No classes match your filter criteria.' : 'You don\'t have any classes assigned yet.'"
    >
      <button v-if="filters.department || filters.program || filters.semester" @click="resetFilters" class="btn btn-teacher-outline">
        <i class="bi bi-x-circle me-2"></i>Clear Filters
      </button>
    </EmptyState>

    <div v-else class="row g-4">
      <div v-for="cls in filteredClasses" :key="cls.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="icon-box-48 rounded-3">
                <i class="bi bi-book-half text-teacher fs-5"></i>
              </div>
              <div class="text-end">
                <span class="badge badge-semester mb-1">{{ cls.semester }}</span>
                <br>
                <small class="text-muted">{{ cls.program_level }}</small>
              </div>
            </div>
            
            <h5 class="fw-bold mb-1">{{ cls.subject_name }}</h5>
            <p class="text-muted small mb-2">{{ cls.subject_code }}</p>
            
            <!-- Academic Hierarchy -->
            <div class="mb-3">
              <div class="d-flex align-items-center gap-2 mb-1">
                <i class="bi bi-building text-muted small"></i>
                <small class="text-muted">{{ cls.department_name }}</small>
              </div>
              <div class="d-flex align-items-center gap-2 mb-1">
                <i class="bi bi-mortarboard text-muted small"></i>
                <small class="text-muted">{{ cls.program_name }}</small>
              </div>
            </div>
            
            <div class="d-flex align-items-center justify-content-between mb-3 text-muted small">
              <span @click="viewSubjectStudents(cls)" class="cursor-pointer hover-link">
                <i class="bi bi-people me-1"></i>{{ cls.student_count }} Students
              </span>
              <span><i class="bi bi-award me-1"></i>{{ cls.credit_hours }} Credit Hours</span>
            </div>
            
            <div class="d-flex gap-2">
              <button @click="viewClass(cls)" class="btn btn-sm btn-teacher-primary flex-grow-1">
                <i class="bi bi-eye me-1"></i>View
              </button>
              <button @click="markAttendance(cls)" class="btn btn-sm btn-teacher-outline">
                <i class="bi bi-calendar-check"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { StatCard, AlertMessage, SelectInput, LoadingSpinner, EmptyState } from '@/components/shared/common'
import { useCachedData } from '@/composables/shared'
import { useFilterLogic } from '@/composables/teacher/useFilterLogic'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { smartSearch } from '@/utils'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'My Classes' }
]

const actions = [
  { label: 'View Schedule', icon: 'bi bi-calendar3', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.CLASS_SCHEDULE.name }) }
]

const filters = ref({ department: '', program: '', semester: '' })

const { searchQuery, filteredItems: searchFilteredClasses } = useFilterLogic(
  computed(() => classes.value || []),
  { searchFields: ['subject_name', 'subject_code', 'department_name', 'program_name', 'semester'] }
)

const mapClassData = (cls) => ({
  id: cls.id || cls.subject_id,
  subject_id: cls.subject_id,
  subject_name: cls.subject_name || 'Unknown Subject',
  subject_code: cls.subject_code || 'N/A',
  credit_hours: cls.credit_hours || 3,
  description: cls.description || '',
  student_count: cls.student_count || 0,
  semester: cls.semester || 'N/A',
  semester_number: cls.semester_number,
  program_name: cls.program_name || 'N/A',
  program_code: cls.program_code || 'N/A',
  program_level: cls.program_level || 'N/A',
  department_name: cls.department_name || 'N/A',
  department_code: cls.department_code || 'N/A'
})

const { data: classes, loading, error, load, refresh } = useCachedData(
  'teacher_classes_list',
  async () => {
    const response = await teacherPanelService.getMyClasses()
    return (response.results || response || []).map(mapClassData)
  }
)

// Dynamic filter options
const departments = computed(() => {
  if (!classes.value) return []
  return [...new Set(classes.value.map(c => c.department_name).filter(Boolean))]
})
const programs = computed(() => {
  if (!classes.value) return []
  return [...new Set(classes.value.map(c => c.program_name).filter(Boolean))]
})
const semesters = computed(() => {
  if (!classes.value) return []
  return [...new Set(classes.value.map(c => c.semester).filter(Boolean))]
})

const totalStudents = computed(() => {
  if (!classes.value) return 0
  return classes.value.reduce((sum, cls) => sum + (cls.student_count || 0), 0)
})
const todayClasses = computed(() => {
  if (!classes.value || classes.value.length === 0) return 0
  return Math.min(3, classes.value.length)
})
const pendingAssignments = computed(() => 0)

const filteredClasses = computed(() => {
  let result = searchFilteredClasses.value || []

  if (filters.value.department) result = result.filter(cls => cls.department_name === filters.value.department)
  if (filters.value.program) result = result.filter(cls => cls.program_name === filters.value.program)
  if (filters.value.semester) result = result.filter(cls => cls.semester === filters.value.semester)
  return result
})

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = { department: '', program: '', semester: '' }
}

const viewClass = (cls) => router.push({ name: TEACHER_ROUTES.SUBJECT_PROFILE.name, params: { id: cls.id } })
const markAttendance = (cls) => router.push({ name: TEACHER_ROUTES.MARK_ATTENDANCE.name, query: { class: cls.id } })
const viewAllStudents = () => router.push({ name: TEACHER_ROUTES.STUDENT_LIST.name })
const viewAllClasses = () => document.querySelector('.row.g-4')?.scrollIntoView({ behavior: 'smooth' })
const viewTodaySchedule = () => router.push({ name: TEACHER_ROUTES.CLASS_SCHEDULE.name })
const viewPendingReviews = () => router.push({ name: TEACHER_ROUTES.SUBMISSIONS.name })
const viewSubjectStudents = (cls) => router.push({ name: TEACHER_ROUTES.STUDENT_LIST.name, query: { subject: cls.subject_id, subject_name: cls.subject_name } })

onMounted(load)
</script>

