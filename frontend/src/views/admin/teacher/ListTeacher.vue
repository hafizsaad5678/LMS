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
        search-placeholder="Search by name, email, or ID..."
        preset="admin-list"
        :show-status-filter="false"
        :loading="loading"
        @refresh="handleRefresh"
        @reset="handleReset"
      >
        <template #filters>
          <SelectInput
            v-model="filters.department"
            label="Department"
            placeholder="All Departments"
            :options="departments"
            option-value-key="name"
            option-label-key="name"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
          <SelectInput
            v-model="filters.designation"
            label="Designation"
            placeholder="All Designations"
            :options="designationOptions"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, SelectInput, ActionButtons, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert, useFilterOptions, useListStats } from '@/composables/shared'
import { teacherService } from '@/services/shared'
import { api } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getActiveBadgeClass, getActiveStatusText } from '@/utils/badgeHelpers'

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
  { key: 'actions', label: 'Actions', center: true }
]

// Departments for filter
const departments = ref([])

// Use composable with custom filter
const {
  loading,
  data,
  filteredData,
  filters,
  stats,
  loadData,
  resetFilters,
  refresh,
  toggleStatus
} = useEntityList({
  cacheKey: 'teachers_list',
  searchFields: ['full_name', 'email', 'employee_id', 'department_name', 'qualification'],
  statusField: 'is_active',
  defaultFilters: { department: '', designation: '' },
  filterSchema: [
    {
      key: 'department',
      itemValue: 'department_name',
      normalize: value => String(value || '').trim()
    },
    {
      key: 'designation',
      itemValue: 'designation',
      normalize: value => String(value || '').trim()
    }
  ]
})

const totalTeachers = computed(() => stats.value.total)

const listStats = useListStats(filteredData)

const activeTeachers = listStats.count((teacher) => teacher.is_active)
const inactiveTeachers = listStats.count((teacher) => !teacher.is_active)

const { createPrimitiveOptions } = useFilterOptions(data)

const designationOptions = createPrimitiveOptions({ value: 'designation' })

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

const handleReset = () => resetFilters()

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
})
</script>


