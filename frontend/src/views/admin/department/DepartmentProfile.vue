<template>
  <AdminPageTemplate
    title="Department Profile"
    subtitle="View department details and statistics"
    icon="bi bi-building"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No ID provided -->
    <div v-if="!departmentId" class="text-center py-5">
      <i class="bi bi-building display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Department</h4>
      <p class="text-muted">Choose a department from the list to view its details.</p>
      <button @click="router.push('/admin-dashboard/departments')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Department List
      </button>
    </div>

    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading department details...</p>
    </div>

    <div v-else-if="!department.id" class="text-center py-5">
      <i class="bi bi-x-circle display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Department Not Found</h4>
      <button @click="router.push('/admin-dashboard/departments')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Departments
      </button>
    </div>

    <div v-else>
      <!-- Department Header -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="profile-avatar rounded profile-avatar-department">
                <i class="bi bi-building"></i>
              </div>
            </div>
            <div class="col">
              <h3 class="mb-1 fw-bold">{{ department.name }}</h3>
              <p class="text-muted mb-2">
                <i class="bi bi-hash me-1"></i>{{ department.code }}
              </p>
              <div class="d-flex flex-wrap gap-2">
                <span :class="['badge', department.is_active ? 'bg-success' : 'bg-warning']">
                  {{ department.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span class="badge bg-info" v-if="department.institution_name">
                  {{ department.institution_name }}
                </span>
              </div>
            </div>
            <div class="col-auto">
              <button @click="router.push(`/admin-dashboard/departments/edit/${department.id}`)" class="btn btn-admin-primary">
                <i class="bi bi-pencil me-2"></i>Edit Department
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Department Information -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-info-circle me-2 text-admin"></i>Department Information</h6>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">Name</span>
                <span class="info-value">{{ department.name }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Code</span>
                <span class="info-value"><span class="badge bg-dark">{{ department.code }}</span></span>
              </div>
              <div class="info-row">
                <span class="info-label">Head of Department</span>
                <span class="info-value">{{ department.head_of_department || 'Not Assigned' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Institution</span>
                <span class="info-value">{{ department.institution_name || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Email</span>
                <span class="info-value">
                  <a v-if="department.email" :href="`mailto:${department.email}`">{{ department.email }}</a>
                  <span v-else>N/A</span>
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">Phone</span>
                <span class="info-value">{{ department.phone || 'N/A' }}</span>
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
              <p v-if="department.description" class="text-muted">{{ department.description }}</p>
              <p v-else class="text-muted fst-italic">No description available</p>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="col-12">
          <div class="row g-4">
            <div class="col-md-4">
              <div class="stat-card bg-admin-light" @click="scrollTo('programs')">
                <i class="bi bi-mortarboard stat-icon text-admin"></i>
                <div class="stat-content">
                  <h3>{{ programs.length }}</h3>
                  <p>Programs/Courses</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="stat-card bg-success-light" @click="scrollTo('teachers')">
                <i class="bi bi-person-workspace stat-icon text-success"></i>
                <div class="stat-content">
                  <h3>{{ teachers.length }}</h3>
                  <p>Teachers</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="stat-card bg-info-light">
                <i class="bi bi-people stat-icon text-info"></i>
                <div class="stat-content">
                  <h3>{{ stats.totalStudents }}</h3>
                  <p>Total Students</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Programs/Courses -->
        <div class="col-12" id="programs">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-mortarboard me-2 text-admin"></i>Programs/Courses</h6>
              <div>
                <span class="badge bg-admin me-2">{{ programs.length }} Programs</span>
                <button @click="router.push({ name: 'AddCourse', query: { department: department.id } })" class="btn btn-sm btn-outline-primary py-0" title="Add Course">
                  <i class="bi bi-plus-lg"></i>
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <div v-if="programs.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No programs in this department</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Code</th>
                      <th>Program Name</th>
                      <th>Duration</th>
                      <th>Semesters</th>
                      <th>Students</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="prog in programs" :key="prog.id">
                      <td><span class="badge bg-dark">{{ prog.code }}</span></td>
                      <td>{{ prog.name }}</td>
                      <td>{{ prog.duration_years }} Years</td>
                      <td><span class="badge bg-info">{{ prog.semester_count || 0 }}</span></td>
                      <td><span class="badge bg-success">{{ prog.student_count || 0 }}</span></td>
                      <td>
                        <button @click="router.push(`/admin-dashboard/courses/${prog.id}`)" class="btn btn-sm btn-outline-primary">
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

        <!-- Teachers -->
        <div class="col-12" id="teachers">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-person-workspace me-2 text-success"></i>Teachers</h6>
              <div>
                <span class="badge bg-success me-2">{{ teachers.length }} Teachers</span>
                <button @click="router.push({ name: 'AddTeacher', query: { department: department.id } })" class="btn btn-sm btn-outline-success py-0" title="Add Teacher">
                  <i class="bi bi-plus-lg"></i>
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <div v-if="teachers.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No teachers in this department</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Name</th>
                      <th>Designation</th>
                      <th>Email</th>

                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="t in teachers" :key="t.id">
                      <td class="fw-semibold">{{ t.full_name }}</td>
                      <td><span class="badge bg-info">{{ t.designation || 'N/A' }}</span></td>
                      <td>{{ t.email }}</td>

                      <td>
                        <button @click="router.push(`/admin-dashboard/teachers/${t.id}`)" class="btn btn-sm btn-outline-primary">
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
import { departmentService } from '@/services/departmentService'

const router = useRouter()
const route = useRoute()
const departmentId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Departments', href: '/admin-dashboard/departments' },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/departments') }
]

const loading = ref(true)
const department = ref({})
const programs = ref([])
const teachers = ref([])

const stats = computed(() => ({
  totalStudents: programs.value.reduce((sum, p) => sum + (p.student_count || 0), 0)
}))

const scrollTo = (id) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

const loadDepartment = async () => {
  loading.value = true
  try {
    department.value = await departmentService.getDepartmentById(departmentId)
    
    // Load programs
    try {
      const progData = await departmentService.getDepartmentPrograms(departmentId)
      programs.value = Array.isArray(progData) ? progData : (progData.results || [])
    } catch (e) { console.log('Could not load programs:', e) }
    
    // Load teachers
    try {
      const teacherData = await departmentService.getDepartmentTeachers(departmentId)
      teachers.value = Array.isArray(teacherData) ? teacherData : (teacherData.results || [])
    } catch (e) { console.log('Could not load teachers:', e) }
  } catch (error) {
    console.error('Error loading department:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (departmentId && departmentId !== 'profile') {
    loadDepartment()
  } else {
    loading.value = false
  }
})
</script>


