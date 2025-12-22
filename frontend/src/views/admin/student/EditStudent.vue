<template>
  <AdminPageTemplate
    title="Edit Student"
    subtitle="Update student information"
    icon="bi bi-person-gear"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="alert.show = false"
    />

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading student details...</p>
    </div>

    <div v-else-if="!studentId" class="text-center py-5">
      <div class="mb-4">
        <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
          <i class="bi bi-person-gear display-4"></i>
        </div>
        <h4 class="text-muted">No Student Selected</h4>
        <p class="text-muted mb-4">Please select a student from the list to edit.</p>
        <button @click="router.push('/admin-dashboard/students')" class="btn btn-admin-primary">
          <i class="bi bi-list-ul me-2"></i>Go to Student List
        </button>
      </div>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-10">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-person-badge me-2 text-admin"></i>
              Student Information
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit">
              <!-- Read-only Info -->
              <div class="mb-4 p-3 bg-light rounded">
                <div class="row">
                  <div class="col-md-4">
                    <label class="form-label text-muted small mb-1">Enrollment Number</label>
                    <p class="fw-semibold mb-0">{{ enrollmentNumber }}</p>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label text-muted small mb-1">Current Department</label>
                    <p class="fw-semibold mb-0">{{ currentDepartmentName || 'Not Assigned' }}</p>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label text-muted small mb-1">Current Program</label>
                    <p class="fw-semibold mb-0">{{ currentProgramName || 'Not Assigned' }}</p>
                  </div>
                </div>
              </div>

              <!-- Personal Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-person me-2"></i>Personal Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <BaseInput v-model="form.full_name" label="Full Name" type="text" :required="true" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.email" label="Email" type="email" :required="true" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.phone" label="Phone Number" type="tel" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.date_of_birth" label="Date of Birth" type="date" />
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="edit-student-gender" class="form-label">Gender <span class="text-danger">*</span></label>
                      <select id="edit-student-gender" v-model="form.gender" class="form-select" required>
                        <option value="">Select Gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.cnic" label="CNIC" type="text" placeholder="12345-1234567-1" />
                  </div>
                </div>
              </div>

              <!-- Academic Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-mortarboard me-2"></i>Academic Information
                </h6>
                <div class="row g-3">
                  <!-- Department Selection -->
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="edit-department-select" class="form-label">Department</label>
                      <select id="edit-department-select" v-model="selectedDepartment" class="form-select" @change="onDepartmentChange">
                        <option value="">Select Department</option>
                        <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                          {{ dept.name }} ({{ dept.code }})
                        </option>
                      </select>
                    </div>
                  </div>
                  <!-- Program/Course Selection -->
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Program/Course</label>
                      <select v-model="form.program" class="form-select" :disabled="!selectedDepartment" @change="onProgramChange">
                        <option value="">{{ !selectedDepartment ? 'Select Department First' : 'Select Course' }}</option>
                        <option v-for="prog in filteredPrograms" :key="prog.id" :value="prog.id">
                          {{ prog.name }} ({{ prog.code }})
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <BaseInput v-model.number="form.enrollment_year" label="Enrollment Year" type="number" />
                  </div>
                  <div class="col-md-3">
                    <BaseInput v-model.number="form.current_semester" label="Current Semester" type="number" />
                  </div>
                </div>
              </div>

              <!-- Subject Enrollment -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-book me-2"></i>Subject Enrollment
                </h6>
                <div v-if="loadingSubjects" class="text-muted">
                  <span class="spinner-border spinner-border-sm me-2"></span>Loading subjects...
                </div>
                <div v-else-if="availableSubjects.length === 0" class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>
                  {{ form.program ? 'No subjects found for this course.' : 'Select a department and course to see subjects.' }}
                </div>
                <div v-else class="subjects-grid">
                  <div v-for="subject in availableSubjects" :key="subject.id" class="form-check subject-item">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      :id="'subject-' + subject.id"
                      :value="subject.id"
                      v-model="form.enrolled_subjects"
                    >
                    <label class="form-check-label" :for="'subject-' + subject.id">
                      <span class="badge bg-dark me-2">{{ subject.code }}</span>
                      {{ subject.name }}
                    </label>
                  </div>
                </div>
                <small class="text-muted mt-2 d-block">Selected: {{ form.enrolled_subjects.length }} subject(s)</small>
              </div>

              <!-- Guardian & Address -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-people me-2"></i>Guardian & Address
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <BaseInput v-model="form.father_name" label="Father's Name" type="text" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.guardian_phone" label="Guardian Phone" type="tel" />
                  </div>
                  <div class="col-12">
                    <div class="mb-3">
                      <label class="form-label">Address</label>
                      <textarea v-model="form.address" class="form-control" rows="2"></textarea>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.city" label="City" type="text" />
                  </div>
                </div>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-admin-outline px-4" :disabled="submitting">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
                  <span v-if="submitting">
                    <span class="spinner-border spinner-border-sm me-2"></span>Updating...
                  </span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Update Student</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { studentService } from '@/services/studentservices'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const studentId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Students', href: '/admin-dashboard/students' },
  { name: 'Edit Student' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/students') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(true)
const submitting = ref(false)
const loadingSubjects = ref(false)
const enrollmentNumber = ref('')
const currentDepartmentName = ref('')
const currentProgramName = ref('')

// Dropdown data
const departments = ref([])
const programs = ref([])
const availableSubjects = ref([])

// Selected values for cascading
const selectedDepartment = ref('')

// Filter programs by selected department
const filteredPrograms = computed(() => {
  if (!selectedDepartment.value) return programs.value
  return programs.value.filter(p => p.department === selectedDepartment.value)
})

const form = ref({
  full_name: '',
  email: '',
  phone: '',
  date_of_birth: '',
  gender: '',
  cnic: '',
  program: '',
  enrollment_year: new Date().getFullYear(),
  current_semester: 1,
  enrolled_subjects: [],
  father_name: '',
  guardian_phone: '',
  address: '',
  city: ''
})

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadDepartments = async () => {
  try {
    const response = await api.get('/departments/')
    departments.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

const loadPrograms = async () => {
  try {
    const response = await api.get('/programs/')
    programs.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading programs:', error)
  }
}

const onDepartmentChange = () => {
  form.value.program = ''
  form.value.enrolled_subjects = []
  availableSubjects.value = []
}

const onProgramChange = () => {
  form.value.enrolled_subjects = []
  loadSubjectsForProgram(form.value.program)
}

const loadSubjectsForProgram = async (programId) => {
  if (!programId) {
    availableSubjects.value = []
    return
  }
  
  loadingSubjects.value = true
  try {
    const semResponse = await api.get(`/programs/${programId}/semesters/`)
    const semesters = Array.isArray(semResponse.data) ? semResponse.data : (semResponse.data.results || [])
    
    const subjects = []
    for (const sem of semesters) {
      try {
        const subResponse = await api.get(`/semesters/${sem.id}/subjects/`)
        const semSubjects = Array.isArray(subResponse.data) ? subResponse.data : (subResponse.data.results || [])
        subjects.push(...semSubjects)
      } catch (e) { console.warn('Could not load subjects for semester:', sem.id) }
    }
    availableSubjects.value = subjects
  } catch (error) {
    console.error('Error loading subjects:', error)
    try {
      const response = await api.get('/subjects/')
      availableSubjects.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
    } catch (e) { console.error('Fallback failed:', e) }
  } finally {
    loadingSubjects.value = false
  }
}

const loadStudent = async () => {
  loading.value = true
  try {
    const student = await studentService.getStudent(studentId)
    enrollmentNumber.value = student.enrollment_number
    currentProgramName.value = student.program_name || ''
    currentDepartmentName.value = student.department_name || ''
    
    form.value = {
      full_name: student.full_name || '',
      email: student.email || '',
      phone: student.phone || '',
      date_of_birth: student.date_of_birth || '',
      gender: student.gender || '',
      cnic: student.cnic || '',
      program: student.program || '',
      enrollment_year: student.enrollment_year || new Date().getFullYear(),
      current_semester: student.current_semester || 1,
      enrolled_subjects: [],
      father_name: student.father_name || '',
      guardian_phone: student.guardian_phone || '',
      address: student.address || '',
      city: student.city || ''
    }
    
    // Find and set the department based on the program
    if (form.value.program) {
      const prog = programs.value.find(p => p.id === form.value.program)
      if (prog && prog.department) {
        selectedDepartment.value = prog.department
        currentDepartmentName.value = departments.value.find(d => d.id === prog.department)?.name || ''
      }
      await loadSubjectsForProgram(form.value.program)
    }
    
    // Load enrolled subjects
    try {
      const enrolled = await api.get(`/students/${studentId}/enrolled_subjects/`)
      const enrolledData = Array.isArray(enrolled.data) ? enrolled.data : (enrolled.data.results || [])
      form.value.enrolled_subjects = enrolledData.map(e => e.subject || e.subject_id || e.id)
    } catch (e) { console.warn('Could not load enrolled subjects:', e) }
    
  } catch (error) {
    console.error('Error loading student:', error)
    showAlert('error', 'Failed to load student details', 'Error')
    setTimeout(() => router.push('/admin-dashboard/students'), 2000)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    // Validate CNIC format if provided
    if (form.value.cnic && form.value.cnic.trim()) {
      const cnicDigits = form.value.cnic.replace('-', '').replace(' ', '').replace(/\D/g, '')
      if (cnicDigits.length !== 13) {
        showAlert('error', 'CNIC must be exactly 13 digits (e.g., 12345-1234567-1)', 'Validation Error!')
        submitting.value = false
        return
      }
    }

    const studentData = {
      full_name: form.value.full_name,
      email: form.value.email,
      phone: form.value.phone || null,
      date_of_birth: form.value.date_of_birth || null,
      gender: form.value.gender,
      cnic: form.value.cnic && form.value.cnic.trim() ? form.value.cnic : null,
      program: form.value.program || null,
      enrollment_year: form.value.enrollment_year,
      current_semester: form.value.current_semester,
      father_name: form.value.father_name || null,
      guardian_phone: form.value.guardian_phone || null,
      address: form.value.address || null,
      city: form.value.city || null
    }

    await studentService.updateStudent(studentId, studentData)
    
    // Update subject enrollments
    for (const subjectId of form.value.enrolled_subjects) {
      try {
        await api.post('/student-subjects/', { student: studentId, subject: subjectId })
      } catch (e) { /* Already enrolled */ }
    }
    
    showAlert('success', 'Student updated successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/students'), 1500)
  } catch (error) {
    console.error('Error updating student:', error)
    const msg = error.response?.data?.detail || error.response?.data?.cnic?.[0] || error.response?.data?.email?.[0] || 'Failed to update student.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  router.push('/admin-dashboard/students')
}

onMounted(async () => {
  await Promise.all([loadDepartments(), loadPrograms()])
  if (studentId) {
    await loadStudent()
  } else {
    loading.value = false
  }
})
</script>

<style scoped>
.form-control:focus, .form-select:focus { border-color: #dc3545; box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.15); }
.card { border-radius: 12px; }
.card-header { background: linear-gradient(135deg, rgba(220, 53, 69, 0.05) 0%, rgba(220, 53, 69, 0.02) 100%); }
.text-admin { color: #dc3545; }
.avatar-circle-lg { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.75rem;
  max-height: 250px;
  overflow-y: auto;
  padding: 1rem;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #f8f9fa;
}

.subject-item {
  background: white;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.subject-item:hover { border-color: #dc3545; }
.form-check-input:checked { background-color: #dc3545; border-color: #dc3545; }
</style>
