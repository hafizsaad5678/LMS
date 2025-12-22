<template>
  <AdminPageTemplate
    title="Semester Management"
    subtitle="View and manage academic semesters"
    icon="bi bi-calendar3"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Semester List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Semesters" :value="stats.total" icon="bi bi-calendar3" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Active" :value="stats.active" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Completed" :value="stats.completed" icon="bi bi-check2-all" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Programs" :value="stats.programs" icon="bi bi-mortarboard" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search by name..."
        :show-status-filter="false"
        search-col-size="col-md-5 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="loadSemesters"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4 col-6">
            <label class="form-label small fw-semibold text-dark">Program</label>
            <select v-model="filters.program" class="form-select" @change="loadSemesters">
              <option value="">All Programs</option>
              <option v-for="prog in programs" :key="prog.id" :value="prog.id">{{ prog.name }}</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="semesters"
      :loading="loading"
      loading-text="Loading semesters..."
      empty-icon="bi bi-calendar3"
      empty-title="No semesters found"
      empty-subtitle="Try adjusting your filters or add a new semester"
    >
      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-semester me-2"><i class="bi bi-calendar3"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
            <small class="text-muted">Semester {{ row.number }}</small>
          </div>
        </div>
      </template>

      <template #cell-program="{ row }">
        <span class="badge bg-light text-dark border">{{ row.program_name || getProgramName(row.program) }}</span>
      </template>

      <template #cell-start_date="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-end_date="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-status="{ row }">
        <span :class="['badge', getStatusBadgeClass(row.status)]">
          {{ getStatusLabel(row.status) }}
        </span>
      </template>

      <template #cell-subjects="{ row }">
        <span class="badge bg-info">{{ row.subject_count || 0 }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="false"
          @view="router.push({ name: 'SemesterProfile', params: { id: row.id } })"
          @edit="router.push({ name: 'EditSemester', params: { id: row.id } })"
          @delete="deleteSemester(row)"
        />
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ semesters.length }} semesters</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons } from '@/components/common'
import { semesterService } from '@/services/semesterService'
import { programService } from '@/services/programService'
import cacheService from '@/services/cacheService'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Semesters' }
]

const actions = [
  { label: 'Add Semester', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: 'AddSemester' }) }
]

const tableColumns = [
  { key: 'name', label: 'Semester' },
  { key: 'program', label: 'Program', hideOnMobile: true },
  { key: 'start_date', label: 'Start', hideOnMobile: true },
  { key: 'end_date', label: 'End', hideOnMobile: true },
  { key: 'status', label: 'Status' },
  { key: 'subjects', label: 'Subjects', center: true },
  { key: 'actions', label: 'Actions', center: true }
]

const loading = ref(false)
const semesters = ref([])
const programs = ref([])
const filters = ref({ search: '', program: '' })

const stats = computed(() => ({
  total: semesters.value.length,
  active: semesters.value.filter(s => s.status === 'active').length,
  completed: semesters.value.filter(s => s.status === 'completed').length,
  programs: new Set(semesters.value.map(s => s.program)).size
}))

// Cache keys
const CACHE_KEYS = {
  SEMESTERS: 'semesters_list',
  PROGRAMS: 'programs_list'
}

const loadSemesters = async (useCache = true) => {
  loading.value = true
  try {
    // Check cache for both semesters and programs
    let semList, progList
    
    if (useCache) {
      const cachedSem = cacheService.get(CACHE_KEYS.SEMESTERS)
      const cachedProg = cacheService.get(CACHE_KEYS.PROGRAMS)
      
      if (cachedSem && cachedProg) {
        semList = cachedSem
        progList = cachedProg
        programs.value = progList
        applyFilters(semList)
        loading.value = false
        return
      }
    }
    
    // Fetch from API if not cached
    const [semRes, progRes] = await Promise.all([
      semesterService.getAll(),
      programService.getAllPrograms()
    ])
    
    semList = semRes.results || semRes.data || semRes
    progList = progRes.results || progRes.data || progRes
    
    // Store in cache
    cacheService.set(CACHE_KEYS.SEMESTERS, semList)
    cacheService.set(CACHE_KEYS.PROGRAMS, progList)
    
    programs.value = progList
    applyFilters(semList)
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = (sourceData = null) => {
  // Use provided data or get from cache
  const cachedData = sourceData || cacheService.get(CACHE_KEYS.SEMESTERS) || []
  let list = [...cachedData]
  
  if (filters.value.program) {
    list = list.filter(s => String(s.program) === String(filters.value.program))
  }
  
  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    list = list.filter(s => s.name?.toLowerCase().includes(q))
  }
  
  semesters.value = list
}

const getProgramName = (programId) => {
  const semester = semesters.value.find(s => s.program === programId)
  if (semester?.program_name) return semester.program_name
  
  const p = programs.value.find(x => String(x.id) === String(programId))
  return p ? p.name : 'N/A'
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '-'

const getStatusBadgeClass = (status) => {
  const map = { draft: 'bg-secondary', active: 'bg-success', completed: 'bg-info', archived: 'bg-dark' }
  return map[status] || 'bg-secondary'
}

const getStatusLabel = (status) => {
  const map = { draft: 'Draft', active: 'Active', completed: 'Completed', archived: 'Archived' }
  return map[status] || status
}

const deleteSemester = async (sem) => {
  if (confirm(`Delete semester "${sem.name}"?`)) {
    try {
      await semesterService.delete(sem.id)
      cacheService.clear(CACHE_KEYS.SEMESTERS) // Invalidate cache
      loadSemesters(false)
    } catch (e) {
      console.error(e)
      alert('Failed to delete')
    }
  }
}

const resetFilters = () => {
  filters.value = { search: '', program: '' }
  applyFilters()
}

// Debounce search filter
let searchTimeout = null
watch(() => filters.value.search, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 300)
})

// Watch program filter without debounce
watch(() => filters.value.program, () => {
  applyFilters()
})

onMounted(loadSemesters)
</script>


