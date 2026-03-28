<template>
  <AdminPageTemplate
    title="Teacher Management"
    subtitle="View and manage all teacher records"
    icon="bi bi-person-workspace"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Teacher List"
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
        <div class="col-6 col-xl-4">
          <StatCard title="Total Teachers" :value="totalTeachers" icon="bi bi-person-workspace" type="teacher" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Active Teachers" :value="activeTeachers" icon="bi bi-check-circle" type="student" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Inactive Teachers" :value="inactiveTeachers" icon="bi bi-x-circle" type="finance" :is-positive="false" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        v-model:status-value="filters.status"
        search-placeholder="Search by name, email, or ID..."
        search-col-size="col-md-4 col-12"
        actions-col-size="col-md-2 col-6"
        :loading="loading"
        @refresh="handleRefresh"
        @reset="handleReset"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Department</label>
            <select v-model="filters.department" class="form-select" @change="applyFilters">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.name">{{ dept.name }}</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="filteredData"
      :loading="loading"
      loading-text="Loading teachers..."
      empty-icon="bi bi-inbox"
      empty-title="No teachers found"
      empty-subtitle="Try adjusting your filters or add a new teacher"
    >
      <template #cell-employee_id="{ value }">
        <span class="badge bg-light text-dark fw-semibold">{{ value }}</span>
      </template>

      <template #cell-full_name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-teacher me-2">{{ row.full_name?.charAt(0).toUpperCase() }}</div>
          <div>
            <div class="fw-semibold text-dark">{{ row.full_name }}</div>
            <small class="text-muted d-none d-md-block">{{ row.email }}</small>
          </div>
        </div>
      </template>

      <template #cell-department_name="{ value }">
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
          @view="router.push({ name: ADMIN_ROUTES.TEACHER_PROFILE.name, params: { id: row.id } })"
          @edit="router.push({ name: ADMIN_ROUTES.TEACHER_EDIT.name, params: { id: row.id } })"
          @delete="router.push({ name: ADMIN_ROUTES.TEACHER_DELETE.name, params: { id: row.id } })"
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert } from '@/composables/shared'
import { teacherService } from '@/services/shared'
import { api } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getActiveBadgeClass, getActiveStatusText } from '@/utils/badgeHelpers'
import adminPanelService from '@/services/admin/adminPanelService'

const router = useRouter()

// Use shared alert composable
const { alert, showAlert } = useAlert()

// Config
const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Teachers' }
]

const actions = [
  { label: 'Add Teacher', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.TEACHER_ADD.name }) }
]

const tableColumns = [
  { key: 'employee_id', label: 'ID' },
  { key: 'full_name', label: 'Name' },
  { key: 'department_name', label: 'Department', hideOnMobile: true },
  { key: 'qualification', label: 'Qualification', hideOnMobile: true, default: 'N/A' },
  { key: 'is_active', label: 'Status' },
  { key: 'edit_count', label: 'Edits', hideOnMobile: true },
  { key: 'created_at', label: 'Joined', type: 'date', hideOnMobile: true },
  { key: 'actions', label: 'Actions', center: true }
]

// Departments for filter
const departments = ref([])

// Use composable with custom filter
const {
  loading,
  filteredData,
  filters,
  stats,
  loadData,
  applyFilters,
  resetFilters,
  refresh,
  toggleStatus
} = useEntityList({
  cacheKey: 'teachers_list',
  searchFields: ['full_name', 'email', 'employee_id', 'department_name', 'qualification'],
  statusField: 'is_active',
  defaultFilters: { department: '' },
  customFilter: (data, filters) => {
    if (filters.department) {
      return data.filter(t => t.department_name === filters.department)
    }
    return data
  }
})

const totalTeachers = ref(0)
const loadTeacherStats = async () => {
    try {
        const dashboardStats = await adminPanelService.getDashboardStats()
        totalTeachers.value = dashboardStats.teachers || 0
    } catch (error) {
        console.error('Failed to load teacher stats:', error)
    }
}

const activeTeachers = computed(() => filteredData.value.filter(t => t.is_active).length)
const inactiveTeachers = computed(() => filteredData.value.filter(t => !t.is_active).length)

// Watch department filter
watch(() => filters.value.department, () => applyFilters())

// Methods
const fetchTeachers = () => teacherService.getAllTeachers()

const loadDepartments = async () => {
  const cached = cacheService.get('departments_list')
  if (cached) {
    departments.value = cached
    return
  }
  try {
    const response = await api.get('/departments/')
    const data = Array.isArray(response.data) ? response.data : (response.data.results || [])
    cacheService.set('departments_list', data)
    departments.value = data
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

const handleRefresh = () => refresh(fetchTeachers)

const handleReset = () => {
  filters.value.department = ''
  resetFilters()
}

const handleToggle = async (teacher) => {
  try {
    await toggleStatus(teacher, teacherService.toggleStatus)
    showAlert('success', 'Teacher status updated successfully')
  } catch {
    showAlert('error', 'Failed to update status')
  }
}

onMounted(() => {
  loadData(fetchTeachers)
  loadDepartments()
  loadTeacherStats()
})
</script>


