<template>
  <AdminPageTemplate
    title="Academic Sessions"
    subtitle="Manage batches and intakes for all programs"
    icon="bi bi-calendar-check"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Session List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Sessions" :value="stats.total" icon="bi bi-list" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active" :value="stats.active" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Upcoming" :value="stats.upcoming" icon="bi bi-clock" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Completed" :value="stats.completed" icon="bi bi-archive" bg-color="bg-info-light" icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search sessions..."
        :show-status-filter="false"
        search-col-size="col-md-3 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="loadSessions"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Program Level</label>
            <select v-model="filters.program_level" class="form-select" @change="loadSessions">
              <option value="">All Levels</option>
              <option value="bachelor">Bachelor</option>
              <option value="master">Master</option>
              <option value="intermediate">Intermediate</option>
              <option value="phd">PhD</option>
              <option value="diploma">Diploma</option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Status</label>
            <select v-model="filters.status" class="form-select" @change="loadSessions">
              <option value="">All Statuses</option>
              <option value="upcoming">Upcoming</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="sessions"
      :loading="loading"
      loading-text="Loading sessions..."
      empty-icon="bi bi-calendar-check"
      empty-title="No sessions found"
      empty-subtitle="Create your first session to get started"
    >
      <template #cell-session_name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-session me-2"><i class="bi bi-calendar-check"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.session_name }}</div>
            <small class="text-muted">{{ row.session_code }}</small>
          </div>
        </div>
      </template>

      <template #cell-program_name="{ row }">
        <div>
          <div>{{ row.program_name }}</div>
          <span :class="getProgramLevelBadgeClass(row.program_level)">{{ row.program_level_display }}</span>
        </div>
      </template>

      <template #cell-years="{ row }">
        <span class="text-nowrap">{{ row.start_year }} - {{ row.end_year }}</span>
      </template>

      <template #cell-capacity="{ row }">
        <div class="capacity-indicator">
          <div class="d-flex justify-content-between mb-1">
            <small>{{ row.current_enrollment }}/{{ row.total_capacity }}</small>
            <small>{{ Math.round(row.capacity_percentage) }}%</small>
          </div>
          <div class="progress" style="height: 6px;">
            <div class="progress-bar" :class="getCapacityClass(row.capacity_percentage)" :style="{ width: row.capacity_percentage + '%' }"></div>
          </div>
        </div>
      </template>

      <template #cell-semester_count="{ row }">
        <span class="badge bg-info">{{ row.semester_count }}/{{ row.total_semesters }}</span>
      </template>

      <template #cell-status="{ row }">
        <span :class="getStatusBadgeClass(row.status)">{{ row.status }}</span>
      </template>

      <template #cell-actions="{ row }">
        <div class="d-flex gap-1 justify-content-center flex-wrap">
          <router-link :to="`/admin-dashboard/sessions/profile/${row.id}`" class="btn btn-sm btn-outline-info" title="View"><i class="bi bi-eye"></i></router-link>
          <router-link :to="`/admin-dashboard/sessions/edit/${row.id}`" class="btn btn-sm btn-outline-primary" title="Edit"><i class="bi bi-pencil"></i></router-link>
          <button v-if="row.semester_count === 0" @click="setupSemesters(row)" class="btn btn-sm btn-success" title="Setup Semesters"><i class="bi bi-gear"></i></button>
          <button @click="confirmDelete(row)" class="btn btn-sm btn-outline-danger" title="Delete"><i class="bi bi-trash"></i></button>
        </div>
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ sessions.length }} sessions</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter } from '@/components/common'
import sessionService from '@/services/sessionService'
import cacheService from '@/services/cacheService'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Sessions' }
]

const actions = [
  { label: 'Create Session', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push('/admin-dashboard/sessions/add') }
]

const tableColumns = [
  { key: 'session_name', label: 'Session' },
  { key: 'program_name', label: 'Program', hideOnMobile: true },
  { key: 'years', label: 'Years' },
  { key: 'capacity', label: 'Capacity', hideOnMobile: true },
  { key: 'semester_count', label: 'Semesters' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const loading = ref(false)
const sessions = ref([])
const stats = ref({ total: 0, active: 0, upcoming: 0, completed: 0 })
const filters = ref({ program_level: '', status: '', search: '' })

// Cache key
const CACHE_KEY = 'sessions_list'

const loadSessions = async (useCache = true) => {
  // Check cache first (only if no filters applied)
  const hasFilters = filters.value.program_level || filters.value.status || filters.value.search
  
  if (useCache && !hasFilters) {
    const cached = cacheService.get(CACHE_KEY)
    if (cached) {
      sessions.value = cached
      return
    }
  }

  loading.value = true
  try {
    const params = {}
    if (filters.value.program_level) params.program__program_level = filters.value.program_level
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    
    const response = await sessionService.getSessions(params)
    const data = Array.isArray(response.data) ? response.data : (response.data.results || [])
    
    // Only cache if no filters applied
    if (!hasFilters) {
      cacheService.set(CACHE_KEY, data)
    }
    
    sessions.value = data
  } catch (error) {
    console.error('Error loading sessions:', error)
    alert('Failed to load sessions')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const [allSessions, activeSessions, upcomingSessions] = await Promise.all([
      sessionService.getSessions(),
      sessionService.getActiveSessions(),
      sessionService.getUpcomingSessions()
    ])
    
    const all = Array.isArray(allSessions.data) ? allSessions.data : (allSessions.data.results || [])
    const active = Array.isArray(activeSessions.data) ? activeSessions.data : (activeSessions.data.results || [])
    const upcoming = Array.isArray(upcomingSessions.data) ? upcomingSessions.data : (upcomingSessions.data.results || [])
    
    stats.value = {
      total: all.length,
      active: active.length,
      upcoming: upcoming.length,
      completed: all.filter(s => s.status === 'completed').length
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const setupSemesters = async (session) => {
  if (!confirm(`Auto-create ${session.total_semesters} semesters for ${session.session_name}?`)) return
  
  try {
    await sessionService.setupSemesters(session.id)
    alert(`Successfully created semesters for ${session.session_name}`)
    cacheService.clear(CACHE_KEY) // Invalidate cache
    loadSessions(false)
  } catch (error) {
    console.error('Error setting up semesters:', error)
    alert(error.response?.data?.error || 'Failed to setup semesters')
  }
}

const confirmDelete = (session) => {
  if (confirm(`Are you sure you want to delete ${session.session_name}?`)) {
    deleteSession(session.id)
  }
}

const deleteSession = async (id) => {
  try {
    await sessionService.deleteSession(id)
    alert('Session deleted successfully')
    cacheService.clear(CACHE_KEY) // Invalidate cache
    loadSessions(false)
    loadStats()
  } catch (error) {
    console.error('Error deleting session:', error)
    alert('Failed to delete session')
  }
}

const resetFilters = () => {
  filters.value = { program_level: '', status: '', search: '' }
  loadSessions()
}

const getProgramLevelBadgeClass = (level) => {
  const classes = { bachelor: 'badge bg-primary', master: 'badge bg-purple', intermediate: 'badge bg-warning', phd: 'badge bg-danger', diploma: 'badge bg-success' }
  return classes[level] || 'badge bg-secondary'
}

const getStatusBadgeClass = (status) => {
  const classes = { upcoming: 'badge bg-warning', active: 'badge bg-success', completed: 'badge bg-secondary', archived: 'badge bg-dark' }
  return classes[status] || 'badge bg-info'
}

const getCapacityClass = (percentage) => {
  if (percentage >= 90) return 'bg-danger'
  if (percentage >= 75) return 'bg-warning'
  return 'bg-success'
}

// Debounce search filter
let searchTimeout = null
watch(() => filters.value.search, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadSessions()
  }, 300)
})

// Watch other filters without debounce
watch(() => [filters.value.program_level, filters.value.status], () => {
  loadSessions()
})

onMounted(() => {
  loadSessions()
  loadStats()
})
</script>


