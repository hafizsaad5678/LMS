<template>
  <div class="d-flex justify-content-between align-items-center mb-5">
    <div>
      <h1 class="h2 fw-bold text-dark mb-0">Student Dashboard</h1>
      <p class="text-muted mb-0 small">Welcome back, {{ studentName }}!</p>
    </div>
    <div class="d-flex align-items-center gap-3">
      <button @click="handleAIChat" 
              class="btn-ai-premium">
        <div class="ai-icon-premium">
          <i class="bi bi-stars"></i>
        </div>
        <span>Ask AI Assistant</span>
      </button>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="row g-4 mb-5">
    <div class="col-xl-3 col-md-6" v-for="stat in dashboardStats" :key="stat.title">
      <StatCard v-bind="stat" role="student" :loading="loading" @click="$router.push(stat.route)" />
    </div>
    <div class="col-xl-3 col-md-6">
      <StatCard :value="stats.unreadAnnouncements" title="New Announcements" icon="bi bi-megaphone"
        bg-color="bg-danger-light" icon-color="text-danger" :loading="loading"
        @click="$router.push(STUDENT_ROUTES.ANNOUNCEMENTS.path)" />
    </div>
  </div>

  <!-- Content Grid -->
  <div class="row g-4">
    <div class="col-lg-6">
      <ActivityFeed :activities="activities" :loading="loadingActivities" />
    </div>

    <div class="col-lg-6">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <h5 class="card-title fw-semibold text-dark mb-4">Quick Actions</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <QuickActionCard title="GPA Calculator" description="Predict your GPA/CGPA"
                icon="bi bi-calculator-fill" bg-gradient="bg-light" icon-bg-color="badge-soft-success"
                icon-color="text-success" @click="$router.push(STUDENT_ROUTES.GPA_CGPA_CALCULATOR.path)" />
            </div>
            <div class="col-md-6">
              <QuickActionCard title="View Grades" description="Check your scores" icon="bi bi-bar-chart-fill"
                bg-gradient="bg-light" icon-bg-color="badge-soft-info" icon-color="text-info"
                @click="$router.push(STUDENT_ROUTES.MY_GRADES.path)" />
            </div>
            <div class="col-md-6">
              <QuickActionCard title="Class Schedule" description="View timetable" icon="bi bi-calendar-event-fill"
                bg-gradient="bg-light" icon-bg-color="badge-soft-info" icon-color="text-info"
                @click="$router.push(STUDENT_ROUTES.CLASS_SCHEDULE.path)" />
            </div>
            <div class="col-md-6">
              <QuickActionCard title="Subject Materials" description="Download resources"
                icon="bi bi-file-earmark-arrow-down-fill" bg-gradient="bg-light" icon-bg-color="badge-soft-primary"
                icon-color="text-primary" @click="$router.push(STUDENT_ROUTES.COURSE_MATERIAL.path)" />
            </div>
            <div class="col-md-6">
              <QuickActionCard title="Announcements" description="View latest updates" icon="bi bi-megaphone-fill"
                bg-gradient="bg-light" icon-bg-color="badge-soft-danger" icon-color="text-danger"
                @click="$router.push(STUDENT_ROUTES.ANNOUNCEMENTS.path)" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ActivityFeed, QuickActionCard, StatCard } from '@/components/shared/common'
import studentPanelService from '@/services/student/studentPanelService'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { STORAGE_KEYS } from '@/utils/constants/storage'

const { studentId, studentName, loadProfile } = useStudentBase()

const loading = ref(true);
const loadingActivities = ref(true)
const activities = ref([]);
const stats = ref(studentPanelService._getDefaultStats())
const activeTodos = ref(0)
const handleAIChat = () => {
  window.dispatchEvent(new CustomEvent('toggle-ai-chat', {
    detail: { action: 'open', focus: true }
  }))
}

const refreshActiveTodoCount = () => {
  try {
    const key = STORAGE_KEYS.TODO_LIST(studentId || 'guest')
    const raw = localStorage.getItem(key)
    const list = raw ? JSON.parse(raw) : []
    activeTodos.value = Array.isArray(list) ? list.filter((task) => !task.completed).length : 0
  } catch {
    activeTodos.value = 0
  }
}

const dashboardStats = computed(() => [
  { value: stats.value.enrolledCourses, title: 'Enrolled Subjects', icon: 'bi bi-book-fill', type: 'student', variant: 'glass', route: STUDENT_ROUTES.ENROLLED_SUBJECTS.path },
  { value: stats.value.pendingAssignments, title: 'Pending Assignments', icon: 'bi bi-clipboard-check-fill', type: 'finance', variant: 'glass', route: STUDENT_ROUTES.VIEW_ASSIGNMENTS.path },
  { value: activeTodos.value, title: 'Active Todos', icon: 'bi bi-list-check', type: 'teacher', variant: 'glass', route: STUDENT_ROUTES.PRODUCTIVITY_TODO.path },
  { value: stats.value.attendance, title: 'Attendance', icon: 'bi bi-calendar-check-fill', type: 'department', variant: 'glass', route: STUDENT_ROUTES.MY_ATTENDANCE.path }
])

const loadDashboard = async () => {
  try {
    await loadProfile()
    if (!studentId) return
    refreshActiveTodoCount()

    const { stats: dStats, activities: activityList } = await studentPanelService.getDashboardStats(studentId)
    stats.value = dStats
    activities.value = activityList
  } finally { loading.value = false; loadingActivities.value = false }
}

onMounted(loadDashboard)
</script>
