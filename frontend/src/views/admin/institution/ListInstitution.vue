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
        :show-status-filter="true"
        search-col-size="col-md-5 col-12"
        actions-col-size="col-md-4 col-12"
        :loading="loading"
        @refresh="loadInstitutions"
        @reset="resetFilters"
      />
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="filteredInstitutions"
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
            <small class="text-muted">{{ row.short_name || '-' }}</small>
          </div>
        </div>
      </template>

      <template #cell-code="{ value }">
        <span class="badge bg-dark">{{ value }}</span>
      </template>

      <template #cell-contact="{ row }">
        <div v-if="row.email || row.phone">
          <small class="text-muted d-block">{{ row.email }}</small>
          <small class="text-muted">{{ row.phone }}</small>
        </div>
        <span v-else class="text-muted">-</span>
      </template>

      <template #cell-is_active="{ row }">
        <span :class="['badge', row.is_active ? 'bg-success' : 'bg-secondary']">
          {{ row.is_active ? 'Active' : 'Inactive' }}
        </span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="false"
          @view="router.push(`/admin-dashboard/institution/${row.id}`)"
          @edit="router.push(`/admin-dashboard/institution/edit/${row.id}`)"
          @delete="confirmDelete(row)"
        />
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ filteredInstitutions.length }} institutions</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage } from '@/components/common'
import { institutionService } from '@/services/institutionService'
import cacheService from '@/services/cacheService'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Institutions' }
]

const actions = [
  { label: 'Add Institution', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push('/admin-dashboard/institution/add') }
]

const tableColumns = [
  { key: 'name', label: 'Institution' },
  { key: 'code', label: 'Code' },
  { key: 'city', label: 'City', hideOnMobile: true, default: '-' },
  { key: 'contact', label: 'Contact', hideOnMobile: true },
  { key: 'is_active', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(true)
const institutions = ref([])
const filters = ref({ search: '', status: '' })

const stats = computed(() => ({
  total: institutions.value.length,
  active: institutions.value.filter(i => i.is_active).length,
  totalDepartments: institutions.value.reduce((sum, i) => sum + (i.department_count || 0), 0),
  uniqueCities: new Set(institutions.value.map(i => i.city).filter(Boolean)).size
}))

const filteredInstitutions = computed(() => {
  let list = institutions.value
  
  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    list = list.filter(i => 
      i.name?.toLowerCase().includes(q) || 
      i.code?.toLowerCase().includes(q) ||
      i.city?.toLowerCase().includes(q)
    )
  }
  
  if (filters.value.status === 'active') {
    list = list.filter(i => i.is_active)
  } else if (filters.value.status === 'inactive') {
    list = list.filter(i => !i.is_active)
  }
  
  return list
})

// Cache key
const CACHE_KEY = 'institutions_list'

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadInstitutions = async (useCache = true) => {
  // Check cache first
  if (useCache) {
    const cached = cacheService.get(CACHE_KEY)
    if (cached) {
      institutions.value = cached
      return
    }
  }

  loading.value = true
  try {
    const data = await institutionService.getAllInstitutions()
    const result = Array.isArray(data) ? data : (data.results || [])
    
    // Store in cache
    cacheService.set(CACHE_KEY, result)
    institutions.value = result
  } catch (error) {
    console.error('Error loading institutions:', error)
    showAlert('danger', 'Failed to load institutions', 'Error')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = { search: '', status: '' }
}

const confirmDelete = (inst) => {
  if (confirm(`Are you sure you want to delete "${inst.name}"? This action cannot be undone.`)) {
    deleteInstitution(inst.id)
  }
}

const deleteInstitution = async (id) => {
  try {
    await institutionService.deleteInstitution(id)
    showAlert('success', 'Institution deleted successfully', 'Success')
    cacheService.clear(CACHE_KEY) // Invalidate cache
    loadInstitutions(false)
  } catch (error) {
    console.error('Error deleting institution:', error)
    showAlert('danger', 'Failed to delete institution', 'Error')
  }
}

// Debounce search filter
let searchTimeout = null
watch(() => filters.value.search, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // Trigger computed property recalculation
    filters.value = { ...filters.value }
  }, 300)
})

onMounted(loadInstitutions)
</script>


