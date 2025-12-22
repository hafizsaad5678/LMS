<template>
  <AdminPageTemplate
    title="Add New Subject"
    subtitle="Create a new academic subject"
    icon="bi bi-book-half"
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
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-book me-2 text-admin"></i>
              Subject Information
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit">
              <!-- Basic Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-info-circle me-2"></i>Basic Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-8">
                    <BaseInput
                      v-model="form.name"
                      label="Subject Name"
                      type="text"
                      placeholder="e.g., Data Structures and Algorithms"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-4">
                    <BaseInput
                      v-model="form.code"
                      label="Subject Code"
                      type="text"
                      placeholder="e.g., CS201"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-4">
                    <BaseInput
                      v-model.number="form.credit_hours"
                      label="Credit Hours"
                      type="number"
                      placeholder="3"
                      :required="true"
                    />
                  </div>
                </div>
              </div>

              <!-- Academic Placement - Cascading Selection -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-diagram-3 me-2"></i>Academic Placement
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
                      <small class="text-muted">Step 1: Select the department</small>
                    </div>
                  </div>

                  <!-- Step 2: Select Course/Program -->
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Course/Program <span class="text-danger">*</span></label>
                      <select v-model="selectedProgram" class="form-select" required :disabled="!selectedDepartment" @change="onProgramChange">
                        <option value="">{{ !selectedDepartment ? 'Select Department First' : 'Select Course' }}</option>
                        <option v-for="prog in filteredPrograms" :key="prog.id" :value="prog.id">
                          {{ prog.name }} ({{ prog.code }})
                        </option>
                      </select>
                      <small class="text-muted">Step 2: Select course like BSCS, BBA</small>
                    </div>
                  </div>

                  <!-- Step 3: Select Semester -->
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Semester <span class="text-danger">*</span></label>
                      <select v-model="form.semester" class="form-select" required :disabled="!selectedProgram || loadingSemesters">
                        <option value="">{{ loadingSemesters ? 'Loading...' : (!selectedProgram ? 'Select Course First' : 'Select Semester') }}</option>
                        <option v-for="sem in semesters" :key="sem.id" :value="sem.id">
                          {{ sem.name }} (Semester {{ sem.number }})
                        </option>
                      </select>
                      <small class="text-muted">Step 3: Assign to a semester</small>
                    </div>
                  </div>
                </div>
                
                <div v-if="selectedProgram && semesters.length === 0 && !loadingSemesters" class="alert alert-warning">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  No semesters found for this course. Please create semesters first.
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-text-paragraph me-2"></i>Description
                </h6>
                <textarea 
                  v-model="form.description" 
                  class="form-control" 
                  rows="4" 
                  placeholder="Enter subject description, learning objectives, prerequisites..."
                ></textarea>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-admin-outline px-4" :disabled="submitting">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
                  <span v-if="submitting">
                    <span class="spinner-border spinner-border-sm me-2"></span>Adding...
                  </span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Add Subject</span>
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
import { subjectService } from '@/services/subjectService'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Subjects', href: '/admin-dashboard/subjects' },
  { name: 'Add Subject' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/subjects') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const submitting = ref(false)
const loadingSemesters = ref(false)

// Dropdown data
const departments = ref([])
const programs = ref([])
const semesters = ref([])

// Selected values for cascading
const selectedDepartment = ref('')
const selectedProgram = ref('')

// Filter programs by selected department
const filteredPrograms = computed(() => {
  if (!selectedDepartment.value) return []
  return programs.value.filter(p => p.department === selectedDepartment.value)
})

const form = ref({
  name: '',
  code: '',
  semester: '',
  credit_hours: 3,
  description: ''
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

// When department changes, reset program and semesters
const onDepartmentChange = () => {
  selectedProgram.value = ''
  form.value.semester = ''
  semesters.value = []
}

// When program/course changes, load semesters
const onProgramChange = () => {
  form.value.semester = ''
  loadSemestersForProgram(selectedProgram.value)
}

// Load semesters for selected program
const loadSemestersForProgram = async (programId) => {
  if (!programId) {
    semesters.value = []
    return
  }
  
  loadingSemesters.value = true
  try {
    const response = await api.get(`/programs/${programId}/semesters/`)
    semesters.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading semesters:', error)
    // Fallback to all semesters filtered by program
    try {
      const res = await api.get('/semesters/', { params: { program: programId } })
      semesters.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
    } catch (e) {
      console.error('Fallback failed:', e)
    }
  } finally {
    loadingSemesters.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.semester) delete data.semester
    
    await subjectService.createSubject(data)
    showAlert('success', 'Subject has been added successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/subjects'), 1500)
  } catch (error) {
    console.error('Error adding subject:', error)
    const msg = error.response?.data?.detail || error.response?.data?.code?.[0] || 'Failed to add subject.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  const hasData = Object.values(form.value).some(val => val !== '' && val !== 3)
  if (hasData) {
    if (confirm('Are you sure? All unsaved changes will be lost.')) {
      router.push('/admin-dashboard/subjects')
    }
  } else {
    router.push('/admin-dashboard/subjects')
  }
}

onMounted(async () => {
  await Promise.all([loadDepartments(), loadPrograms()])
  
  if (route.query.semester) {
    const semId = route.query.semester
    try {
      // Fetch semester to get program link
      const semRes = await api.get(`/semesters/${semId}/`)
      const sem = semRes.data || semRes
      const progId = sem.program
      if (progId) {
        // Fetch program to get department link
        const progRes = await api.get(`/programs/${progId}/`)
        const prog = progRes.data || progRes
        const deptId = prog.department?.id || prog.department // Handle object or ID
        
        if (deptId) {
          selectedDepartment.value = deptId
          // Set program directly without resetting (avoid onDepartmentChange side-effects if any)
          selectedProgram.value = progId
          
          await loadSemestersForProgram(progId)
          form.value.semester = semId
        }
      }
    } catch (e) {
      console.error('Error auto-filling from semester query:', e)
    }
  }
})
</script>

<style scoped>
.form-control:focus, .form-select:focus { border-color: #dc3545; box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.15); }
.card { border-radius: 12px; }
.card-header { background: linear-gradient(135deg, rgba(220, 53, 69, 0.05) 0%, rgba(220, 53, 69, 0.02) 100%); }
.text-admin { color: #dc3545; }
</style>
