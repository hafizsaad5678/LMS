<template>
  <section id="admissions" class="py-5">
    <div class="container py-4">
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-3 mb-5">
        <div>
          <p class="text-uppercase fw-bold mb-2 text-brand tracking-wider small">Admissions</p>
          <h2 class="mb-0 title-font fs-clamp-lg">Session & Admission Details</h2>
        </div>
      </div>

      <!-- Top Admission Info Block -->
      <div v-if="admissions" class="card border-0 shadow-sm rounded-4 overflow-hidden">
        <div class="card-body p-4 p-md-5">
          <div class="d-flex align-items-start gap-4 flex-column flex-md-row">
            <div class="bg-light rounded-circle p-3 d-flex align-items-center justify-content-center flex-shrink-0 size-64">
              <i class="bi bi-journal-text fs-3 text-brand"></i>
            </div>
            <div>
              <h3 class="h4 fw-bold mb-3">{{ admissions.title || 'Admissions' }}</h3>
               <p class="text-secondary mb-0 lh-lg fs-5">
                {{ admissions.description || 'Admissions details will be shared soon.' }}
              </p>
              
              <div class="d-flex flex-wrap gap-3 mt-4">
                <button 
                  v-if="openPrograms.length > 0"
                  @click="openApplyModal(null)"
                  data-bs-toggle="modal" 
                  data-bs-target="#applyModal"
                  class="btn btn-brand-primary rounded-pill px-4 py-2 fw-bold shadow-sm"
                >
                  <i class="bi bi-pencil-square me-2"></i>Apply Now
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card border-0 bg-light rounded-4 border-dashed p-5 text-center">
        <p class="text-secondary mb-0">No admissions info available.</p>
      </div>

      <!-- Program Admissions Grid -->
      <div class="mt-5">
        <div class="d-flex align-items-end justify-content-between flex-wrap gap-3 mb-4">
          <div>
            <p class="text-uppercase fw-bold mb-2 text-brand tracking-wider small">Program Admissions</p>
            <h3 class="mb-0 title-font fs-clamp-md">Open Intakes & Deadlines</h3>
          </div>
        </div>

        <div v-if="openPrograms.length" class="row g-4">
          <div v-for="program in openPrograms" :key="program.id" class="col-md-6 col-lg-4">
            <div class="card h-100 border-0 shadow-sm rounded-4 program-admission-card">
              <div class="card-body p-4 d-flex flex-column">
                <div class="d-flex align-items-start justify-content-between mb-2">
                  <div>
                    <p class="small text-uppercase text-muted mb-1 tracking-wider extra-extra-small">{{ formatLevel(program.program_level) }}</p>
                    <h5 class="fw-bold mb-1">{{ program.name }}</h5>
                    <p class="small text-muted mb-0">{{ program.department_name || 'Department' }}</p>
                  </div>
                  <span class="badge rounded-pill px-3 py-1 bg-success">
                    Admissions Open
                  </span>
                </div>

                <div v-if="getAdmissionSession(program)" class="small text-muted mt-3">
                  <div class="d-flex align-items-center gap-2">
                    <i class="bi bi-calendar-range text-brand"></i>
                    <span>{{ formatAdmissionWindow(getAdmissionSession(program)) }}</span>
                  </div>
                </div>

                <div class="mt-auto pt-4">
                  <button 
                    @click="openApplyModal(program)"
                    data-bs-toggle="modal" 
                    data-bs-target="#applyModal"
                    class="btn btn-sm btn-brand-outline w-100 rounded-pill fw-bold"
                  >
                    Quick Apply
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="card border-0 bg-light rounded-4 border-dashed p-5 text-center">
          <p class="text-secondary mb-0">No programs currently open for admissions.</p>
        </div>
      </div>
    </div>

    <!-- Application Modal -->
    <div class="modal fade" id="applyModal" tabindex="-1" aria-labelledby="applyModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 rounded-4 shadow-lg overflow-hidden">
          <div class="modal-header bg-brand-primary text-white border-0 py-3">
            <h5 class="modal-title fw-bold" id="applyModalLabel">
              <i class="bi bi-send-fill me-2"></i>Online Admission Inquiry
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close" id="closeModalBtn" @click="resetForm"></button>
          </div>
          <div class="modal-body p-4">
            <!-- Professional Alert Component Area -->
            <transition name="fade">
              <div v-if="alert.show" :class="['alert alert-dismissible fade show rounded-3 mb-4 d-flex align-items-center', alert.type === 'success' ? 'alert-success border-success' : 'alert-danger border-danger']" role="alert">
                <i :class="['bi me-2 fs-5', alert.type === 'success' ? 'bi-check-circle-fill text-success' : 'bi-exclamation-triangle-fill text-danger']"></i>
                <div class="flex-grow-1">{{ alert.message }}</div>
                <button type="button" class="btn-close shadow-none" @click="alert.show = false"></button>
              </div>
            </transition>

            <form v-if="!submittedSuccessfully" @submit.prevent="submitApplication" id="admissionForm">
              <p class="text-secondary small mb-4">Please fill in your details to inquire about admissions. Only programs currently open for admission are listed.</p>
              
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted text-uppercase">Full Name</label>
                <input v-model="form.name" type="text" class="form-control rounded-3 shadow-none border-2" placeholder="Enter your full name" required>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold text-muted text-uppercase">Father's Name</label>
                <input v-model="form.father_name" type="text" class="form-control rounded-3 shadow-none border-2" placeholder="Enter father's name" required>
              </div>

              <div class="row g-3 mb-3">
                <div class="col-md-6">
                  <label class="form-label small fw-bold text-muted text-uppercase">Phone Number</label>
                  <input v-model="form.phone" type="tel" class="form-control rounded-3 shadow-none border-2" placeholder="e.g. 03001234567" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-bold text-muted text-uppercase">Email Address</label>
                  <input v-model="form.email" type="email" class="form-control rounded-3 shadow-none border-2" placeholder="yourname@gmail.com" required>
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label small fw-bold text-muted text-uppercase">Interested Program</label>
                <select v-model="form.program_id" class="form-select rounded-3 shadow-none border-2" required>
                  <option value="" disabled>Select an open program</option>
                  <optgroup v-for="dept in departmentsWithOpenPrograms" :key="dept.id" :label="dept.name">
                    <option v-for="prog in getOpenProgramsByDept(dept)" :key="prog.id" :value="prog.id">
                      {{ prog.name }}
                    </option>
                  </optgroup>
                </select>
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-brand-primary py-2 fw-bold rounded-3 h-100" :disabled="isSubmitting">
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isSubmitting ? 'Processing...' : 'Submit Application' }}
                </button>
              </div>
            </form>

            <!-- Success Message View -->
            <div v-else class="text-center py-4">
              <div class="mb-3 animate__animated animate__zoomIn">
                <i class="bi bi-check-circle-fill text-success display-1"></i>
              </div>
              <h3 class="fw-bold mb-2">Application Sent!</h3>
              <p class="text-secondary px-3">Your admission inquiry for the program has been successfully delivered to the relevant department. We will contact you soon!</p>
              <button type="button" class="btn btn-brand-primary px-5 rounded-pill mt-3 fw-bold" data-bs-dismiss="modal" @click="resetForm">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/services/shared/core/api' // Use the configured API instance

const props = defineProps({
  admissions: {
    type: Object,
    default: null
  },
  departments: {
    type: Array,
    default: () => []
  },
  institution: {
    type: Object,
    default: null
  }
})

const isSubmitting = ref(false)
const submittedSuccessfully = ref(false)
const alert = ref({
  show: false,
  type: 'success',
  message: ''
})

const form = ref({
  name: '',
  father_name: '',
  phone: '',
  email: '',
  program_id: ''
})

const showAlert = (type, message) => {
  alert.value = { show: true, type, message }
}

const openApplyModal = (program) => {
  resetForm()
  if (program) {
    form.value.program_id = program.id
  } else if (openPrograms.value.length > 0) {
    form.value.program_id = openPrograms.value[0].id
  }
}

const resetForm = () => {
  form.value = { name: '', father_name: '', phone: '', email: '', program_id: '' }
  submittedSuccessfully.value = false
  alert.value.show = false
}

const submitApplication = async () => {
  try {
    isSubmitting.value = true
    alert.value.show = false
    
    // Correctly using the 'api' instance which has the baseURL set to the Django server
    const response = await api.post('/institution/inquiry/', {
      ...form.value,
      institution_id: props.institution?.id
    })
    
    // Check for success or partial_success (if inquiry received but email failed)
    if (response.data.status === 'success' || response.data.status === 'partial_success') {
      submittedSuccessfully.value = true
    } else {
      throw new Error(response.data.message || 'Submission failed')
    }
  } catch (error) {
    console.error('Error submitting application:', error)
    const errorMsg = error.response?.data?.error || 
                     error.response?.data?.message || 
                     error.userMessage || 
                     'The server is currently unavailable. Please try again later or contact the institution directly.';
    showAlert('danger', errorMsg)
  } finally {
    isSubmitting.value = false
  }
}

const isAdmissionOpen = (program) => {
  const sessions = Array.isArray(program?.admission_sessions) ? program.admission_sessions : []
  return sessions.some(session => session.admissions_open)
}

const openPrograms = computed(() => {
  return props.departments.flatMap((dept) =>
    (dept.programs || [])
      .filter(program => isAdmissionOpen(program))
      .map((program) => ({
        ...program,
        department_name: dept.name,
        department_id: dept.id
      }))
  )
})

const departmentsWithOpenPrograms = computed(() => {
  return props.departments.filter(dept => 
    (dept.programs || []).some(prog => isAdmissionOpen(prog))
  )
})

const getOpenProgramsByDept = (dept) => {
  return (dept.programs || []).filter(prog => isAdmissionOpen(prog))
}

const parseDate = (value) => {
  if (!value) return null
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric'
})

const formatDate = (value) => {
  const date = parseDate(value)
  return date ? dateFormatter.format(date) : 'TBA'
}

const getAdmissionSession = (program) => {
  const sessions = Array.isArray(program?.admission_sessions) ? program.admission_sessions : []
  return sessions.find(s => s.admissions_open)
}

const formatAdmissionWindow = (session) => {
  if (!session) return 'Dates to be announced'
  const startDate = session.admission_start_date
  const endDate = session.admission_end_date
  if (startDate && endDate) return `${formatDate(startDate)} - ${formatDate(endDate)}`
  return 'Dates to be announced'
}

const formatLevel = (level) => {
  if (!level) return 'Degree'
  const labels = {
    'bachelor': 'Bachelor (BS)',
    'master': 'Master (MS)',
    'phd': 'Doctorate (PhD)',
    'intermediate': 'Intermediate',
    'diploma': 'Diploma'
  }
  return labels[level.toLowerCase()] || level.charAt(0).toUpperCase() + level.slice(1)
}
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

