<template>
  <AdminPageTemplate
    :title="session.session_name || 'Session Profile'"
    subtitle="View academic session details and progress"
    icon="bi bi-calendar-event"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No session ID provided -->
    <div v-if="!sessionId" class="text-center py-5">
      <i class="bi bi-calendar-event display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Session</h4>
      <p class="text-muted">Choose a session from the sessions list to view its details.</p>
      <button @click="router.push('/admin-dashboard/sessions')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Sessions List
      </button>
    </div>

    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading session profile...</p>
    </div>

    <div v-else-if="!session.id" class="text-center py-5">
      <i class="bi bi-x-circle display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Session Not Found</h4>
      <button @click="router.push('/admin-dashboard/sessions')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Sessions
      </button>
    </div>

    <div v-else>
      <!-- Session Header -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="session-avatar">
                {{ session.session_code?.substring(0, 2) || 'AS' }}
              </div>
            </div>
            <div class="col">
              <h3 class="mb-1 fw-bold">{{ session.session_name }}</h3>
              <p class="text-muted mb-2">
                <i class="bi bi-hash me-1"></i>{{ session.session_code }}
              </p>
              <div class="d-flex flex-wrap gap-2">
                <span :class="getStatusBadgeClass(session.status)">
                  {{ session.status }}
                </span>
                <span class="badge bg-info">
                  {{ session.program_name }}
                </span>
                <span class="badge bg-dark">
                  {{ session.start_year }} - {{ session.end_year }}
                </span>
              </div>
            </div>
            <div class="col-auto">
              <button @click="router.push(`/admin-dashboard/sessions/${session.id}/edit`)" class="btn btn-admin-primary">
                <i class="bi bi-pencil me-2"></i>Edit Session
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <!-- Key Metrics -->
        <div class="col-md-3">
          <div class="stat-card bg-admin-light">
            <i class="bi bi-people stat-icon text-admin"></i>
            <div class="stat-content">
              <h3>{{ stats.students }}</h3>
              <p>Students Enrolled</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card bg-success-light">
            <i class="bi bi-book stat-icon text-success"></i>
            <div class="stat-content">
              <h3>{{ stats.semesters }}</h3>
              <p>Total Semesters</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card bg-warning-light">
            <i class="bi bi-calendar-check stat-icon text-warning"></i>
            <div class="stat-content">
              <h3>{{ stats.active ? 'Active' : 'Inactive' }}</h3>
              <p>Current Status</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card bg-info-light">
            <i class="bi bi-clock stat-icon text-info"></i>
            <div class="stat-content">
              <h3>{{ stats.duration }} Yrs</h3>
              <p>Duration</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Detailed Information -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-info-circle me-2 text-admin"></i>Session Information</h6>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">Session Code</span>
                <span class="info-value">{{ session.session_code || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Program</span>
                <span class="info-value">{{ session.program_name || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Department</span>
                <span class="info-value">{{ session.department_name || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Start Year</span>
                <span class="info-value">{{ session.start_year || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">End Year</span>
                <span class="info-value">{{ session.end_year || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Duration</span>
                <span class="info-value">{{ session.end_year && session.start_year ? (session.end_year - session.start_year) + ' Years' : 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Status</span>
                <span class="info-value"><span :class="getStatusBadgeClass(session.status)">{{ session.status }}</span></span>
              </div>
              <div class="info-row">
                <span class="info-label">Edit Count</span>
                <span class="info-value">{{ session.edit_count || 0 }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Created At</span>
                <span class="info-value">{{ formatDate(session.created_at) }}</span>
              </div>
              <div class="info-row" v-if="session.description">
                <span class="info-label">Description</span>
                <span class="info-value">{{ session.description }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Semesters List -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-list-ol me-2 text-success"></i>Semester Timeline</h6>
              <button class="btn btn-sm btn-outline-success" v-if="semesters.length === 0" @click="setupSemesters">
                <i class="bi bi-plus me-1"></i>Auto-Gen Semesters
              </button>
            </div>
            <div class="card-body p-0">
              <div v-if="semesters.length === 0" class="text-center py-5 text-muted">
                <i class="bi bi-calendar-x display-6"></i>
                <p class="mt-2">No semesters created yet.</p>
              </div>
              <div v-else class="list-group list-group-flush">
                <div v-for="sem in semesters" :key="sem.id" class="list-group-item px-4 py-3">
                  <div class="d-flex w-100 justify-content-between align-items-center">
                    <div>
                      <h6 class="mb-1">{{ sem.name }}</h6>
                      <small class="text-muted">
                        {{ formatDate(sem.start_date) }} - {{ formatDate(sem.end_date) }}
                      </small>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                       <span class="badge bg-info-light text-info border border-info" title="Subjects">
                        <i class="bi bi-book me-1"></i>{{ sem.subject_count || 0 }}
                      </span>
                      <button 
                        v-if="sem.status !== 'active'" 
                        @click="activateSemester(sem)" 
                        class="btn btn-sm btn-outline-success"
                        :disabled="activatingId === sem.id"
                        title="Activate this semester"
                      >
                        <span v-if="activatingId === sem.id" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-check-circle me-1"></i>
                        {{ activatingId === sem.id ? 'Activating...' : 'Activate' }}
                      </button>
                      <span :class="['badge', sem.status === 'active' ? 'bg-success' : 'bg-light text-dark border']">
                        {{ sem.status === 'active' ? 'Active' : sem.status }}
                      </span>
                      <button 
                        @click="router.push(`/admin-dashboard/semesters/${sem.id}`)"
                        class="btn btn-sm btn-light text-muted border"
                        title="View Semester Details"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Students List (Preview) -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-people me-2 text-info"></i>Enrolled Students</h6>
              <span class="badge bg-admin">{{ students.length }} Students</span>
            </div>
            <div class="card-body p-0">
              <div v-if="students.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-people display-6"></i>
                <p class="mt-2">No students enrolled in this session yet.</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Name</th>
                      <th>Enrollment #</th>
                      <th>Email</th>
                      <th>Phone</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="student in students.slice(0, 10)" :key="student.id">
                      <td>
                        <router-link :to="`/admin-dashboard/students/${student.id}`" class="text-decoration-none fw-bold text-dark">
                          {{ student.full_name }}
                        </router-link>
                      </td>
                      <td>{{ student.enrollment_number }}</td>
                      <td>{{ student.email }}</td>
                      <td>{{ student.phone || '-' }}</td>
                      <td>
                        <span :class="['badge', student.is_active ? 'bg-success' : 'bg-danger']">
                          {{ student.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <button 
                          @click="router.push(`/admin-dashboard/students/${student.id}`)" 
                          class="btn btn-sm btn-light text-primary" 
                          title="View Student Profile"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-if="students.length > 10" class="card-footer text-center bg-white border-0 py-3">
                <button class="btn btn-link text-admin" @click="router.push('/admin-dashboard/students?session=' + session.id)">
                  View all enrolled students
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import sessionService from '@/services/sessionService'
import { semesterService } from '@/services/semesterService'

const router = useRouter()
const route = useRoute()
const sessionId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Sessions', href: '/admin-dashboard/sessions' },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/sessions') }
]

const loading = ref(true)
const session = ref({})
const semesters = ref([])
const students = ref([])
const activatingId = ref(null)

const stats = computed(() => ({
  students: students.value.length,
  semesters: semesters.value.length,
  active: session.value.is_active,
  duration: session.value.end_year && session.value.start_year 
    ? (session.value.end_year - session.value.start_year) 
    : 0
}))

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const getStatusBadgeClass = (status) => {
  const map = {
    upcoming: 'badge bg-warning',
    active: 'badge bg-success',
    completed: 'badge bg-secondary',
    archived: 'badge bg-dark'
  }
  return map[status] || 'badge bg-info'
}

const loadSessionData = async () => {
  loading.value = true
  try {
    // 1. Get Session Details
    const sessionRes = await sessionService.getSession(sessionId)
    session.value = sessionRes.data
    
    // 2. Get Semesters
    try {
      const semesterRes = await sessionService.getSessionSemesters(sessionId)
      semesters.value = Array.isArray(semesterRes.data) ? semesterRes.data : (semesterRes.data.results || [])
    } catch (semErr) {
      console.error('Error loading semesters:', semErr)
      semesters.value = []
    }

    // 3. Get Enrolled Students
    try {
      const studentRes = await sessionService.getSessionStudents(sessionId)
      students.value = Array.isArray(studentRes.data) ? studentRes.data : (studentRes.data.results || [])
    } catch (stuErr) {
      console.error('Error loading students:', stuErr)
      students.value = []
    }
    
  } catch (error) {
    console.error('Error loading session profile:', error)
  } finally {
    loading.value = false
  }
}

const setupSemesters = async () => {
  if (!confirm('Are you sure you want to auto-generate all semesters for this session?')) return

  try {
    await sessionService.setupSemesters(sessionId)
    alert('Semesters generated successfully!')
    loadSessionData() // Refresh
  } catch (error) {
    console.error('Error generating semesters:', error)
    alert('Failed to generate semesters. ' + (error.response?.data?.error || ''))
  }
}

const activateSemester = async (semester) => {
  if (!confirm(`Activate "${semester.name}"? This will set it as the current active semester.`)) return
  
  activatingId.value = semester.id
  try {
    await semesterService.activate(semester.id)
    // Update local state
    semester.status = 'active'
    alert(`${semester.name} has been activated successfully!`)
    // Refresh to get updated subject data
    loadSessionData()
  } catch (error) {
    console.error('Error activating semester:', error)
    alert('Failed to activate semester. ' + (error.response?.data?.error || error.message || ''))
  } finally {
    activatingId.value = null
  }
}

onMounted(() => {
  if (sessionId) {
    loadSessionData()
  } else {
    loading.value = false
  }
})
</script>


