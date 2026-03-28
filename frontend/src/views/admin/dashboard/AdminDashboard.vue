<template>
  <div class="d-flex justify-content-between align-items-center mb-5">
    <div>
      <h1 class="h2 fw-bold text-dark mb-2">Admin Dashboard</h1>
      <p class="text-muted mb-0">Welcome back! Here's what's happening today.</p>
    </div>
    
    <!-- Search Bar -->
    <div class="search-container position-relative">
      <div class="input-group">
        <span class="input-group-text bg-white border-end-0 ps-3">
          <i class="bi bi-search text-muted"></i>
        </span>
        <input 
          v-model="searchQuery" 
          type="text" 
          class="form-control border-start-0 ps-0" 
          placeholder="Search profiles..." 
          @keyup.enter="handleSearch"
        >
        <button @click="handleSearch" class="btn btn-admin-primary px-3" :disabled="loadingSearch">
          <i class="bi bi-arrow-right"></i>
        </button>
      </div>
      <div v-if="loadingSearch" class="position-absolute top-100 start-0 w-100 mt-1">
        <div class="progress search-progress">
          <div class="progress-bar progress-bar-striped progress-bar-animated w-100 bg-admin"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Alert Message -->
  <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />

  <!-- Stats Grid Row 1 -->
  <div class="row g-4 mb-4">
    <div class="col-xl-3 col-md-6" v-for="stat in statsRow1" :key="stat.title">
      <StatCard v-bind="stat" role="admin" :loading="loading" @click="router.push(stat.route)" />
    </div>
  </div>

  <!-- Stats Grid Row 2 -->
  <div class="row g-4 mb-5">
    <div class="col-xl-3 col-md-4" v-for="stat in statsRow2" :key="stat.title">
      <StatCard v-bind="stat" role="admin" :loading="loading" @click="router.push(stat.route)" />
    </div>
  </div>

  <!-- Content Grid -->
  <div class="row g-4">
    <div class="col-lg-6">
      <ActivityFeed :activities="recentActivities" :loading="loadingActivities" />
    </div>

    <div class="col-lg-6">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <h5 class="card-title fw-semibold text-dark mb-4">Quick Actions</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <QuickActionCard
                title="Add Student"
                description="Enroll new student"
                icon="bi bi-person-plus"
                bg-gradient="bg-light"
                icon-bg-color="bg-admin-light"
                icon-color="text-admin"
                @click="router.push({ name: ADMIN_ROUTES.STUDENT_ADD.name })"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="Add Teacher"
                description="Register new teacher"
                icon="bi bi-person-badge"
                bg-gradient="bg-light"
                icon-bg-color="bg-success-light"
                icon-color="text-success"
                @click="router.push({ name: ADMIN_ROUTES.TEACHER_ADD.name })"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="Add Department"
                description="Create new department"
                icon="bi bi-building"
                bg-gradient="bg-light"
                icon-bg-color="bg-info-light"
                icon-color="text-info"
                @click="router.push({ name: ADMIN_ROUTES.DEPARTMENT_ADD.name })"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="Collect Fees"
                description="Process payments"
                icon="bi bi-currency-dollar"
                bg-gradient="bg-light"
                icon-bg-color="bg-warning-light"
                icon-color="text-warning"
                @click="router.push({ name: ADMIN_ROUTES.FEES.name })"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/auth'
import { ActivityFeed, QuickActionCard, StatCard, AlertMessage } from '@/components/shared/common'
import { useAlert } from '@/composables/shared'
import adminPanelService from '@/services/admin/adminPanelService'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { CURRENCY } from '@/utils/constants/config'

const router = useRouter()
const authStore = useAuth()
const { alert, showAlert } = useAlert()
const searchQuery = ref('')
const loadingSearch = ref(false)
const cachedStats = adminPanelService.getCachedStats()
const loading = ref(!cachedStats)
const loadingActivities = ref(true)

const stats = ref({
  students: cachedStats?.students || 0,
  teachers: cachedStats?.teachers || 0,
  departments: cachedStats?.departments || 0,
  revenue: cachedStats?.revenue || 0,
  sessions: cachedStats?.sessions || 0,
  programs: cachedStats?.programs || 0,
  subjects: cachedStats?.subjects || 0
})

const statsRow1 = computed(() => [
  { value: stats.value.students, title: 'Total Students', icon: 'bi bi-people', type: 'student', variant: 'glass', route: { name: ADMIN_ROUTES.STUDENT_LIST.name } },
  { value: stats.value.teachers, title: 'Total Teachers', icon: 'bi bi-person-badge', type: 'teacher', variant: 'glass', route: { name: ADMIN_ROUTES.TEACHER_LIST.name } },
  { value: stats.value.sessions, title: 'Active Sessions', icon: 'bi bi-calendar-event', type: 'finance', variant: 'glass', route: { name: ADMIN_ROUTES.SESSION_LIST.name } }, // Use finance/greenish for sessions
  { value: `${CURRENCY} ${Number(stats.value.revenue).toLocaleString()}`, title: 'Total Revenue', icon: 'bi bi-currency-dollar', type: 'finance', variant: 'glass', route: { name: ADMIN_ROUTES.FEES.name } }
])

const statsRow2 = computed(() => [
  { value: stats.value.departments, title: 'Departments', icon: 'bi bi-building', type: 'department', variant: 'glass', route: { name: ADMIN_ROUTES.DEPARTMENT_LIST.name } },
  { value: stats.value.programs, title: 'Total Programs', icon: 'bi bi-mortarboard', type: 'course', variant: 'glass', route: { name: ADMIN_ROUTES.COURSE_LIST.name } },
  { value: stats.value.subjects, title: 'Total Subjects', icon: 'bi bi-book', type: 'course', variant: 'glass', route: { name: ADMIN_ROUTES.SUBJECT_LIST.name } }
])

const recentActivities = ref([])

const loadDashboard = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login' })
    return
  }

  try {
    if (!cachedStats) loading.value = true
    const dashboardStats = await adminPanelService.getDashboardStats()
    stats.value = dashboardStats
    loading.value = false

    // Load activities in parallel (no setTimeout needed)
    loadActivities()
  } catch (error) {
    console.error('Dashboard error:', error)
    loading.value = false
    loadingActivities.value = false
  }
}

const loadActivities = async () => {
  try {
    recentActivities.value = await adminPanelService.getRecentActivities()
  } catch (error) {
    console.error('Activities error:', error)
  } finally {
    loadingActivities.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  loadingSearch.value = true
  const query = searchQuery.value.toLowerCase()
  
  try {
    const { students, teachers } = await adminPanelService.searchProfiles(query)
    if (students.length > 0) {
      if (students.length === 1) router.push({ name: ADMIN_ROUTES.STUDENT_PROFILE.name, params: { id: students[0].id } })
      else router.push({ path: ADMIN_ROUTES.STUDENT_LIST.path, query: { search: query } })
      return
    }
    if (teachers.length > 0) {
      if (teachers.length === 1) router.push({ name: ADMIN_ROUTES.TEACHER_PROFILE.name, params: { id: teachers[0].id } })
      else router.push({ path: ADMIN_ROUTES.TEACHER_LIST.path, query: { search: query } })
      return
    }
    showAlert('info', 'No direct profile found. Try browsing the lists.', 'Search')
  } catch (error) { console.error('Search error:', error) }
  finally { loadingSearch.value = false }
}

onMounted(() => loadDashboard())
</script>
