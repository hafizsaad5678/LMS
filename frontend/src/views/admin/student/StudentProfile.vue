<template>
  <AdminPageTemplate
    title="Student Profile"
    subtitle="View student details and academic information"
    icon="bi bi-person-badge"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No ID provided -->
    <div v-if="!studentId" class="text-center py-5">
      <i class="bi bi-person-badge display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Student</h4>
      <p class="text-muted">Choose a student from the list to view their profile.</p>
      <button @click="router.push('/admin-dashboard/students')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Student List
      </button>
    </div>

    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading student profile...</p>
    </div>

    <div v-else-if="!student.id" class="text-center py-5">
      <i class="bi bi-person-x display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Student Not Found</h4>
      <button @click="router.push('/admin-dashboard/students')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Students
      </button>
    </div>

    <div v-else>
      <!-- Profile Header -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="profile-avatar profile-avatar-admin">
                {{ student.full_name?.charAt(0)?.toUpperCase() || 'S' }}
              </div>
            </div>
            <div class="col">
              <h3 class="mb-1 fw-bold">{{ student.full_name }}</h3>
              <p class="text-muted mb-2">
                <i class="bi bi-hash me-1"></i>{{ student.enrollment_number }}
              </p>
              <div class="d-flex flex-wrap gap-2">
                <span :class="['badge', student.is_active ? 'bg-success' : 'bg-warning']">
                  {{ student.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span class="badge bg-info" v-if="student.program_name">
                  {{ student.program_name }}
                </span>
              </div>
            </div>
            <div class="col-auto">
              <button @click="router.push(`/admin-dashboard/students/edit/${student.id}`)" class="btn btn-admin-primary">
                <i class="bi bi-pencil me-2"></i>Edit Profile
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Personal Information -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-person me-2 text-admin"></i>Personal Information</h6>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">Email</span>
                <span class="info-value">
                  <a :href="`mailto:${student.email}`">{{ student.email }}</a>
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">Phone</span>
                <span class="info-value">{{ student.phone || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Gender</span>
                <span class="info-value text-capitalize">{{ student.gender || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Date of Birth</span>
                <span class="info-value">{{ formatDate(student.date_of_birth) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">CNIC</span>
                <span class="info-value">{{ student.cnic || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Address</span>
                <span class="info-value">{{ student.address || 'N/A' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Academic Information -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-mortarboard me-2 text-success"></i>Academic Information</h6>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">Program</span>
                <span class="info-value">{{ student.program_name || 'Not Assigned' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Department</span>
                <span class="info-value">{{ student.department_name || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Session/Batch</span>
                <span class="info-value">{{ student.session_name || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Current Semester</span>
                <span class="info-value">{{ student.current_semester_name || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Enrollment Date</span>
                <span class="info-value">{{ formatDate(student.created_at) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Blood Group</span>
                <span class="info-value">{{ student.blood_group || 'N/A' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="col-12">
          <div class="row g-4">
            <div class="col-md-3">
              <div class="stat-card bg-admin-light">
                <i class="bi bi-book stat-icon text-admin"></i>
                <div class="stat-content">
                  <h3>{{ stats.enrolledSubjects }}</h3>
                  <p>Enrolled Subjects</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-success-light">
                <i class="bi bi-check-circle stat-icon text-success"></i>
                <div class="stat-content">
                  <h3>{{ stats.completedAssignments }}</h3>
                  <p>Completed Assignments</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-warning-light">
                <i class="bi bi-hourglass-split stat-icon text-warning"></i>
                <div class="stat-content">
                  <h3>{{ stats.pendingAssignments }}</h3>
                  <p>Pending Assignments</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-info-light">
                <i class="bi bi-graph-up stat-icon text-info"></i>
                <div class="stat-content">
                  <h3>{{ stats.attendanceRate }}%</h3>
                  <p>Attendance Rate</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Enrolled Subjects -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-journals me-2 text-info"></i>Enrolled Subjects</h6>
              <span class="badge bg-admin">{{ enrolledSubjects.length }} Subjects</span>
            </div>
            <div class="card-body p-0">
              <div v-if="enrolledSubjects.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No subjects enrolled yet</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Subject Code</th>
                      <th>Subject Name</th>
                      <th>Semester</th>
                      <th>Credits</th>
                      <th>Teacher</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="subj in enrolledSubjects" :key="subj.id">
                      <td><span class="badge bg-dark">{{ subj.subject_code }}</span></td>
                      <td>{{ subj.subject_name }}</td>
                      <td>{{ subj.semester_name || 'N/A' }}</td>
                      <td>{{ subj.credit_hours }}</td>
                      <td>{{ subj.teacher_name || 'N/A' }}</td>
                      <td>
                        <button @click="router.push(`/admin-dashboard/subjects/${subj.subject}`)" class="btn btn-sm btn-outline-primary" title="View Subject">
                          <i class="bi bi-eye"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
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
import { studentService } from '@/services/studentservices'

const router = useRouter()
const route = useRoute()
const studentId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Students', href: '/admin-dashboard/students' },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/students') }
]

const loading = ref(true)
const student = ref({})
const enrolledSubjects = ref([])

const stats = computed(() => ({
  enrolledSubjects: enrolledSubjects.value.length,
  completedAssignments: student.value.completed_assignments || 0,
  pendingAssignments: student.value.pending_assignments || 0,
  attendanceRate: student.value.attendance_rate || 0
}))

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const loadStudent = async () => {
  loading.value = true
  try {
    student.value = await studentService.getStudent(studentId)
    
    // Try to load enrolled subjects
    try {
      const subjects = await studentService.getStudentSubjects(studentId)
      enrolledSubjects.value = Array.isArray(subjects) ? subjects : (subjects.results || [])
    } catch (e) {
      console.log('Could not load subjects:', e)
    }
  } catch (error) {
    console.error('Error loading student:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (studentId && studentId !== 'profile') {
    loadStudent()
  } else {
    loading.value = false
  }
})
</script>


