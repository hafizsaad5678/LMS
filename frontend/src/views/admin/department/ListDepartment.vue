<template>
  <AdminPageTemplate
    title="Department Management"
    subtitle="View and manage all academic departments"
    icon="bi bi-building"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Department List"
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
          <StatCard title="Total Departments" :value="stats.total" icon="bi bi-building" bg-color="bg-purple-light" icon-color="text-purple" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active" :value="stats.active" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Inactive" :value="stats.inactive" icon="bi bi-x-circle" bg-color="bg-warning-light" icon-color="text-warning" :is-positive="false" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Teachers" :value="totalTeachers" icon="bi bi-person-workspace" bg-color="bg-info-light" icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        v-model:status-value="filters.status"
        search-placeholder="Search by name, code, or head..."
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
      loading-text="Loading departments..."
      empty-icon="bi bi-building"
      empty-title="No departments found"
      empty-subtitle="Try adjusting your filters or add a new department"
    >
      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-dept me-2"><i class="bi bi-building"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
            <small class="text-muted d-none d-md-block">{{ row.code }}</small>
          </div>
        </div>
      </template>

      <template #cell-institution_name="{ value }">
        <span class="badge bg-light text-dark border">{{ value || 'N/A' }}</span>
      </template>

      <template #cell-program_count="{ value }">
        <span class="badge bg-info">{{ value || 0 }}</span>
      </template>

      <template #cell-teacher_count="{ value }">
        <span class="badge bg-secondary">{{ value || 0 }}</span>
      </template>

      <template #cell-is_active="{ row }">
        <span :class="['badge', getActiveBadgeClass(row.is_active)]">
          {{ getActiveStatusText(row.is_active) }}
        </span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="true"
          @view="router.push({ name: ADMIN_ROUTES.DEPARTMENT_PROFILE.name, params: { id: row.id } })"
          @edit="router.push({ name: ADMIN_ROUTES.DEPARTMENT_EDIT.name, params: { id: row.id } })"
          @delete="router.push({ name: ADMIN_ROUTES.DEPARTMENT_DELETE.name, params: { id: row.id } })"
          @toggle="handleToggle(row)"
        />
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ filteredData.length }} departments</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert } from '@/composables/shared'
import { departmentService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getActiveBadgeClass, getActiveStatusText } from '@/utils/badgeHelpers'

const router = useRouter()

// Use shared alert composable
const { alert, showAlert } = useAlert()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Departments' }
]

const actions = [
  { label: 'Add Department', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.DEPARTMENT_ADD.name }) }
]

const tableColumns = [
  { key: 'name', label: 'Department' },
  { key: 'head_of_department', label: 'HOD', hideOnMobile: true, default: 'Not Assigned' },
  { key: 'institution_name', label: 'Institution', hideOnMobile: true },
  { key: 'program_count', label: 'Programs', hideOnMobile: true, center: true },
  { key: 'teacher_count', label: 'Teachers', hideOnMobile: true, center: true },
  { key: 'is_active', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

// Use composable
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
  cacheKey: 'departments_list',
  searchFields: ['name', 'code', 'head_of_department'],
  statusField: 'is_active'
})

// Extra computed for total teachers
const totalTeachers = computed(() => 
  data.value.reduce((sum, d) => sum + (d.teacher_count || 0), 0)
)

// Methods
const fetchDepartments = () => departmentService.getAllDepartments()

const handleRefresh = () => refresh(fetchDepartments)

const handleToggle = async (dept) => {
  try {
    await toggleStatus(dept, departmentService.toggleStatus)
    showAlert('success', 'Department status updated successfully')
  } catch {
    showAlert('error', 'Failed to update status')
  }
}

onMounted(() => loadData(fetchDepartments))
</script>

