<template>
  <AdminPageTemplate
    title="Course Management"
    subtitle="View and manage all academic programs/courses"
    icon="bi bi-mortarboard"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Course List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Courses" :value="stats.total" icon="bi bi-mortarboard" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Students" :value="stats.totalStudents" icon="bi bi-people" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Avg Duration" :value="stats.avgDuration + ' yrs'" icon="bi bi-calendar-range" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Semesters" :value="stats.totalSemesters" icon="bi bi-calendar3" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search by name or code..."
        :show-status-filter="false"
        search-col-size="col-md-5 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="loadCourses"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4 col-6">
            <label class="form-label small fw-semibold text-dark">Duration</label>
            <select v-model="filters.duration" class="form-select" @change="loadCourses">
              <option value="">All Durations</option>
              <option value="2">2 Years</option>
              <option value="3">3 Years</option>
              <option value="4">4 Years</option>
              <option value="5">5 Years</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="courses"
      :loading="loading"
      loading-text="Loading courses..."
      empty-icon="bi bi-mortarboard"
      empty-title="No courses found"
      empty-subtitle="Try adjusting your filters or add a new course"
    >
      <template #cell-code="{ value }">
        <span class="badge bg-dark fw-semibold">{{ value }}</span>
      </template>

      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-course me-2"><i class="bi bi-mortarboard"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
            <small class="text-muted d-none d-md-block">{{ truncate(row.description, 30) }}</small>
          </div>
        </div>
      </template>

      <template #cell-department_name="{ value }">
        <span class="badge bg-light text-dark border">{{ value || 'N/A' }}</span>
      </template>

      <template #cell-duration_years="{ value }">
        <span class="fw-semibold"><i class="bi bi-calendar-range text-muted me-1"></i>{{ value }} Years</span>
      </template>

      <template #cell-semester_count="{ value }">
        <span class="badge bg-info">{{ value || 0 }}</span>
      </template>

      <template #cell-student_count="{ value }">
        <span class="badge bg-success">{{ value || 0 }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="false"
          @view="router.push(`/admin-dashboard/courses/${row.id}`)"
          @edit="router.push(`/admin-dashboard/courses/edit/${row.id}`)"
          @delete="router.push(`/admin-dashboard/courses/delete/${row.id}`)"
        />
      </template>
    </DataTable>

    <template #footer>
      <div class="d-flex justify-content-between flex-wrap gap-2">
        <p class="text-muted small mb-0">Total: {{ courses.length }} courses</p>
        <p class="text-muted small mb-0">Students: {{ stats.totalStudents }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons } from '@/components/common'
import { programService } from '@/services/programService'
import cacheService from '@/services/cacheService'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Courses' }
]

const actions = [
  { label: 'Add Course', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push('/admin-dashboard/courses/add') }
]

const tableColumns = [
  { key: 'code', label: 'Code' },
  { key: 'name', label: 'Course' },
  { key: 'department_name', label: 'Department', hideOnMobile: true },
  { key: 'duration_years', label: 'Duration', hideOnMobile: true },
  { key: 'semester_count', label: 'Semesters' },
  { key: 'student_count', label: 'Students', hideOnMobile: true },
  { key: 'actions', label: 'Actions', center: true }
]

const loading = ref(true)
const courses = ref([])
const filters = ref({ search: '', duration: '' })

const stats = computed(() => {
  const total = courses.value.length
  const totalStudents = courses.value.reduce((sum, c) => sum + (c.student_count || 0), 0)
  const totalDuration = courses.value.reduce((sum, c) => sum + (c.duration_years || 0), 0)
  const avgDuration = total > 0 ? (totalDuration / total).toFixed(1) : 0
  const totalSemesters = courses.value.reduce((sum, c) => sum + (c.semester_count || 0), 0)
  return { total, totalStudents, avgDuration, totalSemesters }
})

// Cache key
const CACHE_KEY = 'courses_list'

const loadCourses = async (useCache = true) => {
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
    const response = await programService.getAllPrograms()
    const data = Array.isArray(response) ? response : (response.results || response.data || [])
    
    // Store in cache
    cacheService.set(CACHE_KEY, data)
    applyFilters(data)
  } catch (error) {
    console.error('Error loading courses:', error)
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
    data = data.filter(c => c.name?.toLowerCase().includes(q) || c.code?.toLowerCase().includes(q))
  }
  
  if (filters.value.duration) {
    const duration = parseInt(filters.value.duration)
    data = data.filter(c => c.duration_years === duration)
  }
  
  courses.value = data
}

const resetFilters = () => {
  filters.value = { search: '', duration: '' }
  applyFilters()
}

const truncate = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

// Debounce search filter
let searchTimeout = null
watch(() => filters.value.search, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 300)
})

// Watch duration filter without debounce
watch(() => filters.value.duration, () => {
  applyFilters()
})

onMounted(loadCourses)
</script>


