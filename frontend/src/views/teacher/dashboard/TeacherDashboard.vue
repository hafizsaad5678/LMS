<template>
  <div class="d-flex justify-content-between align-items-center mb-5">
    <div>
      <h1 class="h2 fw-bold text-dark mb-2">Teacher Dashboard</h1>
      <p class="text-muted mb-0">Welcome back! Manage your classes and students.</p>
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
          placeholder="Search students..." 
          @keyup.enter="handleSearch"
        >
        <button @click="handleSearch" class="btn btn-teacher-primary px-3">
          <i class="bi bi-arrow-right"></i>
        </button>
      </div>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="row g-4 mb-5">
    <div class="col-xl-3 col-md-6" v-for="stat in dashboardStats" :key="stat.title">
      <StatCard v-bind="stat" role="teacher" :loading="loading" @click="router.push(stat.route)" />
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
                title="Create Assignment"
                description="Add new assignment"
                icon="bi bi-file-plus"
                bg-gradient="bg-light"
                icon-bg-color="bg-teacher-light"
                icon-color="text-teacher"
                @click="router.push({ name: TEACHER_ROUTES.ASSIGNMENT_CREATE.name })"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="Grade Students"
                description="Review student work"
                icon="bi bi-check-circle"
                bg-gradient="bg-light"
                icon-bg-color="bg-success-light"
                icon-color="text-success"
                @click="router.push({ name: TEACHER_ROUTES.GRADE_STUDENTS.name })"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="View Classes"
                description="Manage your classes"
                icon="bi bi-book"
                bg-gradient="bg-light"
                icon-bg-color="bg-info-light"
                icon-color="text-info"
                @click="router.push({ name: TEACHER_ROUTES.CLASS_LIST.name })"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="Mark Attendance"
                description="Record attendance"
                icon="bi bi-calendar-check"
                bg-gradient="bg-light"
                icon-bg-color="bg-warning-light"
                icon-color="text-warning"
                @click="router.push({ name: TEACHER_ROUTES.MARK_ATTENDANCE.name })"
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
import { ActivityFeed, QuickActionCard, StatCard } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const searchQuery = ref('')
const loading = ref(true)
const loadingActivities = ref(true)

const stats = ref({
  totalClasses: 0,
  totalStudents: 0,
  pendingReviews: 0,
  upcomingDeadlines: 0
})

const dashboardStats = computed(() => [
  { value: stats.value.totalClasses, title: 'My Classes', icon: 'bi bi-book-half', type: 'teacher', variant: 'glass', route: { name: TEACHER_ROUTES.CLASS_LIST.name } },
  { value: stats.value.totalStudents, title: 'Total Students', icon: 'bi bi-people', type: 'student', variant: 'glass', route: { name: TEACHER_ROUTES.STUDENT_LIST.name } },
  { value: stats.value.pendingReviews, title: 'Pending Reviews', icon: 'bi bi-clipboard-check', type: 'finance', variant: 'glass', route: { name: TEACHER_ROUTES.ASSIGNMENT_LIST.name } },
  { value: stats.value.upcomingDeadlines, title: 'Due This Week', icon: 'bi bi-calendar-event', type: 'department', variant: 'glass', route: { name: TEACHER_ROUTES.ASSIGNMENT_LIST.name } }
])

const recentActivities = ref([])

const loadDashboard = async () => {
  try {
    // Load stats and activities in parallel
    const [dashboardStats, activities] = await Promise.all([
      teacherPanelService.getDashboardStats({ forceRefresh: true }),
      teacherPanelService.getRecentActivities()
    ])
    
    stats.value = {
      totalClasses: dashboardStats.totalClasses || 0,
      totalStudents: dashboardStats.totalStudents || 0,
      pendingReviews: dashboardStats.pendingReviews || 0,
      upcomingDeadlines: dashboardStats.upcomingDeadlines || 0
    }
    recentActivities.value = activities
    
    loading.value = false
    loadingActivities.value = false
  } catch (error) {
    console.error('Dashboard error:', error)
    loading.value = false
    loadingActivities.value = false
  }
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  router.push({ path: TEACHER_ROUTES.STUDENT_LIST.path, query: { search: searchQuery.value.trim() } })
}

onMounted(() => loadDashboard())
</script>
