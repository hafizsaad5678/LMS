<template>
  <div class="mb-5">
    <h1 class="h2 fw-bold text-dark mb-2">Teacher Dashboard</h1>
    <p class="text-muted mb-0">Welcome back! Manage your classes and students.</p>
  </div>

  <!-- Stats Grid -->
  <div class="row g-4 mb-5">
    <div class="col-xl-3 col-md-6" v-for="stat in dashboardStats" :key="stat.title">
      <StatCard v-bind="stat" role="teacher" :loading="loading" @click="router.push(stat.route)" />
    </div>
  </div>

  <!-- Charts Row -->
  <div class="row g-4 mb-5">
    <div class="col-lg-6">
      <DashboardChart
        title="Student Performance (Average Marks)"
        type="bar"
        :chart-data="studentPerformanceData"
        :options="{
          scales: {
            y: {
              min: 0,
              max: 100,
              ticks: { stepSize: 20 }
            }
          }
        }"
        :loading="loadingCharts"
        @refresh="loadCharts"
      />
    </div>
    <div class="col-lg-6">
      <DashboardChart
        title="Assignment Completion Rate"
        type="doughnut"
        :chart-data="assignmentCompletionData"
        :loading="loadingCharts"
        @refresh="loadCharts"
      >
        <template #header-actions>
          <select 
            v-if="assignmentsList.length > 0"
            v-model="selectedAssignmentIndex"
            class="form-select form-select-sm border shadow-sm fw-medium px-3 py-1 bg-white"
            style="width: auto; max-width: 240px; font-size: 0.82rem; border-radius: 8px; border-color: rgba(99, 102, 241, 0.25) !important;"
          >
            <option v-for="(name, idx) in assignmentsList" :key="idx" :value="idx">
              {{ name }}
            </option>
          </select>
        </template>
      </DashboardChart>
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
import { ActivityFeed, QuickActionCard, StatCard, DashboardChart } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
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

const chartRawData = ref({
  student_performance: { labels: [], values: [] },
  assignment_completion: { labels: [], submitted: [], pending: [] }
})
const loadingCharts = ref(true)
const selectedAssignmentIndex = ref(0)

const assignmentsList = computed(() => {
  return chartRawData.value.assignment_completion?.labels || []
})

const studentPerformanceData = computed(() => ({
  labels: chartRawData.value.student_performance?.labels || [],
  datasets: [
    {
      label: 'Average Score (%)',
      data: chartRawData.value.student_performance?.values || [],
      backgroundColor: 'rgba(79, 70, 229, 0.85)',
      borderRadius: 6
    }
  ]
}))

const assignmentCompletionData = computed(() => {
  const labels = chartRawData.value.assignment_completion?.labels || []
  const submitted = chartRawData.value.assignment_completion?.submitted || []
  const pending = chartRawData.value.assignment_completion?.pending || []

  if (labels.length === 0 || selectedAssignmentIndex.value >= labels.length) {
    return { labels: [], datasets: [] }
  }

  const idx = selectedAssignmentIndex.value
  return {
    labels: ['Submitted', 'Pending'],
    datasets: [
      {
        data: [submitted[idx] || 0, pending[idx] || 0],
        backgroundColor: ['#10b981', '#f59e0b'],
        borderWidth: 0
      }
    ]
  }
})

const loadCharts = async () => {
  try {
    loadingCharts.value = true
    chartRawData.value = await teacherPanelService.getChartData()
    selectedAssignmentIndex.value = 0
  } catch (error) {
    console.error('Error loading charts:', error)
  } finally {
    loadingCharts.value = false
  }
}

const loadDashboard = async () => {
  try {
    const { stats: dStats, activities: activityList } = await teacherPanelService.getDashboardStats({ forceRefresh: false })
    
    stats.value = dStats
    recentActivities.value = activityList
    
    loading.value = false
    loadingActivities.value = false
    
    loadCharts()
  } catch (error) {
    console.error('Dashboard error:', error)
    loading.value = false
    loadingActivities.value = false
  }
}

onMounted(() => loadDashboard())
</script>
