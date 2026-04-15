<template>
  <TeacherPageTemplate
    title="Mark Attendance"
    subtitle="Record student attendance for your classes"
    icon="bi bi-calendar-check"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="clearAlert"
    />

    <div class="row g-4">
      <!-- Class Selection Card -->
      <div class="col-12 col-lg-4">
        <div class="card border-0 shadow-sm sticky-lg-top sticky-top-80">
          <div class="card-header bg-white border-bottom">
            <h6 class="mb-0 fw-semibold">
              <i class="bi bi-calendar-check me-2 text-teacher"></i>Attendance Details
            </h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">Class</label>
              <select v-model="selectedClass" class="form-select" :disabled="loading">
                <option value="">Choose a class...</option>
                <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                  {{ cls.name }}
                </option>
              </select>
            </div>

            <div class="mb-3">
              <BaseInput 
                v-model="attendanceDate" 
                type="date" 
                label="Date"
                :max="today"
                required
              />
            </div>

            <div v-if="selectedClass" class="alert alert-info border-0 small">
              <i class="bi bi-info-circle me-2"></i>
              <strong>{{ students.length }}</strong> students enrolled
            </div>

            <div class="d-grid gap-2 d-sm-flex">
              <button @click="markAll('present')" class="btn btn-sm btn-success flex-grow-1" :disabled="!selectedClass || loading">
                <i class="bi bi-check-all me-1"></i>All Present
              </button>
              <button @click="markAll('absent')" class="btn btn-sm btn-danger flex-grow-1" :disabled="!selectedClass || loading">
                <i class="bi bi-x-circle me-1"></i>All Absent
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Student List -->
      <div class="col-12 col-lg-8">
        <div v-if="!selectedClass" class="text-center py-5">
          <i class="bi bi-calendar-check display-1 text-muted"></i>
          <h4 class="text-muted mt-3">Select a Class</h4>
          <p class="text-muted">Choose a class from the left to mark attendance</p>
        </div>

        <div v-else class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2">
              <h6 class="mb-0 fw-semibold">
                <i class="bi bi-people me-2 text-teacher"></i>Student List
              </h6>
              <div class="d-flex flex-wrap gap-2">
                <span class="badge bg-success">{{ getCount('present') }} Present</span>
                <span class="badge bg-danger">{{ getCount('absent') }} Absent</span>
                <span class="badge bg-warning text-dark">{{ getCount('late') }} Late</span>
                <span class="badge bg-info">{{ getCount('excused') }} Excused</span>
              </div>
            </div>
          </div>
          <div class="card-body p-0">
            <LoadingSpinner v-if="loading" theme="teacher" />
            <div v-else class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="d-none d-md-table-cell w-auto">#</th>
                    <th>Student</th>
                    <th class="d-none d-sm-table-cell">Roll No</th>
                    <th class="text-center">Status</th>
                    <th class="text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in students" :key="student.id">
                    <td class="d-none d-md-table-cell">{{ index + 1 }}</td>
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="avatar-circle avatar-circle-sm me-2">
                          {{ student.name.charAt(0) }}
                        </div>
                        <div>
                          <div class="fw-semibold">{{ student.name }}</div>
                          <small class="text-muted d-sm-none">{{ student.roll_no }}</small>
                        </div>
                      </div>
                    </td>
                    <td class="d-none d-sm-table-cell">{{ student.roll_no }}</td>
                    <td class="text-center">
                      <span :class="['badge', getStatusBadge(student.status)]">
                        {{ student.status }}
                      </span>
                    </td>
                    <td class="text-center">
                      <div class="btn-group btn-group-sm">
                        <button v-for="status in ['present', 'absent', 'late', 'excused']" :key="status"
                          @click="student.status = status" 
                          :class="['btn', student.status === status ? getBtnClass(status) : `btn-outline-${getBtnVariant(status)}`]"
                          :title="status.charAt(0).toUpperCase() + status.slice(1)"
                        >
                          <i :class="getBtnIcon(status)"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="card-footer bg-white border-top">
            <div class="d-flex justify-content-end gap-2">
              <button @click="resetAttendance" class="btn btn-outline-secondary" :disabled="loading || saving">
                <i class="bi bi-arrow-clockwise me-2"></i>Reset
              </button>
              <button @click="saveAttendance" class="btn btn-teacher-primary" :disabled="loading || saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-save me-2"></i>Save Attendance
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { BaseInput, AlertMessage, LoadingSpinner } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { useAlert } from '@/composables/shared'

const router = useRouter()
const route = useRoute()
const { alert, showAlert, clearAlert } = useAlert()

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Attendance', href: TEACHER_ROUTES.MARK_ATTENDANCE.path },
  { name: 'Mark Attendance' }
]

const actions = [
  { label: 'View Reports', icon: 'bi bi-graph-up', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.ATTENDANCE_REPORT.name }) }
]

const today = new Date().toISOString().split('T')[0]
const selectedClass = ref('')
const attendanceDate = ref(today)
const saving = ref(false)
const loading = ref(false)
const classes = ref([])
const students = ref([])

const loadClasses = async () => {
  loading.value = true
  try {
    const response = await teacherPanelService.getMyClasses({}, { forceRefresh: true })
    const classList = response.results || response || []
    classes.value = classList.map(cls => ({
      id: cls.id,
      subject_id: cls.subject_id,
      name: `${cls.subject_name} - ${cls.subject_code} (${cls.semester})`
    }))
  } catch (error) {
    showAlert('error', 'Failed to load classes')
  } finally {
    loading.value = false
  }
}

const loadStudents = async (classId) => {
  if (!classId) return
  loading.value = true
  try {
    const response = await teacherPanelService.getClassStudents(classId)
    const studentList = response.results || response || []
    students.value = studentList.map(student => ({
      id: student.id,
      name: student.name,
      roll_no: student.roll_no,
      status: 'present'
    }))
  } catch (error) {
    showAlert('error', 'Failed to load students')
    students.value = []
  } finally {
    loading.value = false
  }
}

watch(selectedClass, (newVal) => {
  if (newVal) loadStudents(newVal)
  else students.value = []
})

const getStatusBadge = (status) => {
  const map = { present: 'bg-success', absent: 'bg-danger', late: 'bg-warning text-dark', excused: 'bg-info' }
  return map[status] || 'bg-secondary'
}

const getBtnVariant = (status) => {
  const map = { present: 'success', absent: 'danger', late: 'warning', excused: 'info' }
  return map[status] || 'secondary'
}

const getBtnClass = (status) => `btn-${getBtnVariant(status)}`

const getBtnIcon = (status) => {
  const map = { present: 'bi-check', absent: 'bi-x', late: 'bi-clock', excused: 'bi-info-circle' }
  return `bi ${map[status]}`
}

const getCount = (status) => students.value.filter(s => s.status === status).length

const markAll = (status) => students.value.forEach(s => s.status = status)
const resetAttendance = () => markAll('present')

const saveAttendance = async () => {
  if (!selectedClass.value || !attendanceDate.value) {
    return showAlert('error', 'Please select class and date')
  }
  
  saving.value = true
  try {
    const selectedClassData = classes.value.find(c => c.id === selectedClass.value)
    if (!selectedClassData?.subject_id) throw new Error("Invalid class data")

    const attendanceData = students.value.map(student => ({
      student: student.id,
      subject: selectedClassData.subject_id,
      session_date: attendanceDate.value,
      status: student.status
    }))

    const response = await teacherPanelService.bulkMarkAttendance(attendanceData)
    
    if (response.failed > 0) {
      // Create detailed error message from response.errors
      const errorDetails = response.errors.map(e => {
        const studentName = students.value[e.index]?.name || 'Unknown'
        // Handle various error formats (string or object)
        const msg = typeof e.error === 'string' ? e.error : 
                   typeof e.errors === 'object' ? JSON.stringify(e.errors) : 'Unknown error'
        return `${studentName}: ${msg}`
      }).join('\n')
      
      showAlert('warning', `Saved with ${response.failed} errors:\n${errorDetails}`, 'Warning!')
    } else {
      showAlert('success', `Attendance saved! ${response.created} records created/updated.`)
      resetAttendance()
    }
  } catch (error) {
    console.error(error)
    const msg = error.response?.data ? JSON.stringify(error.response.data) : error.message
    showAlert('error', `Failed: ${msg}`)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadClasses()
  if (route.query.class) selectedClass.value = route.query.class
})
</script>

