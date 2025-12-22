<template>
  <div class="d-flex justify-content-between align-items-center mb-5">
    <div>
      <h1 class="h2 fw-bold text-dark mb-2">Admin Dashboard</h1>
      <p class="text-muted mb-0">Welcome back! Here's what's happening today.</p>
    </div>
    
    <!-- Compact Search Bar -->
    <div class="search-container position-relative" style="min-width: 300px;">
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
        <button @click="handleSearch" class="btn btn-admin-primary px-3">
          <i class="bi bi-arrow-right"></i>
        </button>
      </div>
      <div v-if="loadingSearch" class="position-absolute top-100 start-0 w-100 mt-1">
        <div class="progress" style="height: 2px;">
          <div class="progress-bar progress-bar-striped progress-bar-animated bg-admin-primary" style="width: 100%"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Stats Grid -->
  <!-- Stats Grid -->
  <div class="row g-4 mb-5">
    <!-- Row 1 -->
    <div class="col-xl-3 col-md-6">
      <div class="stat-card bg-gradient-red" @click="router.push('/admin-dashboard/students')">
        <div class="stat-icon">
          <i class="bi bi-people"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.students.value }}</h3>
          <p>Total Students</p>
        </div>
      </div>
    </div>
    
    <div class="col-xl-3 col-md-6">
      <div class="stat-card bg-gradient-rose" @click="router.push('/admin-dashboard/teachers')">
        <div class="stat-icon">
          <i class="bi bi-person-badge"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.teachers.value }}</h3>
          <p>Total Teachers</p>
        </div>
      </div>
    </div>
    
    <div class="col-xl-3 col-md-6">
      <div class="stat-card bg-gradient-sunset" @click="router.push('/admin-dashboard/sessions')">
        <div class="stat-icon">
          <i class="bi bi-calendar-event"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.sessions.value }}</h3>
          <p>Active Sessions</p>
        </div>
      </div>
    </div>
    
    <div class="col-xl-3 col-md-6">
      <div class="stat-card bg-gradient-dark-red" @click="router.push('/admin-dashboard/fees-collection')">
        <div class="stat-icon">
          <i class="bi bi-currency-dollar"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.revenue.value }}</h3>
          <p>Total Revenue</p>
        </div>
      </div>
    </div>
    
    <!-- Row 2 -->
    <div class="col-xl-3 col-md-4">
      <div class="stat-card bg-gradient-ruby" @click="router.push('/admin-dashboard/departments')">
        <div class="stat-icon">
          <i class="bi bi-building"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.departments.value }}</h3>
          <p>Departments</p>
        </div>
      </div>
    </div>
    
    <div class="col-xl-3 col-md-4">
      <div class="stat-card bg-gradient-tomato" @click="router.push('/admin-dashboard/courses')">
        <div class="stat-icon">
          <i class="bi bi-mortarboard"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.programs.value }}</h3>
          <p>Total Programs</p>
        </div>
      </div>
    </div>
    
    <div class="col-xl-3 col-md-4">
      <div class="stat-card bg-gradient-crimson" @click="router.push('/admin-dashboard/subjects')">
        <div class="stat-icon">
          <i class="bi bi-book"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.subjects.value }}</h3>
          <p>Total Subjects</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Content Grid -->
  <div class="row g-4">
    <!-- Recent Activities -->
    <div class="col-lg-6">
      <ActivityFeed :activities="recentActivities" />
    </div>

    <!-- Quick Actions -->
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
                @click="router.push('/admin-dashboard/students/add')"
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
                @click="router.push('/admin-dashboard/teachers/add')"
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
                @click="router.push('/admin-dashboard/departments/add')"
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
                @click="router.push('/admin-dashboard/fees-collection')"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ActivityFeed from '@/components/common/ActivityFeed.vue'
import QuickActionCard from '@/components/common/QuickActionCard.vue'
import { studentService } from '@/services/studentservices'
import { teacherService } from '@/services/teacherService'
import { departmentService } from '@/services/departmentService'
import { feeService } from '@/services/managementService'
import { assignmentService } from '@/services/assignmentService'
import sessionService from '@/services/sessionService'
import { programService } from '@/services/programService'
import { subjectService } from '@/services/subjectService'

const router = useRouter()
const searchQuery = ref('')
const loadingSearch = ref(false)
const loading = ref(false)

const stats = ref({
  students: { value: '0', change: '+0%' },
  teachers: { value: '0', change: '+0%' },
  departments: { value: '0', change: '+0%' },
  revenue: { value: 'PKR 0', change: '+0%' },
  sessions: { value: '0', change: 'Active' },
  programs: { value: '0', change: 'Total' },
  subjects: { value: '0', change: 'Total' }
})

const recentActivities = ref([])

const loadDashboardData = async () => {
  loading.value = true
  try {
    // BATCH 1: Load stats in parallel (7 calls reduced to 7 - unavoidable for different endpoints)
    const [studentsRes, teachersRes, deptsRes, feeStatsRes, sessionsRes, programsRes, subjectsRes] = await Promise.all([
      studentService.getAllStudents({ page_size: 1 }),
      teacherService.getAllTeachers({ page_size: 1 }),
      departmentService.getAllDepartments({ page_size: 1 }),
      feeService.statistics(),
      sessionService.getSessions({ status: 'active' }),
      programService.getAllPrograms({ page_size: 1 }),
      subjectService.getAllSubjects({ page_size: 1 })
    ])

    const studentCount = studentsRes.count || (studentsRes.results ? studentsRes.results.length : 0)
    const teacherCount = teachersRes.count || (teachersRes.results ? teachersRes.results.length : 0)
    const deptCount = deptsRes.count || (deptsRes.results ? deptsRes.results.length : 0)
    const sessionsData = sessionsRes.data || []
    const activeSessionsCount = sessionsData.length || (sessionsData.results ? sessionsData.results.length : 0)
    const programCount = programsRes.count || (programsRes.results ? programsRes.results.length : 0)
    const subjectCount = subjectsRes.count || (subjectsRes.results ? subjectsRes.results.length : 0)
    const totalRevenue = feeStatsRes.data ? feeStatsRes.data.total_collected : 0
    
    stats.value = {
      students: { value: studentCount.toLocaleString(), change: '+12%' }, 
      teachers: { value: teacherCount.toLocaleString(), change: '+3%' },
      departments: { value: deptCount.toLocaleString(), change: '+1%' },
      revenue: { value: `PKR ${totalRevenue.toLocaleString()}`, change: '+8%' },
      sessions: { value: activeSessionsCount.toLocaleString(), change: 'Active' },
      programs: { value: programCount.toLocaleString(), change: 'Total' },
      subjects: { value: subjectCount.toLocaleString(), change: 'Total' }
    }

    // BATCH 2: Load recent activities (3 calls - load in background after stats)
    setTimeout(async () => {
      try {
        const [recentStudents, recentFees, recentAssignments] = await Promise.all([
          studentService.getAllStudents({ ordering: '-created_at', page_size: 2 }),
          feeService.getAll({ ordering: '-created_at', page_size: 2 }),
          assignmentService.getAllAssignments({ ordering: '-created_at', page_size: 2 })
        ])

        const activities = []

        if (recentStudents.results) {
          recentStudents.results.forEach(s => {
            activities.push({
              id: `student-${s.id}`,
              message: `New student enrolled: ${s.full_name}`,
              time: getTimeAgo(s.created_at),
              timestamp: new Date(s.created_at)
            })
          })
        }

        if (recentFees.data && recentFees.data.results) {
          recentFees.data.results.forEach(f => {
            if (f.status === 'paid') {
              activities.push({
                id: `fee-${f.id}`,
                message: `Fee payment received from ${f.student_name}`,
                time: getTimeAgo(f.payment_date || f.updated_at),
                timestamp: new Date(f.payment_date || f.updated_at)
              })
            }
          })
        }

        if (recentAssignments.results) {
          recentAssignments.results.forEach(a => {
            activities.push({
              id: `assign-${a.id}`,
              message: `New assignment created: ${a.title}`,
              time: getTimeAgo(a.created_at),
              timestamp: new Date(a.created_at)
            })
          })
        }

        recentActivities.value = activities
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, 5)
      } catch (error) {
        console.error('Error loading activities:', error)
      }
    }, 100) // Load activities after stats are displayed

  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const getTimeAgo = (dateString) => {
  if (!dateString) return 'Recently'
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)
  
  let interval = seconds / 31536000
  if (interval > 1) return Math.floor(interval) + " years ago"
  interval = seconds / 2592000
  if (interval > 1) return Math.floor(interval) + " months ago"
  interval = seconds / 86400
  if (interval > 1) return Math.floor(interval) + " days ago"
  interval = seconds / 3600
  if (interval > 1) return Math.floor(interval) + " hours ago"
  interval = seconds / 60
  if (interval > 1) return Math.floor(interval) + " minutes ago"
  return Math.floor(seconds) + " seconds ago"
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  loadingSearch.value = true
  const query = searchQuery.value.toLowerCase()
  
  try {
    const students = await studentService.getAllStudents({ search: query })
    const studentList = students.results || students || []
    
    if (studentList.length > 0) {
      if (studentList.length === 1) {
        router.push(`/admin-dashboard/students/${studentList[0].id}`)
        return
      } else {
        router.push({ path: '/admin-dashboard/students', query: { search: query } })
        return
      }
    }
    
    const teachers = await teacherService.getAllTeachers({ search: query })
    const teacherList = teachers.results || teachers || []
    
    if (teacherList.length > 0) {
      if (teacherList.length === 1) {
        router.push(`/admin-dashboard/teachers/${teacherList[0].id}`)
        return
      } else {
        router.push({ path: '/admin-dashboard/teachers', query: { search: query } })
        return
      }
    }
    
    alert('No direct profile found. Try browsing the lists.')
    
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    loadingSearch.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

