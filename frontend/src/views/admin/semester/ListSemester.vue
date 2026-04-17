<template>
  <AdminPageTemplate
    title="Semester Management"
    subtitle="View and manage academic semesters"
    icon="bi bi-calendar3"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Semester List"
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
      title="Delete Semester"
      :message="semesterToDelete ? `Delete semester '${semesterToDelete.name}'?` : 'Delete this semester?'"
      type="danger"
      theme="admin"
      confirm-text="Delete"
      @confirm="confirmDeleteSemester"
    />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Semesters" :value="stats.total" icon="bi bi-calendar3" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active" :value="stats.active" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Completed" :value="stats.completed" icon="bi bi-check2-all" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Programs" :value="stats.programs" icon="bi bi-mortarboard" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search by name..."
        :show-status-filter="false"
        search-col-size="col-md-5 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="loadSemesters"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4 col-6">
            <label class="form-label small fw-semibold text-dark">Program</label>
            <select v-model="filters.program" class="form-select" @change="applyFilters">
              <option value="">All Programs</option>
              <option v-for="prog in programs" :key="prog.id" :value="prog.id">{{ prog.name }}</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="semesters"
      :loading="loading"
      loading-text="Loading semesters..."
      empty-icon="bi bi-calendar3"
      empty-title="No semesters found"
      empty-subtitle="Try adjusting your filters or add a new semester"
    >
      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-semester me-2"><i class="bi bi-calendar3"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
            <small class="text-muted">Semester {{ row.number }}</small>
          </div>
        </div>
      </template>

      <template #cell-program="{ row }">
        <span class="badge bg-light text-dark border">{{ row.program_name || getProgramName(row.program) }}</span>
      </template>

      <template #cell-start_date="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-end_date="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-status="{ row }">
        <span :class="['badge', getStatusBadgeClass(row.status)]">
          {{ getStatusLabel(row.status) }}
        </span>
      </template>

      <template #cell-subjects="{ row }">
        <span class="badge bg-info">{{ row.subject_count || 0 }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="false"
          @view="router.push({ name: ADMIN_ROUTES.SEMESTER_PROFILE.name, params: { id: row.id } })"
          @edit="router.push({ name: ADMIN_ROUTES.SEMESTER_EDIT.name, params: { id: row.id } })"
          @delete="deleteSemester(row)"
        />
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ semesters.length }} semesters</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, ConfirmDialog, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert } from '@/composables/shared'
import { semesterService } from '@/services/shared'
import { programService } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Semesters' }
]

const actions = [
  { label: 'Add Semester', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.SEMESTER_ADD.name }) }
]

const tableColumns = [
  { key: 'name', label: 'Semester' },
  { key: 'program', label: 'Program', hideOnMobile: true },
  { key: 'start_date', label: 'Start', hideOnMobile: true },
  { key: 'end_date', label: 'End', hideOnMobile: true },
  { key: 'status', label: 'Status' },
  { key: 'subjects', label: 'Subjects', center: true },
  { key: 'actions', label: 'Actions', center: true }
]

const programs = ref([])
const showConfirmDialog = ref(false)
const semesterToDelete = ref(null)
const { alert, showAlert } = useAlert()

// Use composable for list logic
const {
  loading,
  filteredData: semesters,
  filters,
  loadData,
  applyFilters,
  resetFilters: baseResetFilters
} = useEntityList({
  cacheKey: 'semesters_list',
  searchFields: ['name'],
  defaultFilters: { program: '' },
  customFilter: (data, filterValues) => {
    if (filterValues.program) {
      return data.filter(s => String(s.program) === String(filterValues.program))
    }
    return data
  }
})

// Custom stats
const stats = computed(() => ({
  total: semesters.value.length,
  active: semesters.value.filter(s => s.status === 'active').length,
  completed: semesters.value.filter(s => s.status === 'completed').length,
  programs: new Set(semesters.value.map(s => s.program)).size
}))

const loadSemesters = async () => {
  const semestersPromise = loadData(() => semesterService.getAll())

  // Load programs in parallel
  const cachedProg = cacheService.get('programs_list')
  if (cachedProg) {
    programs.value = cachedProg
  } else {
    try {
      const progRes = await programService.getAllPrograms()
      const progList = progRes.results || progRes.data || progRes
      cacheService.set('programs_list', progList)
      programs.value = progList
    } catch (e) {
      console.error('Error loading programs:', e)
    }
  }

  await semestersPromise
}

const getProgramName = (programId) => {
  const semester = semesters.value.find(s => s.program === programId)
  if (semester?.program_name) return semester.program_name
  const p = programs.value.find(x => String(x.id) === String(programId))
  return p ? p.name : 'N/A'
}

// Use shared formatDate utility
const formatDate = (d) => formatDateUtil(d)

const getStatusBadgeClass = (status) => {
  const map = { draft: 'bg-secondary', active: 'bg-success', completed: 'bg-info', archived: 'bg-dark' }
  return map[status] || 'bg-secondary'
}

const getStatusLabel = (status) => {
  const map = { draft: 'Draft', active: 'Active', completed: 'Completed', archived: 'Archived' }
  return map[status] || status
}

const deleteSemester = (sem) => {
  semesterToDelete.value = sem
  showConfirmDialog.value = true
}

const confirmDeleteSemester = async () => {
  try {
    await semesterService.delete(semesterToDelete.value.id)
    cacheService.clear('semesters_list')
    showAlert('success', 'Semester deleted successfully')
    loadSemesters()
  } catch (e) {
    console.error(e)
    showAlert('error', 'Failed to delete semester')
  } finally {
    showConfirmDialog.value = false
    semesterToDelete.value = null
  }
}

const resetFilters = () => {
  filters.value.program = ''
  baseResetFilters()
}

// Watch program filter
watch(() => filters.value.program, () => applyFilters())

onMounted(loadSemesters)
</script>


