<template>
  <AdminPageTemplate
    title="Teacher Management"
    subtitle="View and manage all teacher records"
    icon="bi bi-person-workspace"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Teacher List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Teachers" :value="stats.total" icon="bi bi-person-workspace" bg-color="bg-primary-light" icon-color="text-primary" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active Teachers" :value="stats.active" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Inactive" :value="stats.inactive" icon="bi bi-x-circle" bg-color="bg-warning-light" icon-color="text-warning" :is-positive="false" />
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
        @refresh="loadTeachers"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Department</label>
            <select v-model="filters.department" class="form-select" @change="loadTeachers">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.name">{{ dept.name }}</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content - Using DataTable -->
    <DataTable
      :columns="tableColumns"
      :data="teachers"
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
        <span :class="['badge', row.is_active ? 'bg-success' : 'bg-warning']">
          {{ row.is_active ? 'Active' : 'Inactive' }}
        </span>
      </template>

      <template #cell-edit_count="{ value }">
        <span class="badge bg-light text-dark border">{{ value || 0 }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="true"
          @view="router.push(`/admin-dashboard/teachers/${row.id}`)"
          @edit="router.push(`/admin-dashboard/teachers/edit/${row.id}`)"
          @delete="router.push(`/admin-dashboard/teachers/delete/${row.id}`)"
          @toggle="toggleStatus(row)"
        />
      </template>
    </DataTable>

    <template #footer>
      <div class="d-flex justify-content-end">
        <p class="text-muted small mb-0">Total Records: {{ teachers.length }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons } from '@/components/common'
import { teacherService } from '@/services/teacherService'
import api from '@/services/api'
import cacheService from '@/services/cacheService'

const router = useRouter()

// Config
const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Teachers' }
]

const actions = [
  { label: 'Add Teacher', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push('/admin-dashboard/teachers/add') }
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

// State
const loading = ref(true)
const teachers = ref([])
const departments = ref([])
const filters = ref({ search: '', department: '', status: '' })

const stats = computed(() => {
  const total = teachers.value.length
  const active = teachers.value.filter(t => t.is_active).length
  return { total, active, inactive: total - active }
})

// Cache keys
const CACHE_KEYS = {
  TEACHERS: 'teachers_list',
  DEPARTMENTS: 'departments_list'
}

// Methods
const loadTeachers = async (useCache = true) => {
  // Check cache first
  if (useCache) {
    const cached = cacheService.get(CACHE_KEYS.TEACHERS)
    if (cached) {
      applyFilters(cached)
      return
    }
  }

  loading.value = true
  try {
    const response = await teacherService.getAllTeachers()
    const data = Array.isArray(response) ? response : (response.results || response.data || [])
    
    // Store in cache
    cacheService.set(CACHE_KEYS.TEACHERS, data)
    applyFilters(data)
  } catch (error) {
    console.error('Error loading teachers:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = (sourceData = null) => {
  // Use provided data or get from cache
  const cachedData = sourceData || cacheService.get(CACHE_KEYS.TEACHERS) || []
  let data = [...cachedData]
  
  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    data = data.filter(t => 
      t.full_name?.toLowerCase().includes(q) || 
      t.email?.toLowerCase().includes(q) || 
      t.employee_id?.toLowerCase().includes(q)
    )
  }
  
  if (filters.value.department) {
    data = data.filter(t => t.department_name === filters.value.department)
  }

  if (filters.value.status) {
    const isActive = filters.value.status === 'active'
    data = data.filter(t => t.is_active === isActive)
  }
  
  teachers.value = data
}

const loadDepartments = async () => {
  // Check cache first
  const cached = cacheService.get(CACHE_KEYS.DEPARTMENTS)
  if (cached) {
    departments.value = cached
    return
  }

  try {
    const response = await api.get('/departments/')
    const data = Array.isArray(response.data) ? response.data : (response.data.results || [])
    
    // Store in cache
    cacheService.set(CACHE_KEYS.DEPARTMENTS, data)
    departments.value = data
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

const resetFilters = () => {
  filters.value = { search: '', department: '', status: '' }
  applyFilters()
}

// Debounce search filter
let searchTimeout = null
watch(() => filters.value.search, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 300) // Wait 300ms after user stops typing
})

// Watch other filters without debounce
watch(() => [filters.value.department, filters.value.status], () => {
  applyFilters()
})

const toggleStatus = async (teacher) => {
  try {
    await teacherService.toggleStatus(teacher.id)
    teachersCache = [] // Invalidate cache
    await loadTeachers(false)
  } catch (error) {
    console.error('Error toggling status:', error)
    alert('Failed to update status')
  }
}

onMounted(() => {
  loadTeachers()
  loadDepartments()
})
</script>


