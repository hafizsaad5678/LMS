<template>
  <TeacherPageTemplate title="Assignments" subtitle="Create and manage student assignments"
    icon="bi bi-file-earmark-text" :breadcrumbs="breadcrumbs" :actions="actions">
    <AlertMessage v-if="alert.show" v-bind="alert" :auto-close="true" @close="clearAlert" />

    <ConfirmDialog v-model="showDeleteModal" title="Delete Assignment"
      :message="`Are you sure you want to delete '${selectedAssignment?.title}'? This action cannot be undone.`"
      type="danger" theme="teacher" :loading="deleting" confirm-text="Delete Permanently" @confirm="handleDelete" />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 mb-4">
        <div v-for="stat in statsCards" :key="stat.title" class="col-md-3 col-6">
          <StatCard v-bind="stat" />
        </div>
      </div>
    </template>

    <template #filters>
      <SearchFilter v-model="filters.search" :show-card="true" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search assignments..." search-col-size="col-md-5"
        actions-col-size="col-md-3" theme="teacher" @refresh="refreshAssignments" @reset="resetFilters">
        <template #filters>
          <div class="col-md-4">
            <SelectInput v-model="filters.subject" :options="subjectOptions" placeholder="All Subjects"
              :no-margin="true" />
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredData" :loading="loading" loading-text="Loading assignments..."
      empty-icon="bi bi-file-earmark-text" empty-title="No assignments found">
      <template #cell-title="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle-teacher sm me-2">
            <i class="bi bi-file-earmark-text"></i>
          </div>
          <div>
            <div class="fw-bold text-dark">{{ row.title }}</div>
            <div class="small text-muted">
              <i class="bi bi-book me-1"></i>
              {{ row.subject_name }} ({{ row.subject_code }})
            </div>
          </div>
        </div>
      </template>

      <template #cell-due_date="{ row }">
        <div :class="getDueDateClass(row.due_date)">
          <i class="bi bi-calendar-event me-1"></i>
          {{ formatDate(row.due_date) }}
        </div>
      </template>

      <template #cell-submissions="{ row }">
        <div class="text-center">
          <div class="fw-bold text-teacher">{{ row.submission_count }} / {{ row.total_students }}</div>
          <div class="progress progress-mini">
            <div class="progress-bar bg-teacher"
              :style="{ width: (row.total_students ? (row.submission_count / row.total_students * 100) : 0) + '%' }">
            </div>
          </div>
        </div>
      </template>

      <template #cell-actions="{ row }">
        <div class="d-flex gap-2 justify-content-center">
          <button @click="router.push(`${TEACHER_ROUTES.SUBMISSIONS.path}?id=${row.id}`)"
            class="btn btn-sm btn-outline-primary btn-action" title="View Submissions"><i
              class="bi bi-people"></i></button>
          <button @click="router.push(`${TEACHER_ROUTES.ASSIGNMENT_EDIT.path}/${row.id}`)"
            class="btn btn-sm btn-outline-primary btn-action" title="Edit"><i class="bi bi-pencil"></i></button>
          <button @click="confirmDelete(row)" class="btn btn-sm btn-outline-danger btn-action" title="Delete"><i
              class="bi bi-trash"></i></button>
        </div>
      </template>
    </DataTable>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ConfirmDialog, AlertMessage, SelectInput } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { useEntityList, useAlert, useAsyncState } from '@/composables/shared'
import { generateBreadcrumbs } from '@/utils/navigation'
import { formatDate, isDateWithinNextDays } from '@/utils/formatters'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const { alert, showSuccess, showError, clearAlert } = useAlert()
const { loading, data: assignments, filteredData, filters, loadData, resetFilters, refresh, applyFilters } = useEntityList({
  cacheKey: 'teacher_assignments_list',
  searchFields: ['title', 'subject_name', 'subject_code', 'description'],
  defaultFilters: { subject: '' },
  customFilter: (items, filters) => {
    if (!filters.subject) return items
    return items.filter(a => (a.subject_id || a.subject) == filters.subject)
  }
})

const { data: subjects, loading: loadingSubjects, execute: fetchSubjects } = useAsyncState({ initialLoading: true })
const showDeleteModal = ref(false)
const selectedAssignment = ref(null)
const deleting = ref(false)

const breadcrumbs = generateBreadcrumbs('teacher', 'Assignments')

const actions = [
  { label: 'Create Assignment', icon: 'bi bi-plus-lg', variant: 'btn-teacher-outline', onClick: () => router.push(TEACHER_ROUTES.ASSIGNMENT_CREATE.path) }
]

const tableColumns = [
  { key: 'title', label: 'Assignment Details' },
  { key: 'due_date', label: 'Due Date' },
  { key: 'submissions', label: 'Submissions' },
  { key: 'total_marks', label: 'Marks', center: true },
  { key: 'actions', label: 'Actions', center: true }
]

// Computed
const subjectOptions = computed(() => (subjects.value?.results || []).map(s => ({
  value: s.subject_id || s.id,
  label: `${s.subject_name} (${s.subject_code})`
})))

const statsCards = computed(() => {
  const now = new Date()

  return [
    { title: 'Total Assignments', value: assignments.value.length, icon: 'bi bi-file-earmark-text', bgColor: 'bg-admin-light', iconColor: 'text-teacher' },
    {
      title: 'Due This Week', value: assignments.value.filter(a => {
        return isDateWithinNextDays(a.due_date, 7, now)
      }).length, icon: 'bi bi-calendar-week', bgColor: 'bg-warning-light', iconColor: 'text-warning'
    },
    { title: 'Total Submissions', value: assignments.value.reduce((sum, a) => sum + (a.submission_count || 0), 0), icon: 'bi bi-upload', bgColor: 'bg-success-light', iconColor: 'text-success' },
    {
      title: 'Pending Review',
      value: assignments.value.reduce((sum, a) => {
        if (typeof a.pending_review_count === 'number') {
          return sum + a.pending_review_count
        }
        return sum + Math.max(0, (a.submission_count || 0) - (a.graded_count || 0))
      }, 0),
      icon: 'bi bi-clock-history',
      bgColor: 'bg-danger-light',
      iconColor: 'text-danger'
    }
  ]
})

// Methods
const loadAssignments = () => loadData(() => teacherPanelService.getMyAssignments())
const refreshAssignments = () => refresh(() => teacherPanelService.getMyAssignments())

const loadSubjects = () => fetchSubjects(() => teacherPanelService.getMyClasses())

const confirmDelete = (assignment) => {
  selectedAssignment.value = assignment
  showDeleteModal.value = true
}

const handleDelete = async () => {
  if (!selectedAssignment.value) return
  deleting.value = true
  try {
    await teacherPanelService.deleteAssignment(selectedAssignment.value.id)
    showDeleteModal.value = false
    showSuccess('Assignment deleted successfully!')
    refreshAssignments()
  } catch (error) {
    showError('Failed to delete assignment.')
  } finally {
    deleting.value = false
  }
}

const getDueDateClass = (dateString) => {
  const due = new Date(dateString)
  const now = new Date()
  if (due < now) return 'text-danger fw-semibold'
  return (due.getTime() - now.getTime() < 86400000) ? 'text-warning fw-semibold' : 'text-muted'
}

watch(() => filters.value.subject, () => {
  applyFilters()
})

onMounted(() => {
  loadSubjects()
  loadAssignments()
})
</script>
