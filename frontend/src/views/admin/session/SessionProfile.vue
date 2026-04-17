<template>
  <AdminPageTemplate
    :title="session.session_name || 'Session Profile'"
    subtitle="View academic session details and progress"
    icon="bi bi-calendar-event"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />

    <ConfirmDialog
      v-model="showConfirmDialog"
      :title="confirmTitle"
      :message="confirmMessage"
      type="info"
      theme="admin"
      confirm-text="Confirm"
      @confirm="handleConfirm"
    />

    <!-- No session ID provided -->
    <div v-if="!sessionId" class="text-center py-5">
      <i class="bi bi-calendar-event display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Session</h4>
      <p class="text-muted">Choose a session from the sessions list to view its details.</p>
      <button @click="router.push({ name: ADMIN_ROUTES.SESSION_LIST.name })" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Sessions List
      </button>
    </div>

    <LoadingSpinner v-else-if="loading" text="Loading session profile..." theme="admin" />

    <div v-else-if="!session.id" class="text-center py-5">
      <i class="bi bi-x-circle display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Session Not Found</h4>
      <button @click="router.push({ name: ADMIN_ROUTES.SESSION_LIST.name })" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Sessions
      </button>
    </div>

    <div v-else>
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
            <div class="card-body info-card">
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
              <div class="info-row info-row-multiline" v-if="session.description">
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
                        <span v-if="activatingId === sem.id" class="spinner-border spinner-border-sm"></span>
                        <i v-else class="bi bi-check-circle"></i>
                      </button>
                      <span :class="['badge', sem.status === 'active' ? 'bg-success' : 'bg-light text-dark border']">
                        {{ sem.status === 'active' ? 'Active' : sem.status }}
                      </span>
                      <button 
                        @click="router.push({ name: ADMIN_ROUTES.SEMESTER_PROFILE.name, params: { id: sem.id } })"
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
                        <router-link :to="`${ADMIN_ROUTES.STUDENT_LIST.path}/${student.id}`" class="text-decoration-none fw-bold text-dark">
                          {{ student.full_name }}
                        </router-link>
                      </td>
                      <td>{{ student.enrollment_number }}</td>
                      <td>{{ student.email }}</td>
                      <td>{{ student.phone || '-' }}</td>
                      <td>
                        <span :class="['badge', getActiveBadgeClass(student.is_active)]">
                          {{ getActiveStatusText(student.is_active) }}
                        </span>
                      </td>
                      <td>
                        <button 
                          @click="router.push({ name: ADMIN_ROUTES.STUDENT_PROFILE.name, params: { id: student.id } })" 
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
                <button class="btn btn-link text-admin" @click="router.push(`${ADMIN_ROUTES.STUDENT_LIST.path}?session=${session.id}`)">
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
import { AdminPageTemplate } from '@/components/shared/panels'
import { sessionService, semesterService } from '@/services/shared'
import { ConfirmDialog, LoadingSpinner, AlertMessage } from '@/components/shared/common'
import { useAlert } from '@/composables/shared'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getActiveBadgeClass, getActiveStatusText } from '@/utils/badgeHelpers'

const router = useRouter()
const route = useRoute()
const sessionId = route.params.id
const { alert, showAlert } = useAlert()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Sessions', href: ADMIN_ROUTES.SESSION_LIST.path },
  { name: 'Profile' }
]

const actions = [
  { label: 'Edit Session', icon: 'bi bi-pencil', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.SESSION_EDIT.name, params: { id: sessionId } }) },
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.SESSION_LIST.name }) }
]

const loading = ref(true)
const session = ref({})
const semesters = ref([])
const students = ref([])
const activatingId = ref(null)
const showConfirmDialog = ref(false)
const confirmAction = ref(null)
const confirmMessage = ref('')
const confirmTitle = ref('')
const semesterToActivate = ref(null)

const stats = computed(() => ({
  students: students.value.length,
  semesters: semesters.value.length,
  active: session.value.is_active,
  duration: session.value.end_year && session.value.start_year 
    ? (session.value.end_year - session.value.start_year) 
    : 0
}))

// Use shared formatDate utility with custom options
const formatDate = (dateString) => formatDateUtil(dateString, { year: 'numeric', month: 'long', day: 'numeric' })

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
    // Helper to extract array from response
    const extractArray = (data) => {
      if (!data) return []
      return Array.isArray(data) ? data : (data.results || [])
    }

    // 1. Get Session Details
    const sessionData = await sessionService.getSession(sessionId)
    session.value = sessionData || {}

    // 2. Get Semesters
    try {
      const semesterData = await sessionService.getSessionSemesters(sessionId)
      semesters.value = extractArray(semesterData)
    } catch (semErr) {
      console.error('Error loading semesters:', semErr)
      semesters.value = []
    }

    // 3. Get Enrolled Students
    try {
      const studentData = await sessionService.getSessionStudents(sessionId)
      students.value = extractArray(studentData)
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

const setupSemesters = () => {
  confirmTitle.value = 'Generate Semesters'
  confirmMessage.value = 'Are you sure you want to auto-generate all semesters for this session?'
  confirmAction.value = 'setupSemesters'
  showConfirmDialog.value = true
}

const confirmSetupSemesters = async () => {
  try {
    await sessionService.setupSemesters(sessionId)
    showAlert('success', 'Semesters generated successfully!', 'Success')
    loadSessionData()
  } catch (error) {
    console.error('Error generating semesters:', error)
    showAlert('error', 'Failed to generate semesters. ' + (error.response?.data?.error || ''), 'Error')
  } finally {
    showConfirmDialog.value = false
  }
}

const activateSemester = (semester) => {
  semesterToActivate.value = semester
  confirmTitle.value = 'Activate Semester'
  confirmMessage.value = `Activate "${semester.name}"? This will set it as the current active semester.`
  confirmAction.value = 'activateSemester'
  showConfirmDialog.value = true
}

const confirmActivateSemester = async () => {
  const semester = semesterToActivate.value
  activatingId.value = semester.id
  try {
    await semesterService.activate(semester.id)
    semester.status = 'active'
    showAlert('success', `${semester.name} has been activated successfully!`, 'Success')
    loadSessionData()
  } catch (error) {
    console.error('Error activating semester:', error)
    showAlert('error', 'Failed to activate semester. ' + (error.response?.data?.error || error.message || ''), 'Error')
  } finally {
    activatingId.value = null
    showConfirmDialog.value = false
    semesterToActivate.value = null
  }
}

const handleConfirm = () => {
  if (confirmAction.value === 'setupSemesters') {
    confirmSetupSemesters()
  } else if (confirmAction.value === 'activateSemester') {
    confirmActivateSemester()
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

