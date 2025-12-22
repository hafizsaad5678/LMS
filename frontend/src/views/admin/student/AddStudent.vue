<template>
  <AdminPageTemplate
    title="Add New Student"
    subtitle="Register a new student in the system"
    icon="bi bi-person-plus-fill"
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

    <div class="row justify-content-center">
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
              <!-- Personal Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-person me-2"></i>Personal Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <BaseInput
                      v-model="form.full_name"
                      label="Full Name"
                      type="text"
                      placeholder="Enter full name"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model="form.email"
                      label="Email"
                      type="email"
                      placeholder="student@college.edu"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model="form.phone"
                      label="Phone Number"
                      type="tel"
                      placeholder="+92 300-1234567"
                    />
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model="form.date_of_birth"
                      label="Date of Birth"
                      type="date"
                    />
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="add-student-gender" class="form-label">Gender <span class="text-danger">*</span></label>
                      <select id="add-student-gender" v-model="form.gender" class="form-select" required>
                        <option value="">Select Gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model="form.cnic"
                      label="CNIC"
                      type="text"
                      placeholder="12345-1234567-1"
                    />
                  </div>
                </div>
              </div>

              <!-- Academic Information - Cascading Selection -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-mortarboard me-2"></i>Academic Information
                </h6>
                <div class="row g-3">
                  <!-- Step 1: Select Department -->
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Department <span class="text-danger">*</span></label>
                      <select v-model="selectedDepartment" class="form-select" required @change="onDepartmentChange">
                        <option value="">Select Department</option>
                        <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                          {{ dept.name }} ({{ dept.code }})
                        </option>
                      </select>
                      <small class="text-muted">Step 1: First select the department</small>
                    </div>
                  </div>

                  <!-- Step 2: Select Course/Program -->
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Course/Program <span class="text-danger">*</span></label>
                      <select v-model="form.program" class="form-select" required :disabled="!selectedDepartment" @change="onProgramChange">
                        <option value="">{{ loadingPrograms ? 'Loading...' : 'Select Course' }}</option>
                        <option v-for="prog in filteredPrograms" :key="prog.id" :value="prog.id">
                          {{ prog.name }} ({{ prog.code }})
                        </option>
                      </select>
                      <small class="text-muted">Step 2: Select course like BSCS, BBA</small>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <BaseInput
                      v-model.number="form.enrollment_year"
                      label="Enrollment Year"
                      type="number"
                      placeholder="2024"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model.number="form.current_semester"
                      label="Current Semester"
                      type="number"
                      placeholder="1"
                      :required="true"
                    />
                  </div>
                </div>
              </div>

              <!-- Subject Enrollment (Multi-Select) -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-book me-2"></i>Subject Enrollment (Step 3)
                </h6>
                <div class="row">
                  <div class="col-12">
                    <label class="form-label">Select Subjects to Enroll</label>
                    <div v-if="loadingSubjects" class="text-muted">
                      <span class="spinner-border spinner-border-sm me-2"></span>Loading subjects...
                    </div>
                    <div v-else-if="availableSubjects.length === 0" class="alert alert-info">
                      <i class="bi bi-info-circle me-2"></i>
                      {{ form.program ? 'No subjects available for this course.' : 'Please select a department and course first.' }}
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
                          <small class="text-muted ms-2">({{ subject.credit_hours }} Cr)</small>
                        </label>
                      </div>
                    </div>
                    <small class="text-muted mt-2 d-block">
                      Selected: {{ form.enrolled_subjects.length }} subject(s)
                    </small>
                  </div>
                </div>
              </div>

              <!-- Guardian Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-people me-2"></i>Guardian Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <BaseInput v-model="form.father_name" label="Father's Name" type="text" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.guardian_phone" label="Guardian Phone" type="tel" />
                  </div>
                </div>
              </div>

              <!-- Address Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-geo-alt me-2"></i>Address Information
                </h6>
                <div class="row g-3">
                  <div class="col-12">
                    <textarea v-model="form.address" class="form-control" rows="2" placeholder="Enter address"></textarea>
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.city" label="City" type="text" placeholder="e.g., Karachi" />
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
                    <span class="spinner-border spinner-border-sm me-2"></span>Adding Student...
                  </span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Add Student</span>
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
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { studentService } from '@/services/studentservices'
import api from '@/services/api'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Students', href: '/admin-dashboard/students' },
  { name: 'Add Student' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/students') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const submitting = ref(false)
const loadingPrograms = ref(false)
const loadingSubjects = ref(false)

// Dropdown data
const departments = ref([])
const programs = ref([])
const availableSubjects = ref([])

// Selected values for cascading
const selectedDepartment = ref('')

// Filter programs by selected department
const filteredPrograms = computed(() => {
  if (!selectedDepartment.value) return []
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

// Load all departments
const loadDepartments = async () => {
  try {
    const response = await api.get('/departments/')
    departments.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

// Load all programs/courses
const loadPrograms = async () => {
  try {
    const response = await api.get('/programs/')
    programs.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading programs:', error)
  }
}

// When department changes, reset program and subjects
const onDepartmentChange = () => {
  form.value.program = ''
  form.value.enrolled_subjects = []
  availableSubjects.value = []
}

// When program/course changes, load subjects for that program
const onProgramChange = () => {
  form.value.enrolled_subjects = []
  loadSubjectsForProgram(form.value.program)
}

// Load subjects for selected program
const loadSubjectsForProgram = async (programId) => {
  if (!programId) {
    availableSubjects.value = []
    return
  }
  
  loadingSubjects.value = true
  try {
    // Get semesters for this program, then subjects from each semester
    const semResponse = await api.get(`/programs/${programId}/semesters/`)
    const semesters = Array.isArray(semResponse.data) ? semResponse.data : (semResponse.data.results || [])
    
    const subjects = []
    for (const sem of semesters) {
      try {
        const subResponse = await api.get(`/semesters/${sem.id}/subjects/`)
        const semSubjects = Array.isArray(subResponse.data) ? subResponse.data : (subResponse.data.results || [])
        semSubjects.forEach(s => {
          s.semester_name = sem.name
          subjects.push(s)
        })
      } catch (e) { console.warn('Could not load subjects for semester:', sem.id) }
    }
    availableSubjects.value = subjects
  } catch (error) {
    console.error('Error loading subjects:', error)
    // Fallback: try getting all subjects
    try {
      const response = await api.get('/subjects/')
      availableSubjects.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
    } catch (e) { console.error('Fallback failed:', e) }
  } finally {
    loadingSubjects.value = false
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

    // Prepare student data
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

    // Create student
    const createdStudent = await studentService.createStudent(studentData)
    
    // Enroll in subjects if any selected
    if (form.value.enrolled_subjects.length > 0) {
      for (const subjectId of form.value.enrolled_subjects) {
        try {
          await api.post('/student-subjects/', {
            student: createdStudent.id,
            subject: subjectId
          })
        } catch (e) {
          console.warn('Could not enroll in subject:', subjectId, e)
        }
      }
    }
    
    showAlert('success', 'Student has been added successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/students'), 1500)
  } catch (error) {
    console.error('Error adding student:', error)
    const msg = error.response?.data?.detail || error.response?.data?.cnic?.[0] || error.response?.data?.email?.[0] || 'Failed to add student.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  if (confirm('Are you sure? All unsaved changes will be lost.')) {
    router.push('/admin-dashboard/students')
  }
}

onMounted(async () => {
  await Promise.all([loadDepartments(), loadPrograms()])
})
</script>

<style scoped>
.form-control:focus, .form-select:focus { border-color: #dc3545; box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.15); }
.card { border-radius: 12px; }
.card-header { background: linear-gradient(135deg, rgba(220, 53, 69, 0.05) 0%, rgba(220, 53, 69, 0.02) 100%); }
.text-admin { color: #dc3545; }

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
  max-height: 300px;
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
  transition: all 0.2s;
}

.subject-item:hover {
  border-color: #dc3545;
  background: rgba(220, 53, 69, 0.02);
}

.form-check-input:checked {
  background-color: #dc3545;
  border-color: #dc3545;
}
</style>
