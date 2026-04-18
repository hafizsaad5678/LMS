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
        preset="admin-list"
        :show-status-filter="false"
        :loading="loading"
        @refresh="loadSemesters"
        @reset="resetFilters"
      >
        <template #filters>
          <SelectInput
            v-model="filters.program"
            label="Program"
            placeholder="All Programs"
            :options="programs"
            option-value-key="id"
            option-label-key="name"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
          <SelectInput
            v-model="filters.status"
            label="Status"
            placeholder="All Status"
            :options="SEMESTER_STATUS_OPTIONS"
            option-value-key="value"
            option-label-key="label"
            col-class="col-md-2 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, SelectInput, ActionButtons, ConfirmDialog, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert, useListStats } from '@/composables/shared'
import { semesterService } from '@/services/shared'
import { programService } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { SEMESTER_STATUS_OPTIONS, getOptionLabel } from '@/utils/constants/options'

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

const normalizeStatus = (status) => String(status || '').trim().toLowerCase()

const extractProgramId = (semester) => {
  if (!semester || typeof semester !== 'object') return ''

  const direct = semester.program
  if (direct && typeof direct === 'object') {
    return String(direct.id || direct.pk || '')
  }

  const fallback = semester.program_id || direct || ''
  return String(fallback)
}

// Use composable for list logic
const {
  loading,
  data,
  filteredData: semesters,
  filters,
  loadData,
  refresh,
  resetFilters: baseResetFilters
} = useEntityList({
  cacheKey: 'semesters_list',
  searchFields: ['name'],
  forceFreshOnMount: true,
  defaultFilters: { program: '', status: 'active' },
  resetToDefaults: { status: 'active' },
  filterSchema: [
    {
      key: 'status',
      itemValue: 'status',
      normalize: value => String(value || '').trim().toLowerCase()
    },
    {
      key: 'program',
      predicate: (semester, selectedProgramId) => {
        const programId = String(selectedProgramId || '')
        const selectedProgram = programs.value.find((program) => String(program.id) === programId)
        const selectedProgramName = String(selectedProgram?.name || '').trim().toLowerCase()

        const semesterProgramId = extractProgramId(semester)
        const semesterProgramName = String(semester.program_name || semester.program?.name || '').trim().toLowerCase()

        if (semesterProgramId && semesterProgramId === programId) return true
        if (selectedProgramName && semesterProgramName && semesterProgramName === selectedProgramName) return true
        return false
      }
    }
  ]
})

const listStats = useListStats(semesters)

const stats = listStats.summary({
  total: list => list.length,
  active: list => list.filter((semester) => normalizeStatus(semester.status) === 'active').length,
  completed: list => list.filter((semester) => normalizeStatus(semester.status) === 'completed').length,
  programs: list => new Set(list.map((semester) => extractProgramId(semester))).size
})

const loadPrograms = async () => {
  const cachedProg = cacheService.get('programs_list')
  if (cachedProg) {
    programs.value = cachedProg
    return
  }

  try {
    const progRes = await programService.getAllPrograms()
    const progList = progRes.results || progRes.data || progRes
    cacheService.set('programs_list', progList)
    programs.value = progList
  } catch (e) {
    console.error('Error loading programs:', e)
  }
}

const loadSemesters = async () => {
  await loadPrograms()
  return loadData(() => semesterService.getAll())
}

const getProgramName = (programId) => {
  const semester = data.value.find((s) => extractProgramId(s) === String(programId))
  if (semester?.program_name) return semester.program_name
  const p = programs.value.find((x) => String(x.id) === String(programId))
  return p ? p.name : 'N/A'
}

// Use shared formatDate utility
const formatDate = (d) => formatDateUtil(d)

const getStatusBadgeClass = (status) => {
  const normalized = normalizeStatus(status)
  const map = { draft: 'bg-secondary', active: 'bg-success', completed: 'bg-info', archived: 'bg-dark' }
  return map[normalized] || 'bg-secondary'
}

const getStatusLabel = (status) => getOptionLabel(SEMESTER_STATUS_OPTIONS, normalizeStatus(status))

const deleteSemester = (sem) => {
  semesterToDelete.value = sem
  showConfirmDialog.value = true
}

const confirmDeleteSemester = async () => {
  try {
    await semesterService.delete(semesterToDelete.value.id)
    showAlert('success', 'Semester deleted successfully')
    await refresh(() => semesterService.getAll())
  } catch (e) {
    console.error(e)
    showAlert('error', 'Failed to delete semester')
  } finally {
    showConfirmDialog.value = false
    semesterToDelete.value = null
  }
}

const resetFilters = () => baseResetFilters()

onMounted(loadSemesters)
</script>


