<template>
  <AdminPageTemplate
    title="Student Management"
    subtitle="View and manage all student records"
    icon="bi bi-people-fill"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Student List"
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

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Students" :value="stats.total" icon="bi bi-people" type="student" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active Students" :value="stats.active" icon="bi bi-check-circle" type="student" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Inactive Students" :value="stats.inactive" icon="bi bi-x-circle" type="finance" :is-positive="false" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Programs" :value="totalPrograms" icon="bi bi-mortarboard" type="course" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        v-model:status-value="filters.status"
        search-placeholder="Search by name, email, or enrollment number..."
        preset="admin-list"
        :loading="loading"
        @refresh="handleRefresh"
        @reset="resetFilters"
      />
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="filteredData"
      :loading="loading"
      loading-text="Loading students..."
      empty-icon="bi bi-inbox"
      empty-title="No students found"
      empty-subtitle="Try adjusting your filters or add a new student"
    >
      <template #cell-enrollment_number="{ value }">
        <span class="badge bg-light text-dark fw-semibold">{{ value }}</span>
      </template>

      <template #cell-full_name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle me-2">{{ row.full_name?.charAt(0).toUpperCase() }}</div>
          <div>
            <div class="fw-semibold text-dark">{{ row.full_name }}</div>
            <small class="text-muted d-none d-md-block">{{ row.email }}</small>
          </div>
        </div>
      </template>

      <template #cell-program_name="{ value }">
        <span class="badge bg-info-light text-info">{{ value || 'N/A' }}</span>
      </template>

      <template #cell-is_active="{ row }">
        <span :class="['badge', getActiveBadgeClass(row.is_active)]">
          {{ getActiveStatusText(row.is_active) }}
        </span>
      </template>

      <template #cell-edit_count="{ value }">
        <span class="badge bg-light text-dark border">{{ value || 0 }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="true"
          @view="router.push({ name: ADMIN_ROUTES.STUDENT_PROFILE.name, params: { id: row.id } })"
          @edit="router.push({ name: ADMIN_ROUTES.STUDENT_EDIT.name, params: { id: row.id } })"
          @delete="router.push({ name: ADMIN_ROUTES.STUDENT_DELETE.name, params: { id: row.id } })"
          @toggle="handleToggle(row)"
        />
      </template>
    </DataTable>

    <template #footer>
      <div class="d-flex justify-content-end">
        <p class="text-muted small mb-0">Total Records: {{ filteredData.length }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert } from '@/composables/shared'
import { studentService } from '@/services/shared'
import adminPanelService from '@/services/admin/adminPanelService'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getActiveBadgeClass, getActiveStatusText } from '@/utils/badgeHelpers'

const router = useRouter()
const totalPrograms = ref(0) // Initialize as 0

// Use shared alert composable
const { alert, showAlert } = useAlert()

// Config
const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Students' }
]

const actions = [
  { label: 'Add Student', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.STUDENT_ADD.name }) }
]

const tableColumns = [
  { key: 'enrollment_number', label: 'ID' },
  { key: 'full_name', label: 'Name' },
  { key: 'program_name', label: 'Program', hideOnMobile: true, default: 'N/A' },
  { key: 'is_active', label: 'Status' },
  { key: 'edit_count', label: 'Edits', hideOnMobile: true },
  { key: 'created_at', label: 'Joined', type: 'date', hideOnMobile: true },
  { key: 'actions', label: 'Actions', center: true }
]

// Use composable for list logic
const {
  loading,
  filteredData,
  filters,
  stats,
  loadData,
  resetFilters,
  refresh,
  toggleStatus
} = useEntityList({
  cacheKey: 'students_list',
  searchFields: ['full_name', 'email', 'enrollment_number', 'program_name'],
  statusField: 'is_active'
})

// Methods
const fetchStudents = () => studentService.getAllStudents()

const handleRefresh = () => refresh(fetchStudents)

const handleToggle = async (student) => {
  try {
    await toggleStatus(student, studentService.toggleStatus)
    showAlert('success', `Student status updated successfully`)
  } catch {
    showAlert('error', 'Failed to update status')
  }
}

const loadProgramCount = async () => {
  try {
    // This will return cached stats if available, or fetch them if missing
    const stats = await adminPanelService.getDashboardStats()
    totalPrograms.value = stats.programs || 0
  } catch (error) {
    console.error('Failed to load program count:', error)
  }
}

onMounted(() => {
  loadData(fetchStudents)
  loadProgramCount()
})
</script>

