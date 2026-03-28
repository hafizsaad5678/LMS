<template>
  <AdminPageTemplate
    title="Assignment Management"
    subtitle="View and manage all assignments"
    icon="bi bi-file-earmark-text"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Assignment List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Assignments" :value="stats.total" icon="bi bi-file-earmark-text" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Due This Week" :value="stats.dueThisWeek" icon="bi bi-calendar-week" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Submissions" :value="stats.totalSubmissions" icon="bi bi-upload" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Overdue" :value="stats.overdue" icon="bi bi-exclamation-triangle" bg-color="bg-danger-light" icon-color="text-danger" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search by title or subject..."
        :show-status-filter="false"
        :loading="loading"
        @refresh="loadAssignments"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <select v-model="filters.subject" class="form-select" @change="loadAssignments">
              <option value="">All Subjects</option>
              <option v-for="subj in subjects" :key="subj.id" :value="subj.id">{{ subj.code }} - {{ subj.name }}</option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <select v-model="filters.status" class="form-select" @change="loadAssignments">
              <option value="">All Status</option>
              <option v-for="opt in ASSIGNMENT_TIME_STATUS_OPTIONS" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="assignments"
      :loading="loading"
      loading-text="Loading assignments..."
      empty-icon="bi bi-file-earmark-text"
      empty-title="No assignments found"
      empty-subtitle="Try adjusting your filters or create a new assignment"
    >
      <template #cell-title="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-assignment me-2"><i class="bi bi-file-earmark-text"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.title }}</div>
            <small class="text-muted d-none d-md-block">{{ truncate(row.description, 30) }}</small>
          </div>
        </div>
      </template>

      <template #cell-subject_code="{ value }">
        <span class="badge bg-info">{{ value || 'N/A' }}</span>
      </template>

      <template #cell-due_date="{ row }">
        <div :class="getDueDateClass(row.due_date)">
          <i class="bi bi-calendar me-1"></i>{{ formatDate(row.due_date) }}
        </div>
      </template>

      <template #cell-total_marks="{ value }">
        <span class="fw-semibold">{{ value }}</span>
      </template>

      <template #cell-submission_count="{ value }">
        <span class="badge bg-success">{{ value || 0 }}</span>
      </template>

      <template #cell-status="{ row }">
        <span :class="getStatusBadge(row.due_date)">{{ getStatus(row.due_date) }}</span>
      </template>

      <template #cell-actions="{ row }">
        <button @click="viewSubmissions(row)" class="btn btn-sm btn-outline-info" title="View Submissions">
          <i class="bi bi-list-check"></i>
        </button>
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ assignments.length }} assignments</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, SelectInput } from '@/components/shared/common'
import { useEntityList } from '@/composables/shared'
import { assignmentService } from '@/services/shared'
import { subjectService } from '@/services/shared'
import { formatDate as formatDateUtil, truncateText } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { ASSIGNMENT_TIME_STATUS_OPTIONS } from '@/utils/constants/options'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Assignments' }
]

const actions = [
  { label: 'Add Assignment', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push(`${ADMIN_ROUTES.ASSIGNMENTS.path}/add`) }
]

const tableColumns = [
  { key: 'title', label: 'Title' },
  { key: 'subject_code', label: 'Subject' },
  { key: 'due_date', label: 'Due Date' },
  { key: 'total_marks', label: 'Marks', hideOnMobile: true },
  { key: 'submission_count', label: 'Submissions', hideOnMobile: true },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const subjects = ref([])

// Use composable for list logic
const {
  loading,
  filteredData: assignments,
  filters,
  loadData,
  applyFilters,
  resetFilters: baseResetFilters
} = useEntityList({
  cacheKey: 'assignments_list',
  searchFields: ['title', 'subject_name'],
  defaultFilters: { subject: '', status: '' },
  customFilter: (data, filterValues) => {
    let result = data
    if (filterValues.subject) {
      result = result.filter(a => String(a.subject) === String(filterValues.subject))
    }
    if (filterValues.status === 'upcoming') {
      result = result.filter(a => new Date(a.due_date) >= new Date())
    } else if (filterValues.status === 'overdue') {
      result = result.filter(a => new Date(a.due_date) < new Date())
    }
    return result
  }
})

// Custom stats
const stats = computed(() => {
  const total = assignments.value.length
  const now = new Date()
  const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
  
  const dueThisWeek = assignments.value.filter(a => {
    const due = new Date(a.due_date)
    return due >= now && due <= weekFromNow
  }).length
  
  const overdue = assignments.value.filter(a => new Date(a.due_date) < now).length
  const totalSubmissions = assignments.value.reduce((sum, a) => sum + (a.submission_count || 0), 0)
  
  return { total, dueThisWeek, overdue, totalSubmissions }
})

const fetchAssignments = () => assignmentService.getAllAssignments()

const loadAssignments = () => loadData(fetchAssignments)

const loadSubjects = async () => {
  try {
    const response = await subjectService.getAllSubjects()
    subjects.value = Array.isArray(response) ? response : (response.results || [])
  } catch (error) {
    console.error('Error loading subjects:', error)
  }
}

const resetFilters = () => {
  filters.value.subject = ''
  filters.value.status = ''
  baseResetFilters()
}

const viewSubmissions = (assignment) => {
  router.push(`${ADMIN_ROUTES.ASSIGNMENTS.path}/${assignment.id}/submissions`)
}

// Use shared formatDate utility
const formatDate = (dateString) => formatDateUtil(dateString)

// Use shared truncateText utility
const truncate = (text, length) => truncateText(text, length)

const getDueDateClass = (dueDate) => {
  const due = new Date(dueDate)
  const now = new Date()
  if (due < now) return 'text-danger fw-semibold'
  const diff = due.getTime() - now.getTime()
  if (diff < 3 * 24 * 60 * 60 * 1000) return 'text-warning fw-semibold'
  return 'text-muted'
}

const getStatus = (dueDate) => new Date(dueDate) < new Date() ? 'Overdue' : 'Active'
const getStatusBadge = (dueDate) => new Date(dueDate) < new Date() ? 'badge bg-danger' : 'badge bg-success'

// Watch custom filters
watch(() => [filters.value.subject, filters.value.status], () => applyFilters())

onMounted(() => {
  loadSubjects()
  loadAssignments()
})
</script>



