<template>
  <AdminPageTemplate
    title="Edit Teacher"
    subtitle="Update teacher information"
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
      <div class="spinner-border text-admin" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading teacher details...</p>
    </div>

    <div v-else-if="!teacherId" class="text-center py-5">
      <div class="mb-4">
        <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
          <i class="bi bi-person-gear display-4"></i>
        </div>
        <h4 class="text-muted">No Teacher Selected</h4>
        <p class="text-muted mb-4">Please select a teacher from the list to edit.</p>
        <button @click="router.push('/admin-dashboard/teachers')" class="btn btn-admin-primary">
          <i class="bi bi-list-ul me-2"></i>Go to Teacher List
        </button>
      </div>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-10">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-person-workspace me-2 text-admin"></i>
              Teacher Information
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit">
              <!-- Read-only Info -->
              <div class="mb-4 p-3 bg-light rounded">
                <div class="row">
                  <div class="col-md-6">
                    <label class="form-label text-muted small mb-1">Employee ID</label>
                    <p class="fw-semibold mb-0">{{ employeeId }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted small mb-1">Current Department</label>
                    <p class="fw-semibold mb-0">{{ currentDepartmentName || 'Not Assigned' }}</p>
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
                      <label for="edit-gender-select" class="form-label">Gender <span class="text-danger">*</span></label>
                      <select id="edit-gender-select" v-model="form.gender" class="form-select" required>
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

              <!-- Professional Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-briefcase me-2"></i>Professional Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="edit-department-select" class="form-label">Department <span class="text-danger">*</span></label>
                      <select id="edit-department-select" v-model="form.department" class="form-select" required>
                        <option value="">Select Department</option>
                        <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                          {{ dept.name }} ({{ dept.code }})
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="edit-designation-select" class="form-label">Designation</label>
                      <select id="edit-designation-select" v-model="form.designation" class="form-select">
                        <option value="">Select Designation</option>
                        <option value="Professor">Professor</option>
                        <option value="Associate Professor">Associate Professor</option>
                        <option value="Assistant Professor">Assistant Professor</option>
                        <option value="Lecturer">Lecturer</option>
                        <option value="Lab Instructor">Lab Instructor</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.qualification" label="Qualification" type="text" placeholder="e.g., PhD Computer Science" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.specialization" label="Specialization" type="text" placeholder="e.g., Machine Learning" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.joining_date" label="Joining Date" type="date" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model.number="form.experience_years" label="Years of Experience" type="number" />
                  </div>
                </div>
              </div>

              <!-- Teaching Subjects -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-book me-2"></i>Teaching Subjects
                </h6>
                <div v-if="loadingSubjects" class="text-muted">
                  <span class="spinner-border spinner-border-sm me-2"></span>Loading subjects...
                </div>
                <div v-else-if="subjects.length === 0" class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>No subjects available.
                </div>
                <div v-else class="subjects-grid">
                  <div v-for="subject in subjects" :key="subject.id" class="form-check subject-item">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      :id="'subject-' + subject.id"
                      :value="subject.id"
                      v-model="form.teaching_subjects"
                    >
                    <label class="form-check-label" :for="'subject-' + subject.id">
                      <span class="badge bg-dark me-2">{{ subject.code }}</span>
                      {{ subject.name }}
                    </label>
                  </div>
                </div>
                <small class="text-muted mt-2 d-block">Selected: {{ form.teaching_subjects.length }} subject(s)</small>
              </div>

              <!-- Address Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-geo-alt me-2"></i>Address Information
                </h6>
                <div class="row g-3">
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
                  <span v-else><i class="bi bi-check-circle me-2"></i>Update Teacher</span>
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { teacherService } from '@/services/teacherService'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const teacherId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Teachers', href: '/admin-dashboard/teachers' },
  { name: 'Edit Teacher' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/teachers') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(true)
const submitting = ref(false)
const loadingSubjects = ref(false)
const employeeId = ref('')
const currentDepartmentName = ref('')

// Dropdown data
const departments = ref([])
const subjects = ref([])

const form = ref({
  full_name: '',
  email: '',
  phone: '',
  date_of_birth: '',
  gender: '',
  cnic: '',
  department: '',
  designation: '',
  qualification: '',
  specialization: '',
  joining_date: '',
  experience_years: 0,
  teaching_subjects: [],
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

const loadSubjects = async () => {
  loadingSubjects.value = true
  try {
    const response = await api.get('/subjects/')
    subjects.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading subjects:', error)
  } finally {
    loadingSubjects.value = false
  }
}

const loadTeacher = async () => {
  loading.value = true
  try {
    const teacher = await teacherService.getTeacher(teacherId)
    employeeId.value = teacher.employee_id
    currentDepartmentName.value = teacher.department_name || (teacher.department?.name) || ''
    
    form.value = {
      full_name: teacher.full_name || '',
      email: teacher.email || '',
      phone: teacher.phone || '',
      date_of_birth: teacher.date_of_birth || '',
      gender: teacher.gender || '',
      cnic: teacher.cnic || '',
      department: teacher.department || '',
      designation: teacher.designation || '',
      qualification: teacher.qualification || '',
      specialization: teacher.specialization || '',
      joining_date: teacher.joining_date || '',
      experience_years: teacher.experience_years || 0,
      teaching_subjects: [],
      address: teacher.address || '',
      city: teacher.city || ''
    }
    
    // Load currently assigned subjects
    try {
      const assigned = await api.get(`/teachers/${teacherId}/teaching_subjects/`)
      const assignedData = Array.isArray(assigned.data) ? assigned.data : (assigned.data.results || [])
      form.value.teaching_subjects = assignedData.map(a => a.subject || a.subject_id || a.id)
    } catch (e) { console.warn('Could not load teaching subjects:', e) }
    
  } catch (error) {
    console.error('Error loading teacher:', error)
    showAlert('error', 'Failed to load teacher details', 'Error')
    setTimeout(() => router.push('/admin-dashboard/teachers'), 2000)
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

    const teacherData = {
      full_name: form.value.full_name,
      email: form.value.email,
      phone: form.value.phone,
      date_of_birth: form.value.date_of_birth || null,
      gender: form.value.gender,
      cnic: form.value.cnic && form.value.cnic.trim() ? form.value.cnic : null,
      department: form.value.department || null,
      designation: form.value.designation || null,
      qualification: form.value.qualification || null,
      specialization: form.value.specialization || null,
      joining_date: form.value.joining_date || null,
      experience_years: form.value.experience_years || 0,
      address: form.value.address || null,
      city: form.value.city || null
    }

    await teacherService.updateTeacher(teacherId, teacherData)
    
    // Update subject assignments
    for (const subjectId of form.value.teaching_subjects) {
      try {
        await api.post('/teacher-subjects/', { teacher: teacherId, subject: subjectId })
      } catch (e) { /* Already assigned */ }
    }
    
    showAlert('success', 'Teacher updated successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/teachers'), 1500)
  } catch (error) {
    console.error('Error updating teacher:', error)
    const msg = error.response?.data?.detail || error.response?.data?.cnic?.[0] || error.response?.data?.email?.[0] || 'Failed to update teacher.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  router.push('/admin-dashboard/teachers')
}

onMounted(async () => {
  await Promise.all([loadDepartments(), loadSubjects()])
  if (teacherId) {
    await loadTeacher()
  } else {
    loading.value = false
  }
})
</script>

<style scoped>
.form-control:focus, .form-select:focus { border-color: #0d6efd; box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.15); }
.card { border-radius: 12px; }
.card-header { background: linear-gradient(135deg, rgba(13, 110, 253, 0.05) 0%, rgba(13, 110, 253, 0.02) 100%); }

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

.subject-item:hover { border-color: #0d6efd; }
.form-check-input:checked { background-color: #0d6efd; border-color: #0d6efd; }
</style>
