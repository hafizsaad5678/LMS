<template>
  <AdminPageTemplate
    title="Department Management"
    subtitle="View and manage all academic departments"
    icon="bi bi-building"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Department List"
  >
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
          <StatCard title="Total Teachers" :value="stats.totalTeachers" icon="bi bi-person-workspace" bg-color="bg-info-light" icon-color="text-info" />
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
        @refresh="loadDepartments"
        @reset="resetFilters"
      />
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="departments"
      :loading="loading"
      loading-text="Loading departments..."
      empty-icon="bi bi-building"
      empty-title="No departments found"
      empty-subtitle="Try adjusting your filters or add a new department"
    >
      <template #cell-code="{ value }">
        <span class="badge bg-dark fw-semibold">{{ value }}</span>
      </template>

      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-dept me-2"><i class="bi bi-building"></i></div>
          <div class="fw-semibold text-dark">{{ row.name }}</div>
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
        <span :class="['badge', row.is_active ? 'bg-success' : 'bg-warning']">
          {{ row.is_active ? 'Active' : 'Inactive' }}
        </span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="true"
          @view="router.push(`/admin-dashboard/departments/${row.id}`)"
          @edit="router.push(`/admin-dashboard/departments/edit/${row.id}`)"
          @delete="router.push(`/admin-dashboard/departments/delete/${row.id}`)"
          @toggle="toggleStatus(row)"
        />
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ departments.length }} departments</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons } from '@/components/common'
import { departmentService } from '@/services/departmentService'
import cacheService from '@/services/cacheService'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Departments' }
]

const actions = [
  { label: 'Add Department', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push('/admin-dashboard/departments/add') }
]

const tableColumns = [
  { key: 'code', label: 'Code' },
  { key: 'name', label: 'Department' },
  { key: 'head_of_department', label: 'HOD', hideOnMobile: true, default: 'Not Assigned' },
  { key: 'institution_name', label: 'Institution', hideOnMobile: true },
  { key: 'program_count', label: 'Programs', hideOnMobile: true },
  { key: 'teacher_count', label: 'Teachers', hideOnMobile: true },
  { key: 'is_active', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const loading = ref(true)
const departments = ref([])
const filters = ref({ search: '', status: '' })

const stats = computed(() => {
  const total = departments.value.length
  const active = departments.value.filter(d => d.is_active).length
  const totalTeachers = departments.value.reduce((sum, d) => sum + (d.teacher_count || 0), 0)
  return { total, active, inactive: total - active, totalTeachers }
})

// Cache key
const CACHE_KEY = 'departments_list'

const loadDepartments = async (useCache = true) => {
  // Check cache first
  if (useCache) {
    const cached = cacheService.get(CACHE_KEY)
    if (cached) {
      applyFilters(cached)
      return
    }
  }

  loading.value = true
  try {
    const response = await departmentService.getAllDepartments()
    const data = Array.isArray(response) ? response : (response.results || response.data || [])
    
    // Store in cache
    cacheService.set(CACHE_KEY, data)
    applyFilters(data)
  } catch (error) {
    console.error('Error loading departments:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = (sourceData = null) => {
  // Use provided data or get from cache
  const cachedData = sourceData || cacheService.get(CACHE_KEY) || []
  let data = [...cachedData]
  
  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    data = data.filter(d => 
      d.name?.toLowerCase().includes(q) || 
      d.code?.toLowerCase().includes(q) || 
      d.head_of_department?.toLowerCase().includes(q)
    )
  }
  
  if (filters.value.status) {
    const isActive = filters.value.status === 'active'
    data = data.filter(d => d.is_active === isActive)
  }
  
  departments.value = data
}

const resetFilters = () => {
  filters.value = { search: '', status: '' }
  applyFilters()
}

const toggleStatus = async (dept) => {
  try {
    await departmentService.toggleStatus(dept.id)
    cacheService.clear(CACHE_KEY) // Invalidate cache
    await loadDepartments(false)
  } catch (error) {
    console.error('Error toggling status:', error)
    alert('Failed to update status')
  }
}

// Debounce search filter
let searchTimeout = null
watch(() => filters.value.search, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 300)
})

// Watch other filters without debounce
watch(() => filters.value.status, () => {
  applyFilters()
})

onMounted(loadDepartments)
</script>


