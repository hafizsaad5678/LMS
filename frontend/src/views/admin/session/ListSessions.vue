<template>
  <AdminPageTemplate
    title="Academic Sessions"
    subtitle="Manage batches and intakes for all programs"
    icon="bi bi-calendar-check"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Session List"
  >
    <!-- Alert Message -->
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="alert.show = false"
    />

    <ConfirmDialog
      v-model="showConfirmDialog"
      :title="confirmTitle"
      :message="confirmMessage"
      :type="confirmAction === 'deleteSession' ? 'danger' : 'info'"
      theme="admin"
      :confirm-text="confirmAction === 'deleteSession' ? 'Delete' : 'Confirm'"
      @confirm="handleConfirm"
    />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Sessions" :value="stats.total" icon="bi bi-list" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active" :value="stats.active" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Upcoming" :value="stats.upcoming" icon="bi bi-clock" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Completed" :value="stats.completed" icon="bi bi-archive" bg-color="bg-info-light" icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        v-model:status-value="filters.status"
        search-placeholder="Search sessions..."
        preset="admin-list"
        :loading="loading"
        @refresh="loadSessions"
        @reset="resetFilters"
      />
    </template>

    <!-- Main Content -->
    <DataTable
      class="session-list-table"
      :columns="tableColumns"
      :data="sessions"
      :loading="loading"
      loading-text="Loading sessions..."
      empty-icon="bi bi-calendar-check"
      empty-title="No sessions found"
      empty-subtitle="Create your first session to get started"
    >
      <template #cell-session_name="{ row }">
        <div class="py-1">
          <div class="fw-bold text-dark mb-0">{{ row.session_name }}</div>
          <div class="text-muted small lh-1">{{ row.session_code }}</div>
        </div>
      </template>

      <template #cell-program_name="{ row }">
        <div class="py-1">
          <div class="text-dark fw-semibold mb-1 small">{{ row.program_name }}</div>
          <span class="badge bg-primary rounded-pill px-3 py-1 fw-bold" style="font-size: 0.65rem; letter-spacing: 0.02em;">
            {{ row.program_level_display }}
          </span>
        </div>
      </template>

      <template #cell-years="{ row }">
        <span class="text-dark fw-medium">{{ row.start_year }} - {{ row.end_year }}</span>
      </template>

      <template #cell-capacity="{ row }">
        <div class="d-flex align-items-center gap-2" style="min-width: 150px;">
          <small class="text-muted fw-bold" style="font-size: 0.7rem;">{{ row.current_enrollment }}/{{ row.total_capacity }}</small>
          <div class="progress flex-grow-1" style="height: 5px; background-color: #eaeff4;">
            <div class="progress-bar bg-success transition-all" :style="{ width: row.capacity_percentage + '%' }"></div>
          </div>
          <small class="text-muted fw-bold" style="font-size: 0.7rem;">{{ Math.round(row.capacity_percentage) }}%</small>
        </div>
      </template>

      <template #cell-semester_count="{ row }">
        <span class="badge bg-info rounded-pill px-3 py-1 fw-bold">
          {{ row.semester_count }}/
        </span>
      </template>

      <template #cell-status="{ row }">
        <span class="badge bg-success rounded-pill px-3 py-1 fw-bold text-capitalize">
          {{ row.status }}
        </span>
      </template>

      <template #cell-actions="{ row }">
        <div class="d-flex align-items-center gap-2 justify-content-center">
          <button @click="router.push({ name: ADMIN_ROUTES.SESSION_PROFILE.name, params: { id: row.id } })" class="btn btn-outline-info btn-sm rounded-3 p-0 d-flex align-items-center justify-content-center shadow-sm" style="width: 34px; height: 34px;"><i class="bi bi-eye"></i></button>
          <button @click="router.push({ name: ADMIN_ROUTES.SESSION_EDIT.name, params: { id: row.id } })" class="btn btn-outline-primary btn-sm rounded-3 p-0 d-flex align-items-center justify-content-center shadow-sm" style="width: 34px; height: 34px;"><i class="bi bi-pencil"></i></button>
          <button @click="confirmDelete(row)" class="btn btn-outline-danger btn-sm rounded-3 p-0 d-flex align-items-center justify-content-center shadow-sm" style="width: 34px; height: 34px;"><i class="bi bi-trash"></i></button>
          <button v-if="row.semester_count === 0" @click="setupSemesters(row)" class="btn btn-success btn-sm rounded-3 p-0 d-flex align-items-center justify-content-center shadow-sm" style="width: 34px; height: 34px;"><i class="bi bi-gear-fill"></i></button>
        </div>
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ sessions.length }} sessions</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, ConfirmDialog, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert, useListStats } from '@/composables/shared'
import { sessionService, cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Sessions' }
]

const actions = [
  { label: 'Create Session', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.SESSION_ADD.name }) }
]

const tableColumns = [
  { key: 'session_name', label: 'Session' },
  { key: 'program_name', label: 'Program', hideOnMobile: true },
  { key: 'years', label: 'Years' },
  { key: 'capacity', label: 'Capacity', hideOnMobile: true },
  { key: 'semester_count', label: 'Semesters' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const showConfirmDialog = ref(false)
const confirmAction = ref(null)
const confirmMessage = ref('')
const confirmTitle = ref('')
const sessionToDelete = ref(null)
const sessionToSetup = ref(null)
const { alert, showAlert } = useAlert()

// Use composable for list logic
const {
  loading,
  data,
  filteredData: sessions,
  filters,
  loadData,
  refresh,
  resetFilters: baseResetFilters
} = useEntityList({
  cacheKey: 'sessions_list',
  searchFields: ['session_name', 'session_code', 'program_name', 'program_level_display'],
  statusField: 'status',
  defaultFilters: {},
  filterSchema: [
    {
      key: 'status',
      itemValue: 'status',
      normalize: value => String(value || '').toLowerCase()
    }
  ]
})

const listStats = useListStats(data)

const stats = listStats.summary({
  total: list => list.length,
  active: list => list.filter((session) => session.status === 'active').length,
  upcoming: list => list.filter((session) => session.status === 'upcoming').length,
  completed: list => list.filter((session) => session.status === 'completed').length
})

const fetchSessions = async () => {
  const data = await sessionService.getSessions()
  return Array.isArray(data) ? data : (data.results || [])
}

const loadSessions = async () => loadData(fetchSessions)

const setupSemesters = (session) => {
  sessionToSetup.value = session
  confirmTitle.value = 'Setup Semesters'
  confirmMessage.value = `Auto-create ${session.total_semesters} semesters for ${session.session_name}?`
  confirmAction.value = 'setupSemesters'
  showConfirmDialog.value = true
}

const confirmSetupSemesters = async () => {
  try {
    await sessionService.setupSemesters(sessionToSetup.value.id)
    showAlert('success', `Successfully created semesters for ${sessionToSetup.value.session_name}`)
    await refresh(fetchSessions)
  } catch (error) {
    console.error('Error setting up semesters:', error)
    showAlert('error', error.response?.data?.error || 'Failed to setup semesters')
  } finally {
    showConfirmDialog.value = false
    sessionToSetup.value = null
  }
}

const confirmDelete = (session) => {
  sessionToDelete.value = session
  confirmTitle.value = 'Delete Session'
  confirmMessage.value = `Are you sure you want to delete ${session.session_name}?`
  confirmAction.value = 'deleteSession'
  showConfirmDialog.value = true
}

const confirmDeleteSession = async () => {
  try {
    await sessionService.deleteSession(sessionToDelete.value.id)
    showAlert('success', 'Session deleted successfully')
    await refresh(fetchSessions)
  } catch (error) {
    console.error('Error deleting session:', error)
    showAlert('error', error.response?.data?.error || 'Failed to delete session')
  } finally {
    showConfirmDialog.value = false
    sessionToDelete.value = null
  }
}

const handleConfirm = () => {
  if (confirmAction.value === 'setupSemesters') {
    confirmSetupSemesters()
  } else if (confirmAction.value === 'deleteSession') {
    confirmDeleteSession()
  }
}

const resetFilters = () => {
  baseResetFilters()
}

const percentageColor = (percentage) => {
  if (percentage >= 90) return 'text-danger'
  if (percentage >= 75) return 'text-warning'
  return 'text-success'
}

const getProgramLevelBadgeClass = (level) => {
  const classes = { 
    bachelor: 'bg-primary-subtle text-primary border border-primary-subtle', 
    master: 'bg-info-subtle text-info border border-info-subtle', 
    intermediate: 'bg-warning-subtle text-warning border border-warning-subtle', 
    phd: 'bg-danger-subtle text-danger border border-danger-subtle', 
    diploma: 'bg-success-subtle text-success border border-success-subtle' 
  }
  return classes[level] || 'bg-secondary-subtle text-secondary border border-secondary-subtle'
}

const getStatusBadgeClass = (status) => {
  const classes = { 
    upcoming: 'bg-warning-subtle text-warning border border-warning-subtle', 
    active: 'bg-success-subtle text-success border border-success-subtle', 
    completed: 'bg-info-subtle text-info border border-info-subtle', 
    archived: 'bg-dark-subtle text-dark border border-dark-subtle' 
  }
  return classes[status] || 'bg-primary-subtle text-primary border border-primary-subtle'
}

const getCapacityClass = (percentage) => {
  if (percentage >= 90) return 'bg-danger'
  if (percentage >= 75) return 'bg-warning'
  return 'bg-success'
}

onMounted(loadSessions)
</script>

