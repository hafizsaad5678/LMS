<template>
  <AdminPageTemplate
    title="Student Management"
    subtitle="View and manage all student records"
    icon="bi bi-people-fill"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Student List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Students" :value="stats.total" icon="bi bi-people" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active Students" :value="stats.active" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Inactive" :value="stats.inactive" icon="bi bi-x-circle" bg-color="bg-warning-light" icon-color="text-warning" :is-positive="false" />
        </div>
      </div>
    </template>

    <!-- Filters Section - Using SearchFilter Component -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        v-model:status-value="filters.status"
        search-placeholder="Search by name, email, or enrollment number..."
        :loading="loading"
        @refresh="loadStudents"
        @reset="resetFilters"
      />
    </template>

    <!-- Main Content - Using DataTable Component -->
    <DataTable
      :columns="tableColumns"
      :data="students"
      :loading="loading"
      loading-text="Loading students..."
      empty-icon="bi bi-inbox"
      empty-title="No students found"
      empty-subtitle="Try adjusting your filters or add a new student"
    >
      <!-- Custom cell for ID -->
      <template #cell-enrollment_number="{ value }">
        <span class="badge bg-light text-dark fw-semibold">{{ value }}</span>
      </template>

      <!-- Custom cell for Name with Avatar -->
      <template #cell-full_name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle me-2">{{ row.full_name?.charAt(0).toUpperCase() }}</div>
          <div class="fw-semibold text-dark">{{ row.full_name }}</div>
        </div>
      </template>

      <!-- Custom cell for Program -->
      <template #cell-program_name="{ value }">
        <span class="badge bg-info-light text-info">{{ value || 'N/A' }}</span>
      </template>

      <!-- Custom cell for Email -->
      <template #cell-email="{ value }">
        <a :href="`mailto:${value}`" class="text-decoration-none d-none d-md-inline">{{ value }}</a>
        <span class="d-md-none">{{ value?.split('@')[0] }}</span>
      </template>

      <!-- Custom cell for Status -->
      <template #cell-is_active="{ row }">
        <span :class="['badge', row.is_active ? 'bg-success' : 'bg-warning']">
          {{ row.is_active ? 'Active' : 'Inactive' }}
        </span>
      </template>

      <!-- Custom cell for Edit Count -->
      <template #cell-edit_count="{ value }">
        <span class="badge bg-light text-dark border">{{ value || 0 }}</span>
      </template>

      <!-- Actions Column -->
      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="true"
          @view="router.push(`/admin-dashboard/students/${row.id}`)"
          @edit="router.push(`/admin-dashboard/students/edit/${row.id}`)"
          @delete="router.push(`/admin-dashboard/students/delete/${row.id}`)"
          @toggle="toggleStatus(row)"
        />
      </template>
    </DataTable>

    <!-- Footer -->
    <template #footer>
      <div class="d-flex justify-content-end">
        <p class="text-muted small mb-0">Total Records: {{ students.length }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons } from '@/components/common'
import { studentService } from '@/services/studentservices'
import cacheService from '@/services/cacheService'

const router = useRouter()

// Config
const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Students' }
]

const actions = [
  { label: 'Add Student', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push('/admin-dashboard/students/add') }
]

const tableColumns = [
  { key: 'enrollment_number', label: 'ID' },
  { key: 'full_name', label: 'Name' },
  { key: 'program_name', label: 'Program', hideOnMobile: true, default: 'N/A' },
  { key: 'email', label: 'Email', hideOnMobile: true },
  { key: 'is_active', label: 'Status' },
  { key: 'created_at', label: 'Joined', type: 'date', hideOnMobile: true },
  { key: 'actions', label: 'Actions', center: true }
]

// State
const loading = ref(true)
const students = ref([])
const filters = ref({ search: '', status: '' })

const stats = computed(() => {
  const total = students.value.length
  const active = students.value.filter(s => s.is_active).length
  return { total, active, inactive: total - active }
})

// Cache key
const CACHE_KEY = 'students_list'

// Methods
const loadStudents = async (useCache = true) => {
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
    const response = await studentService.getAllStudents()
    const data = Array.isArray(response) ? response : (response.results || response.data || [])
    
    // Store in cache
    cacheService.set(CACHE_KEY, data)
    applyFilters(data)
  } catch (error) {
    console.error('Error loading students:', error)
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
    data = data.filter(s => 
      s.full_name?.toLowerCase().includes(q) || 
      s.email?.toLowerCase().includes(q) || 
      s.enrollment_number?.toLowerCase().includes(q)
    )
  }
  
  if (filters.value.status) {
    const isActive = filters.value.status === 'active'
    data = data.filter(s => s.is_active === isActive)
  }
  
  students.value = data
}

const resetFilters = () => {
  filters.value = { search: '', status: '' }
  applyFilters()
}

const toggleStatus = async (student) => {
  try {
    await studentService.toggleStatus(student.id)
    cacheService.clear(CACHE_KEY) // Invalidate cache
    await loadStudents(false)
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

onMounted(loadStudents)
</script>


