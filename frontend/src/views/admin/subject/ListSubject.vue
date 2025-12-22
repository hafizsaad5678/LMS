<template>
  <AdminPageTemplate
    title="Subject Management"
    subtitle="View and manage all academic subjects"
    icon="bi bi-book"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Subject List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Subjects" :value="stats.total" icon="bi bi-book" bg-color="bg-primary-light" icon-color="text-primary" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Credits" :value="stats.totalCredits" icon="bi bi-clock" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Avg Credits" :value="stats.avgCredits" icon="bi bi-bar-chart" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Semesters" :value="stats.uniqueSemesters" icon="bi bi-calendar3" bg-color="bg-warning-light" icon-color="text-warning" />
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
        @refresh="loadSubjects"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4 col-6">
            <label class="form-label small fw-semibold text-dark">Credit Hours</label>
            <select v-model="filters.credits" class="form-select" @change="loadSubjects">
              <option value="">All Credits</option>
              <option value="1">1 Credit</option>
              <option value="2">2 Credits</option>
              <option value="3">3 Credits</option>
              <option value="4">4 Credits</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="subjects"
      :loading="loading"
      loading-text="Loading subjects..."
      empty-icon="bi bi-book"
      empty-title="No subjects found"
      empty-subtitle="Try adjusting your filters or add a new subject"
    >
      <template #cell-code="{ value }">
        <span class="badge bg-dark fw-semibold">{{ value }}</span>
      </template>

      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-subject me-2"><i class="bi bi-book"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
            <small class="text-muted d-none d-md-block">{{ truncate(row.description, 30) }}</small>
          </div>
        </div>
      </template>

      <template #cell-semester_name="{ value }">
        <span class="badge bg-info">{{ value || 'N/A' }}</span>
      </template>

      <template #cell-credit_hours="{ value }">
        <span class="fw-semibold"><i class="bi bi-clock text-muted me-1"></i>{{ value }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="false"
          @view="router.push(`/admin-dashboard/subjects/${row.id}`)"
          @edit="router.push(`/admin-dashboard/subjects/edit/${row.id}`)"
          @delete="router.push(`/admin-dashboard/subjects/delete/${row.id}`)"
        />
      </template>
    </DataTable>

    <template #footer>
      <div class="d-flex justify-content-between flex-wrap gap-2">
        <p class="text-muted small mb-0">Total: {{ subjects.length }} subjects</p>
        <p class="text-muted small mb-0">Credits: {{ stats.totalCredits }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons } from '@/components/common'
import { subjectService } from '@/services/subjectService'
import cacheService from '@/services/cacheService'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Subjects' }
]

const actions = [
  { label: 'Add Subject', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push('/admin-dashboard/subjects/add') }
]

const tableColumns = [
  { key: 'code', label: 'Code' },
  { key: 'name', label: 'Subject' },
  { key: 'semester_name', label: 'Semester', hideOnMobile: true },
  { key: 'program_name', label: 'Program', hideOnMobile: true, default: 'N/A' },
  { key: 'credit_hours', label: 'Credits' },
  { key: 'actions', label: 'Actions', center: true }
]

const loading = ref(true)
const subjects = ref([])
const filters = ref({ search: '', credits: '' })

const stats = computed(() => {
  const total = subjects.value.length
  const totalCredits = subjects.value.reduce((sum, s) => sum + (s.credit_hours || 0), 0)
  const avgCredits = total > 0 ? (totalCredits / total).toFixed(1) : 0
  const uniqueSemesters = new Set(subjects.value.map(s => s.semester)).size
  return { total, totalCredits, avgCredits, uniqueSemesters }
})

// Cache key
const CACHE_KEY = 'subjects_list'

const loadSubjects = async (useCache = true) => {
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
    const response = await subjectService.getAllSubjects()
    const data = Array.isArray(response) ? response : (response.results || response.data || [])
    
    // Store in cache
    cacheService.set(CACHE_KEY, data)
    applyFilters(data)
  } catch (error) {
    console.error('Error loading subjects:', error)
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
    data = data.filter(s => s.name?.toLowerCase().includes(q) || s.code?.toLowerCase().includes(q))
  }
  
  if (filters.value.credits) {
    const credits = parseInt(filters.value.credits)
    data = data.filter(s => s.credit_hours === credits)
  }
  
  subjects.value = data
}

const resetFilters = () => {
  filters.value = { search: '', credits: '' }
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

// Watch credits filter without debounce
watch(() => filters.value.credits, () => {
  applyFilters()
})

onMounted(loadSubjects)
</script>


