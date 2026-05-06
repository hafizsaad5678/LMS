<template>
  <AdminPageTemplate
    title="Institution Management"
    subtitle="Manage all institutions in the system"
    icon="bi bi-bank2"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Institution List"
  >
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
      title="Delete Institution"
      :message="institutionToDelete ? `Are you sure you want to delete '${institutionToDelete.name}'? This action cannot be undone.` : 'Delete this institution?'"
      type="danger"
      theme="admin"
      confirm-text="Delete"
      @confirm="confirmDeleteInstitution"
    />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Institutions" :value="stats.total" icon="bi bi-bank2" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active" :value="stats.active" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Departments" :value="stats.totalDepartments" icon="bi bi-building" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Cities" :value="stats.uniqueCities" icon="bi bi-geo-alt" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        v-model:status-value="filters.status"
        search-placeholder="Search by name, code, or city..."
        preset="admin-list"
        :show-status-filter="true"
        :loading="loading"
        @refresh="loadInstitutions"
        @reset="resetFilters"
      />
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="filteredData"
      :loading="loading"
      loading-text="Loading institutions..."
      empty-icon="bi bi-bank2"
      empty-title="No institutions found"
      empty-subtitle="Add your first institution to get started"
    >
      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-institution me-2"><i class="bi bi-bank2"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
            <small class="text-muted d-none d-md-block">{{ row.code }}</small>
          </div>
        </div>
      </template>



      <template #cell-contact="{ row }">
        <div v-if="row.email || row.phone">
          <small class="text-muted d-block">{{ row.email }}</small>
          <small class="text-muted">{{ row.phone }}</small>
        </div>
        <span v-else class="text-muted">-</span>
      </template>

      <template #cell-is_active="{ row }">
        <span :class="['badge', getActiveBadgeClass(row.is_active)]">
          {{ getActiveStatusText(row.is_active) }}
        </span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="false"
          @view="router.push({ name: ADMIN_ROUTES.INSTITUTION_PROFILE.name, params: { id: row.id } })"
          @edit="router.push({ name: ADMIN_ROUTES.INSTITUTION_EDIT.name, params: { id: row.id } })"
          @delete="confirmDelete(row)"
        />
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ filteredData.length }} institutions</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { useEntityList, useAlert, useListStats } from '@/composables/shared'
import { institutionService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getActiveBadgeClass, getActiveStatusText } from '@/utils/badgeHelpers'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Institutions' }
]

const actions = [
  { label: 'Add Institution', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.INSTITUTION_ADD.name }) }
]

const tableColumns = [
  { key: 'name', label: 'Institution' },
  { key: 'city', label: 'City', hideOnMobile: true, default: '-' },
  { key: 'contact', label: 'Contact', hideOnMobile: true },
  { key: 'is_active', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

// Use shared alert composable
const { alert, showAlert } = useAlert()
const showConfirmDialog = ref(false)
const institutionToDelete = ref(null)

// Use composable for list logic
const {
  loading,
  data: institutions,
  filteredData,
  filters,
  loadData,
  resetFilters,
  refresh
} = useEntityList({
  cacheKey: 'institutions_list',
  searchFields: ['name', 'code', 'city'],
  statusField: 'is_active'
})

const listStats = useListStats(institutions)

const stats = listStats.summary({
  total: list => list.length,
  active: list => list.filter((institution) => institution.is_active).length,
  totalDepartments: list => list.reduce((sum, institution) => sum + (institution.department_count || 0), 0),
  uniqueCities: list => new Set(list.map((institution) => institution.city).filter(Boolean)).size
})

const fetchInstitutions = () => institutionService.getAllInstitutions()

const loadInstitutions = () => loadData(fetchInstitutions)

const confirmDelete = (inst) => {
  institutionToDelete.value = inst
  showConfirmDialog.value = true
}

const confirmDeleteInstitution = async () => {
  try {
    await institutionService.deleteInstitution(institutionToDelete.value.id)
    showAlert('success', 'Institution deleted successfully', 'Success')
    refresh(fetchInstitutions)
  } catch (error) {
    console.error('Error deleting institution:', error)
    showAlert('error', 'Failed to delete institution', 'Error')
  } finally {
    showConfirmDialog.value = false
    institutionToDelete.value = null
  }
}

onMounted(loadInstitutions)
</script>



