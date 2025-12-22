<template>
  <TeacherPageTemplate
    title="Mark Attendance"
    subtitle="Record student attendance for your classes"
    icon="bi bi-calendar-check"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <div class="row g-4">
      <!-- Class Selection Card -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm sticky-top" style="top: 80px;">
          <div class="card-header bg-white border-bottom">
            <h6 class="mb-0 fw-semibold">
              <i class="bi bi-book me-2 text-teacher"></i>Select Class
            </h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">Class</label>
              <select v-model="selectedClass" class="form-select">
                <option value="">Choose a class...</option>
                <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                  {{ cls.name }}
                </option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label small fw-semibold">Date</label>
              <input v-model="attendanceDate" type="date" class="form-control" :max="today">
            </div>

            <div class="mb-3">
              <label class="form-label small fw-semibold">Session</label>
              <select v-model="session" class="form-select">
                <option value="morning">Morning</option>
                <option value="afternoon">Afternoon</option>
                <option value="evening">Evening</option>
              </select>
            </div>

            <div v-if="selectedClass" class="alert alert-info border-0 small">
              <i class="bi bi-info-circle me-2"></i>
              <strong>{{ students.length }}</strong> students enrolled
            </div>

            <div class="d-flex gap-2">
              <button @click="markAllPresent" class="btn btn-sm btn-success flex-grow-1" :disabled="!selectedClass">
                <i class="bi bi-check-all me-1"></i>All Present
              </button>
              <button @click="markAllAbsent" class="btn btn-sm btn-danger flex-grow-1" :disabled="!selectedClass">
                <i class="bi bi-x-circle me-1"></i>All Absent
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Student List -->
      <div class="col-lg-8">
        <div v-if="!selectedClass" class="text-center py-5">
          <i class="bi bi-calendar-check display-1 text-muted"></i>
          <h4 class="text-muted mt-3">Select a Class</h4>
          <p class="text-muted">Choose a class from the left to mark attendance</p>
        </div>

        <div v-else class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
            <h6 class="mb-0 fw-semibold">
              <i class="bi bi-people me-2 text-teacher"></i>Student List
            </h6>
            <div class="d-flex gap-2 align-items-center">
              <span class="badge bg-success">{{ presentCount }} Present</span>
              <span class="badge bg-danger">{{ absentCount }} Absent</span>
              <span class="badge bg-warning text-dark">{{ leaveCount }} Leave</span>
            </div>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th style="width: 50px;">#</th>
                    <th>Student</th>
                    <th>Roll No</th>
                    <th class="text-center">Status</th>
                    <th class="text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in students" :key="student.id">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="avatar-circle avatar-circle-sm me-2">
                          {{ student.name.charAt(0) }}
                        </div>
                        <span class="fw-semibold">{{ student.name }}</span>
                      </div>
                    </td>
                    <td>{{ student.roll_no }}</td>
                    <td class="text-center">
                      <span :class="['badge', getStatusBadge(student.status)]">
                        {{ student.status }}
                      </span>
                    </td>
                    <td class="text-center">
                      <div class="btn-group btn-group-sm">
                        <button 
                          @click="markStatus(student, 'present')" 
                          :class="['btn', student.status === 'present' ? 'btn-success' : 'btn-outline-success']"
                          title="Present"
                        >
                          <i class="bi bi-check"></i>
                        </button>
                        <button 
                          @click="markStatus(student, 'absent')" 
                          :class="['btn', student.status === 'absent' ? 'btn-danger' : 'btn-outline-danger']"
                          title="Absent"
                        >
                          <i class="bi bi-x"></i>
                        </button>
                        <button 
                          @click="markStatus(student, 'leave')" 
                          :class="['btn', student.status === 'leave' ? 'btn-warning' : 'btn-outline-warning']"
                          title="Leave"
                        >
                          <i class="bi bi-calendar-x"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="card-footer bg-white border-top">
            <div class="d-flex justify-content-between align-items-center">
              <button @click="resetAttendance" class="btn btn-outline-secondary">
                <i class="bi bi-arrow-clockwise me-2"></i>Reset
              </button>
              <button @click="saveAttendance" class="btn btn-teacher-primary" :disabled="saving">
                <span v-if="saving">
                  <span class="spinner-border spinner-border-sm me-2"></span>Saving...
                </span>
                <span v-else>
                  <i class="bi bi-save me-2"></i>Save Attendance
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import TeacherPageTemplate from '@/components/navbar/TeacherPageTemplate.vue'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/teacher-dashboard' },
  { name: 'Attendance', href: '/teacher-dashboard/attendance/mark' },
  { name: 'Mark Attendance' }
]

const actions = [
  { label: 'View Reports', icon: 'bi bi-graph-up', variant: 'btn-teacher-outline', onClick: () => router.push('/teacher-dashboard/attendance/report') }
]

const today = new Date().toISOString().split('T')[0]
const selectedClass = ref('')
const attendanceDate = ref(today)
const session = ref('morning')
const saving = ref(false)

const classes = ref([
  { id: 1, name: 'Data Structures - CS201 (Semester 3)' },
  { id: 2, name: 'Database Systems - CS301 (Semester 5)' },
  { id: 3, name: 'Web Development - CS202 (Semester 3)' }
])

const students = ref([])

const mockStudents = [
  { id: 1, name: 'Ahmed Ali', roll_no: 'CS-2023-001', status: 'present' },
  { id: 2, name: 'Fatima Khan', roll_no: 'CS-2023-002', status: 'present' },
  { id: 3, name: 'Hassan Raza', roll_no: 'CS-2023-003', status: 'absent' },
  { id: 4, name: 'Ayesha Malik', roll_no: 'CS-2023-004', status: 'present' },
  { id: 5, name: 'Usman Ahmed', roll_no: 'CS-2023-005', status: 'leave' }
]

const presentCount = computed(() => students.value.filter(s => s.status === 'present').length)
const absentCount = computed(() => students.value.filter(s => s.status === 'absent').length)
const leaveCount = computed(() => students.value.filter(s => s.status === 'leave').length)

watch(selectedClass, (newVal) => {
  if (newVal) {
    students.value = JSON.parse(JSON.stringify(mockStudents))
  } else {
    students.value = []
  }
})

const getStatusBadge = (status) => {
  const badges = {
    present: 'bg-success',
    absent: 'bg-danger',
    leave: 'bg-warning text-dark'
  }
  return badges[status] || 'bg-secondary'
}

const markStatus = (student, status) => {
  student.status = status
}

const markAllPresent = () => {
  students.value.forEach(s => s.status = 'present')
}

const markAllAbsent = () => {
  students.value.forEach(s => s.status = 'absent')
}

const resetAttendance = () => {
  students.value.forEach(s => s.status = 'present')
}

const saveAttendance = () => {
  saving.value = true
  setTimeout(() => {
    saving.value = false
    alert('Attendance saved successfully!')
  }, 1000)
}
</script>
