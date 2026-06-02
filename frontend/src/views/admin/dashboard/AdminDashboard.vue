<template>
  <div class="mb-5">
    <h1 class="h2 fw-bold text-dark mb-2">Admin Dashboard</h1>
    <p class="text-muted mb-0">Welcome back! Here's what's happening today.</p>
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

  <!-- Charts Row -->
  <div class="row g-4 mb-5">
    <div class="col-lg-6">
      <DashboardChart
        title="User Growth (Last 6 Months)"
        type="line"
        :chart-data="userGrowthData"
        :loading="loadingCharts"
        @refresh="loadCharts"
      />
    </div>
    <div class="col-lg-6">
      <DashboardChart
        title="Course Enrollment Stats"
        type="bar"
        :chart-data="courseEnrollmentData"
        :loading="loadingCharts"
        @refresh="loadCharts"
      />
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/auth'
import { ActivityFeed, QuickActionCard, StatCard, AlertMessage, DashboardChart } from '@/components/shared/common'

import adminPanelService from '@/services/admin/adminPanelService'
import { useAlert } from '@/composables/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { CURRENCY } from '@/utils/constants/config'

const router = useRouter()
const authStore = useAuth()
const { alert } = useAlert()
const cachedStats = adminPanelService.getCachedStats()
const loading = ref(!cachedStats)
const loadingActivities = ref(true)
let dashboardRefreshTimer = null

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
  { value: stats.value.sessions, title: 'Total Sessions', icon: 'bi bi-calendar-event', type: 'finance', variant: 'glass', route: { name: ADMIN_ROUTES.SESSION_LIST.name } },
  { value: `${CURRENCY} ${Number(stats.value.revenue).toLocaleString()}`, title: 'Total Revenue', icon: 'bi bi-currency-dollar', type: 'finance', variant: 'glass', route: { name: ADMIN_ROUTES.FEES.name } }
])

const statsRow2 = computed(() => [
  { value: stats.value.departments, title: 'Departments', icon: 'bi bi-building', type: 'department', variant: 'glass', route: { name: ADMIN_ROUTES.DEPARTMENT_LIST.name } },
  { value: stats.value.programs, title: 'Total Programs', icon: 'bi bi-mortarboard', type: 'course', variant: 'glass', route: { name: ADMIN_ROUTES.COURSE_LIST.name } },
  { value: stats.value.subjects, title: 'Total Subjects', icon: 'bi bi-book', type: 'course', variant: 'glass', route: { name: ADMIN_ROUTES.SUBJECT_LIST.name } }
])

const recentActivities = ref([])

const chartRawData = ref({
  user_growth: { labels: [], students: [], teachers: [] },
  course_enrollment: { labels: [], values: [] }
})
const loadingCharts = ref(true)

const userGrowthData = computed(() => ({
  labels: chartRawData.value.user_growth?.labels || [],
  datasets: [
    {
      label: 'Students',
      data: chartRawData.value.user_growth?.students || [],
      borderColor: '#4f46e5',
      backgroundColor: 'rgba(79, 70, 229, 0.1)',
      tension: 0.3,
      fill: true
    },
    {
      label: 'Teachers',
      data: chartRawData.value.user_growth?.teachers || [],
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      tension: 0.3,
      fill: true
    }
  ]
}))

const courseEnrollmentData = computed(() => ({
  labels: chartRawData.value.course_enrollment?.labels || [],
  datasets: [
    {
      label: 'Students Enrolled',
      data: chartRawData.value.course_enrollment?.values || [],
      backgroundColor: '#3b82f6',
      borderRadius: 6
    }
  ]
}))

const loadCharts = async () => {
  try {
    loadingCharts.value = true
    chartRawData.value = await adminPanelService.getChartData()
  } catch (error) {
    console.error('Error loading charts:', error)
  } finally {
    loadingCharts.value = false
  }
}

const loadDashboard = async (forceRefresh = false) => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login' })
    return
  }

  try {
    if (!cachedStats) {
      loading.value = true
      loadingActivities.value = true
    }

    const { stats: dashboardStats, activities } = await adminPanelService.getDashboardStats(forceRefresh)
    
    stats.value = dashboardStats
    recentActivities.value = activities
    
    loading.value = false
    loadingActivities.value = false
    
    loadCharts()
  } catch (error) {
    console.error('Dashboard error:', error)
    loading.value = false
    loadingActivities.value = false
  }
}

const handleVisibilityRefresh = () => {
  if (document.visibilityState === 'visible') {
    loadDashboard(true)
  }
}

const handleWindowFocus = () => {
  loadDashboard(true)
}


onMounted(() => {
  loadDashboard()

  document.addEventListener('visibilitychange', handleVisibilityRefresh)
  window.addEventListener('focus', handleWindowFocus)

  dashboardRefreshTimer = setInterval(() => {
    if (document.visibilityState === 'visible') {
      loadDashboard(true)
    }
  }, 30000)
})

onUnmounted(() => {
  document.removeEventListener('visibilitychange', handleVisibilityRefresh)
  window.removeEventListener('focus', handleWindowFocus)
  if (dashboardRefreshTimer) {
    clearInterval(dashboardRefreshTimer)
    dashboardRefreshTimer = null
  }
})
</script>
