<template>
  <AdminPageTemplate
    title="Course Profile"
    subtitle="View course details and academic information"
    icon="bi bi-mortarboard"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No ID provided -->
    <div v-if="!courseId" class="text-center py-5">
      <i class="bi bi-mortarboard display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Course</h4>
      <p class="text-muted">Choose a course from the list to view its details.</p>
      <button @click="router.push('/admin-dashboard/courses')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Course List
      </button>
    </div>

    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading course details...</p>
    </div>

    <div v-else-if="!course.id" class="text-center py-5">
      <i class="bi bi-x-circle display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Course Not Found</h4>
      <button @click="router.push('/admin-dashboard/courses')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Courses
      </button>
    </div>

    <div v-else>
      <!-- Course Header -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="profile-avatar rounded profile-avatar-course">
                <i class="bi bi-mortarboard"></i>
              </div>
            </div>
            <div class="col">
              <h3 class="mb-1 fw-bold">{{ course.name }}</h3>
              <p class="text-muted mb-2">
                <i class="bi bi-hash me-1"></i>{{ course.code }}
              </p>
              <div class="d-flex flex-wrap gap-2">
                <span class="badge bg-admin">{{ course.duration_years }} Years</span>
                <span class="badge bg-info" v-if="course.department_name">
                  {{ course.department_name }}
                </span>
              </div>
            </div>
            <div class="col-auto">
              <button @click="router.push(`/admin-dashboard/courses/edit/${course.id}`)" class="btn btn-admin-primary">
                <i class="bi bi-pencil me-2"></i>Edit Course
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Course Information -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-info-circle me-2 text-admin"></i>Course Information</h6>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">Name</span>
                <span class="info-value">{{ course.name }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Code</span>
                <span class="info-value"><span class="badge bg-dark">{{ course.code }}</span></span>
              </div>
              <div class="info-row">
                <span class="info-label">Department</span>
                <span class="info-value">{{ course.department_name || 'Not Assigned' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Duration</span>
                <span class="info-value">{{ course.duration_years }} Years</span>
              </div>
              <div class="info-row">
                <span class="info-label">Created</span>
                <span class="info-value">{{ formatDate(course.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-text-paragraph me-2 text-success"></i>Description</h6>
            </div>
            <div class="card-body">
              <p v-if="course.description" class="text-muted">{{ course.description }}</p>
              <p v-else class="text-muted fst-italic">No description available</p>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="col-12">
          <div class="row g-4">
            <div class="col-md-3">
              <div class="stat-card bg-admin-light">
                <i class="bi bi-calendar3 stat-icon text-admin"></i>
                <div class="stat-content">
                  <h3>{{ semesters.length }}</h3>
                  <p>Semesters</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-success-light">
                <i class="bi bi-book stat-icon text-success"></i>
                <div class="stat-content">
                  <h3>{{ stats.totalSubjects }}</h3>
                  <p>Total Subjects</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-info-light">
                <i class="bi bi-people stat-icon text-info"></i>
                <div class="stat-content">
                  <h3>{{ students.length }}</h3>
                  <p>Enrolled Students</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-warning-light">
                <i class="bi bi-clock stat-icon text-warning"></i>
                <div class="stat-content">
                  <h3>{{ stats.totalCredits }}</h3>
                  <p>Total Credit Hours</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Semesters -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-calendar3 me-2 text-admin"></i>Semesters</h6>
              <div>
                <span class="badge bg-admin me-2">{{ semesters.length }} Semesters</span>
              </div>
            </div>
            <div class="card-body p-0">
              <div v-if="semesters.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No semesters defined yet</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Semester</th>
                      <th>Number</th>
                      <th>Subjects</th>
                      <th>Start Date</th>
                      <th>End Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="sem in semesters" :key="sem.id">
                      <td class="fw-semibold">{{ sem.name }}</td>
                      <td><span class="badge bg-dark">{{ sem.number }}</span></td>
                      <td><span class="badge bg-info">{{ sem.subject_count || 0 }}</span></td>
                      <td>{{ formatDate(sem.start_date) }}</td>
                      <td>{{ formatDate(sem.end_date) }}</td>
                      <td>
                        <button @click="router.push({ name: 'SemesterProfile', params: { id: sem.id } })" class="btn btn-sm btn-outline-primary" title="View Semester">
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

        <!-- Students -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-people me-2 text-info"></i>Enrolled Students</h6>
              <span class="badge bg-info">{{ students.length }} Students</span>
            </div>
            <div class="card-body p-0">
              <div v-if="students.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No students enrolled in this course</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Enrollment #</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Semester</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="s in students.slice(0, 10)" :key="s.id">
                      <td><span class="badge bg-light text-dark">{{ s.enrollment_number }}</span></td>
                      <td class="fw-semibold">{{ s.full_name }}</td>
                      <td>{{ s.email }}</td>
                      <td>{{ s.current_semester_name || 'N/A' }}</td>
                      <td>
                        <span :class="['badge', s.is_active ? 'bg-success' : 'bg-warning']">
                          {{ s.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <button @click="router.push(`/admin-dashboard/students/${s.id}`)" class="btn btn-sm btn-outline-primary">
                          <i class="bi bi-eye"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="students.length > 10" class="text-center py-3">
                  <small class="text-muted">Showing 10 of {{ students.length }} students</small>
                </div>
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
import { programService } from '@/services/programService'

const router = useRouter()
const route = useRoute()
const courseId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Courses', href: '/admin-dashboard/courses' },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/courses') }
]

const loading = ref(true)
const course = ref({})
const semesters = ref([])
const students = ref([])

const stats = computed(() => ({
  totalSubjects: semesters.value.reduce((sum, s) => sum + (s.subject_count || 0), 0),
  totalCredits: course.value.total_credits || semesters.value.reduce((sum, s) => sum + (s.credit_hours || 0), 0)
}))

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const loadCourse = async () => {
  loading.value = true
  try {
    course.value = await programService.getProgramById(courseId)
    
    // Load semesters
    try {
      const semData = await programService.getProgramSemesters(courseId)
      semesters.value = Array.isArray(semData) ? semData : (semData.results || [])
    } catch (e) { console.log('Could not load semesters:', e) }
    
    // Load students
    try {
      const studentData = await programService.getProgramStudents(courseId)
      students.value = Array.isArray(studentData) ? studentData : (studentData.results || [])
    } catch (e) { console.log('Could not load students:', e) }
  } catch (error) {
    console.error('Error loading course:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (courseId && courseId !== 'profile') {
    loadCourse()
  } else {
    loading.value = false
  }
})
</script>


