<template>
  <AdminPageTemplate
    title="Teacher Profile"
    subtitle="View teacher details and teaching information"
    icon="bi bi-person-workspace"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No ID provided -->
    <div v-if="!teacherId" class="text-center py-5">
      <i class="bi bi-person-workspace display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Teacher</h4>
      <p class="text-muted">Choose a teacher from the list to view their profile.</p>
      <button @click="router.push('/admin-dashboard/teachers')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Teacher List
      </button>
    </div>

    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading teacher profile...</p>
    </div>

    <div v-else-if="!teacher.id" class="text-center py-5">
      <i class="bi bi-person-x display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Teacher Not Found</h4>
      <button @click="router.push('/admin-dashboard/teachers')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Teachers
      </button>
    </div>

    <div v-else>
      <!-- Profile Header -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="profile-avatar profile-avatar-teacher">
                {{ teacher.full_name?.charAt(0)?.toUpperCase() || 'T' }}
              </div>
            </div>
            <div class="col">
              <h3 class="mb-1 fw-bold">{{ teacher.full_name }}</h3>
              <p class="text-muted mb-2">
                <i class="bi bi-hash me-1"></i>{{ teacher.employee_id }}
              </p>
              <div class="d-flex flex-wrap gap-2">
                <span :class="['badge', teacher.is_active ? 'bg-success' : 'bg-warning']">
                  {{ teacher.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span class="badge bg-admin" v-if="teacher.department_name">
                  {{ teacher.department_name }}
                </span>
                <span class="badge bg-info" v-if="teacher.designation">
                  {{ teacher.designation }}
                </span>
              </div>
            </div>
            <div class="col-auto">
              <button @click="router.push(`/admin-dashboard/teachers/edit/${teacher.id}`)" class="btn btn-admin-primary">
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
                  <a :href="`mailto:${teacher.email}`">{{ teacher.email }}</a>
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">Phone</span>
                <span class="info-value">{{ teacher.phone || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Gender</span>
                <span class="info-value text-capitalize">{{ teacher.gender || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Date of Birth</span>
                <span class="info-value">{{ formatDate(teacher.date_of_birth) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">CNIC</span>
                <span class="info-value">{{ teacher.cnic || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Address</span>
                <span class="info-value">{{ teacher.address || 'N/A' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Professional Information -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-briefcase me-2 text-success"></i>Professional Information</h6>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">Department</span>
                <span class="info-value">{{ teacher.department_name || 'Not Assigned' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Designation</span>
                <span class="info-value text-capitalize">{{ teacher.designation || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Qualification</span>
                <span class="info-value">{{ teacher.qualification || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Specialization</span>
                <span class="info-value">{{ teacher.specialization || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Joining Date</span>
                <span class="info-value">{{ formatDate(teacher.joining_date || teacher.created_at) }}</span>
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
                  <h3>{{ stats.subjectsTaught }}</h3>
                  <p>Subjects Teaching</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-success-light">
                <i class="bi bi-people stat-icon text-success"></i>
                <div class="stat-content">
                  <h3>{{ stats.totalStudents }}</h3>
                  <p>Total Students</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-warning-light">
                <i class="bi bi-file-earmark-text stat-icon text-warning"></i>
                <div class="stat-content">
                  <h3>{{ stats.assignmentsCreated }}</h3>
                  <p>Assignments Created</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="stat-card bg-info-light">
                <i class="bi bi-calendar-check stat-icon text-info"></i>
                <div class="stat-content">
                  <h3>{{ stats.classesThisWeek }}</h3>
                  <p>Classes This Week</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Subjects Teaching -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-journals me-2 text-info"></i>Subjects Currently Teaching</h6>
              <span class="badge bg-admin">{{ teachingSubjects.length }} Subjects</span>
            </div>
            <div class="card-body p-0">
              <div v-if="teachingSubjects.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No subjects assigned yet</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Subject Code</th>
                      <th>Subject Name</th>
                      <th>Semester</th>
                      <th>Credits</th>
                      <th>Students</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="subj in teachingSubjects" :key="subj.id">
                      <td><span class="badge bg-dark">{{ subj.subject_code }}</span></td>
                      <td>{{ subj.subject_name }}</td>
                      <td>{{ subj.semester_name || 'N/A' }}</td>
                      <td>{{ subj.credit_hours }}</td>
                      <td><span class="badge bg-info">{{ subj.student_count || 0 }}</span></td>
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
import { teacherService } from '@/services/teacherService'

const router = useRouter()
const route = useRoute()
const teacherId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Teachers', href: '/admin-dashboard/teachers' },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/teachers') }
]

const loading = ref(true)
const teacher = ref({})
const teachingSubjects = ref([])

const stats = computed(() => ({
  subjectsTaught: teachingSubjects.value.length,
  totalStudents: teachingSubjects.value.reduce((sum, s) => sum + (s.student_count || 0), 0),
  assignmentsCreated: teacher.value.assignments_count || 0,
  classesThisWeek: teacher.value.classes_this_week || 0
}))

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const loadTeacher = async () => {
  loading.value = true
  try {
    teacher.value = await teacherService.getTeacher(teacherId)
    
    // Try to load teaching subjects
    try {
      const subjects = await teacherService.getTeacherSubjects(teacherId)
      teachingSubjects.value = Array.isArray(subjects) ? subjects : (subjects.results || [])
    } catch (e) {
      console.log('Could not load subjects:', e)
    }
  } catch (error) {
    console.error('Error loading teacher:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (teacherId && teacherId !== 'profile') {
    loadTeacher()
  } else {
    loading.value = false
  }
})
</script>


