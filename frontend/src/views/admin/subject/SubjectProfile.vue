<template>
  <AdminPageTemplate
    title="Subject Profile"
    subtitle="View subject details and enrollment information"
    icon="bi bi-book"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No ID provided -->
    <div v-if="!subjectId" class="text-center py-5">
      <i class="bi bi-book display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Subject</h4>
      <p class="text-muted">Choose a subject from the list to view its profile.</p>
      <button @click="router.push('/admin-dashboard/subjects')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Subject List
      </button>
    </div>

    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading subject details...</p>
    </div>

    <div v-else-if="!subject.id" class="text-center py-5">
      <i class="bi bi-book display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Subject Not Found</h4>
      <button @click="router.push('/admin-dashboard/subjects')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Subjects
      </button>
    </div>

    <div v-else>
      <!-- Subject Header -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="profile-avatar rounded profile-avatar-subject">
                <i class="bi bi-book"></i>
              </div>
            </div>
            <div class="col">
              <h3 class="mb-1 fw-bold">{{ subject.name }}</h3>
              <p class="text-muted mb-2">
                <i class="bi bi-hash me-1"></i>{{ subject.code }}
              </p>
              <div class="d-flex flex-wrap gap-2">
                <span class="badge bg-admin">{{ subject.credit_hours }} Credits</span>
                <span class="badge bg-info" v-if="subject.semester_name">
                  {{ subject.semester_name }}
                </span>
                <span class="badge bg-secondary" v-if="subject.program_name">
                  {{ subject.program_name }}
                </span>
              </div>
            </div>
            <div class="col-auto">
              <button @click="router.push(`/admin-dashboard/subjects/edit/${subject.id}`)" class="btn btn-admin-primary">
                <i class="bi bi-pencil me-2"></i>Edit Subject
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Subject Information -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-info-circle me-2 text-admin"></i>Subject Information</h6>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">Name</span>
                <span class="info-value">{{ subject.name }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Code</span>
                <span class="info-value"><span class="badge bg-dark">{{ subject.code }}</span></span>
              </div>
              <div class="info-row">
                <span class="info-label">Credit Hours</span>
                <span class="info-value">{{ subject.credit_hours }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Semester</span>
                <span class="info-value">{{ subject.semester_name || 'Not Assigned' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Program</span>
                <span class="info-value">{{ subject.program_name || 'N/A' }}</span>
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
              <p v-if="subject.description" class="text-muted">{{ subject.description }}</p>
              <p v-else class="text-muted fst-italic">No description available</p>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="col-12">
          <div class="row g-4">
            <div class="col-md-3">
              <div class="stat-card bg-admin-light">
                <i class="bi bi-people stat-icon text-admin"></i>
                <div class="stat-content">
                  <h3>{{ enrolledStudents.length }}</h3>
                  <p>Enrolled Students</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-success-light">
                <i class="bi bi-person-workspace stat-icon text-success"></i>
                <div class="stat-content">
                  <h3>{{ assignedTeachers.length }}</h3>
                  <p>Teachers</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-warning-light">
                <i class="bi bi-file-earmark-text stat-icon text-warning"></i>
                <div class="stat-content">
                  <h3>{{ assignments.length }}</h3>
                  <p>Assignments</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-info-light">
                <i class="bi bi-clock stat-icon text-info"></i>
                <div class="stat-content">
                  <h3>{{ subject.credit_hours }}</h3>
                  <p>Credit Hours</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Assigned Teachers -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-person-workspace me-2 text-success"></i>Assigned Teachers</h6>
              <span class="badge bg-success">{{ assignedTeachers.length }}</span>
            </div>
            <div class="card-body p-0">
              <div v-if="assignedTeachers.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No teachers assigned</p>
              </div>
              <ul v-else class="list-group list-group-flush">
                <li v-for="t in assignedTeachers" :key="t.id" class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ t.teacher_name || t.full_name }}</strong>
                    <br><small class="text-muted">{{ t.designation || 'Teacher' }}</small>
                  </div>
                  <button @click="router.push(`/admin-dashboard/teachers/${t.teacher}`)" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-eye"></i>
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Assignments -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-file-earmark-text me-2 text-warning"></i>Assignments</h6>
              <span class="badge bg-warning text-dark">{{ assignments.length }}</span>
            </div>
            <div class="card-body p-0">
              <div v-if="assignments.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No assignments yet</p>
              </div>
              <ul v-else class="list-group list-group-flush">
                <li v-for="a in assignments.slice(0, 5)" :key="a.id" class="list-group-item">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{{ a.title }}</strong>
                      <br><small class="text-muted">Due: {{ formatDate(a.due_date) }}</small>
                    </div>
                    <span class="badge bg-admin">{{ a.total_marks }} marks</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Enrolled Students -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-people me-2 text-admin"></i>Enrolled Students</h6>
              <span class="badge bg-admin">{{ enrolledStudents.length }} Students</span>
            </div>
            <div class="card-body p-0">
              <div v-if="enrolledStudents.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No students enrolled in this subject</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Enrollment #</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="s in enrolledStudents.slice(0, 10)" :key="s.id">
                      <td><span class="badge bg-light text-dark">{{ s.student_enrollment }}</span></td>
                      <td class="fw-semibold">{{ s.student_name }}</td>
                      <td>{{ s.student_email || 'N/A' }}</td>
                      <td>
                        <span :class="['badge', s.is_active !== false ? 'bg-success' : 'bg-warning']">
                          {{ s.is_active !== false ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <button @click="router.push(`/admin-dashboard/students/${s.student}`)" class="btn btn-sm btn-outline-primary">
                          <i class="bi bi-eye"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="enrolledStudents.length > 10" class="text-center py-3">
                  <small class="text-muted">Showing 10 of {{ enrolledStudents.length }} students</small>
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { subjectService } from '@/services/subjectService'

const router = useRouter()
const route = useRoute()
const rawId = route.params.id
const subjectId = rawId && rawId !== 'profile' ? rawId : null

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Subjects', href: '/admin-dashboard/subjects' },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/subjects') }
]

const loading = ref(true)
const subject = ref({})
const enrolledStudents = ref([])
const assignedTeachers = ref([])
const assignments = ref([])

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const loadSubject = async () => {
  loading.value = true
  try {
    subject.value = await subjectService.getSubjectById(subjectId)
    
    // Load enrolled students
    try {
      const studentData = await subjectService.getEnrolledStudents(subjectId)
      enrolledStudents.value = Array.isArray(studentData) ? studentData : (studentData.results || [])
    } catch (e) { console.log('Could not load students:', e) }
    
    // Load assigned teachers
    try {
      const teacherData = await subjectService.getAssignedTeachers(subjectId)
      assignedTeachers.value = Array.isArray(teacherData) ? teacherData : (teacherData.results || [])
    } catch (e) { console.log('Could not load teachers:', e) }
    
    // Load assignments
    try {
      const assignmentData = await subjectService.getSubjectAssignments(subjectId)
      assignments.value = Array.isArray(assignmentData) ? assignmentData : (assignmentData.results || [])
    } catch (e) { console.log('Could not load assignments:', e) }
  } catch (error) {
    console.error('Error loading subject:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (subjectId) {
    loadSubject()
  } else {
    loading.value = false
  }
})
</script>


