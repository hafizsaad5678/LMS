<template>
  <AdminPageTemplate
    title="Create Academic Session"
    subtitle="Step-by-step wizard to create a new batch/intake"
    icon="bi bi-calendar-plus"
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

    <!-- Progress Steps -->
    <div class="wizard-progress mb-4">
      <div :class="['wizard-step', currentStep >= 1 && 'active', currentStep > 1 && 'completed']">
        <div class="step-number"><i v-if="currentStep > 1" class="bi bi-check"></i><span v-else>1</span></div>
        <div class="step-label">Select Program</div>
      </div>
      <div class="step-line" :class="currentStep > 1 && 'completed'"></div>
      <div :class="['wizard-step', currentStep >= 2 && 'active', currentStep > 2 && 'completed']">
        <div class="step-number"><i v-if="currentStep > 2" class="bi bi-check"></i><span v-else>2</span></div>
        <div class="step-label">Basic Info</div>
      </div>
      <div class="step-line" :class="currentStep > 2 && 'completed'"></div>
      <div :class="['wizard-step', currentStep >= 3 && 'active']">
        <div class="step-number">3</div>
        <div class="step-label">Review</div>
      </div>
    </div>

    <!-- Wizard Content -->
    <div class="card border-0 shadow-sm session-wizard-card">
      <div class="card-body p-4">
        <!-- Step 1: Select Program -->
        <div v-if="currentStep === 1" class="wizard-content">
          <h5 class="mb-4 fw-semibold"><i class="bi bi-mortarboard me-2 text-admin"></i>Select Program</h5>
          <div class="mb-3">
            <label class="form-label">Choose a program for this session <span class="text-danger">*</span></label>
            <select v-model="formData.program" class="form-select session-program-select" @change="onProgramChange">
              <option value="">-- Select Program --</option>
              <option v-for="program in programs" :key="program.id" :value="program.id">
                {{ program.name }} ({{ program.code }}) - {{ program.program_level_display || program.duration_years + ' Years' }}
              </option>
            </select>
          </div>
          <div v-if="selectedProgram" class="alert alert-info">
            <h6 class="fw-semibold"><i class="bi bi-info-circle me-2"></i>Program Details</h6>
            <div class="row mt-3">
              <div class="col-md-6">
                <p class="mb-2"><strong>Department:</strong> {{ selectedProgram.department_name || 'N/A' }}</p>
                <p class="mb-2"><strong>Duration:</strong> {{ selectedProgram.duration_years }} years</p>
              </div>
              <div class="col-md-6">
                <p class="mb-2"><strong>Default Semesters:</strong> {{ selectedProgram.duration_years ? selectedProgram.duration_years * 2 : (selectedProgram.default_semesters || 8) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Basic Info -->
        <div v-if="currentStep === 2" class="wizard-content">
          <h5 class="mb-4 fw-semibold"><i class="bi bi-info-circle me-2 text-admin"></i>Basic Information</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Session Name <span class="text-danger">*</span></label>
              <input v-model="formData.session_name" type="text" class="form-control" placeholder="e.g., BSCS 2023-2027" required>
            </div>
            <div class="col-md-6">
              <label class="form-label">Session Code <span class="text-danger">*</span></label>
              <input v-model="formData.session_code" type="text" class="form-control" placeholder="e.g., BSCS-2023" required>
            </div>
            <div class="col-md-4">
              <label class="form-label">Start Year <span class="text-danger">*</span></label>
              <input v-model.number="formData.start_year" type="number" class="form-control" min="2020" max="2030" required>
            </div>
            <div class="col-md-4">
              <label class="form-label">End Year</label>
              <input v-model.number="formData.end_year" type="number" class="form-control" :placeholder="suggestedEndYear" :min="formData.start_year">
              <small class="text-muted">Auto: {{ suggestedEndYear }}</small>
            </div>
            <div class="col-md-4">
              <label class="form-label">Total Capacity <span class="text-danger">*</span></label>
              <input v-model.number="formData.total_capacity" type="number" class="form-control" min="1" placeholder="60" required>
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.admission_start_date" type="date" label="Admission Start Date" />
              <small class="text-muted">When applications open</small>
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.admission_end_date" type="date" label="Admission End Date" />
              <small class="text-muted">When applications close</small>
            </div>
            <div class="col-12">
              <label class="form-label">Description</label>
              <textarea v-model="formData.description" class="form-control" rows="2" placeholder="Additional notes..."></textarea>
            </div>
          </div>
        </div>



        <!-- Step 3: Review -->
        <div v-if="currentStep === 3" class="wizard-content">
          <h5 class="mb-4 fw-semibold"><i class="bi bi-check-circle me-2 text-admin"></i>Review Session Details</h5>
          <div class="row g-4">
            <div class="col-md-6">
              <div class="card bg-light border-0">
                <div class="card-body">
                  <h6 class="text-admin fw-semibold mb-3">Program Information</h6>
                  <p class="mb-2"><strong>Program:</strong> {{ selectedProgram?.name }}</p>
                  <p class="mb-2"><strong>Department:</strong> {{ selectedProgram?.department_name || 'N/A' }}</p>
                  <p class="mb-0"><strong>Duration:</strong> {{ selectedProgram?.duration_years }} years</p>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card bg-light border-0">
                <div class="card-body">
                  <h6 class="text-admin fw-semibold mb-3">Session Information</h6>
                  <p class="mb-2"><strong>Name:</strong> {{ formData.session_name }}</p>
                  <p class="mb-2"><strong>Code:</strong> {{ formData.session_code }}</p>
                  <p class="mb-2"><strong>Duration:</strong> {{ formData.start_year }} - {{ formData.end_year || suggestedEndYear }}</p>
                  <p class="mb-0"><strong>Capacity:</strong> {{ formData.total_capacity }} students</p>
                  <p class="mt-2 mb-0"><strong>Admissions:</strong> {{ formData.admission_start_date || 'Not set' }} - {{ formData.admission_end_date || 'Not set' }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="alert alert-warning mt-4">
            <div class="form-check">
              <input v-model="autoSetupSemesters" type="checkbox" class="form-check-input" id="autoSetup">
              <label class="form-check-label" for="autoSetup">
                <strong>Automatically create semesters</strong> after session creation
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Wizard Footer -->
      <div class="card-footer bg-white d-flex justify-content-between py-3">
        <button v-if="currentStep > 1" @click="previousStep" class="btn btn-admin-outline">
          <i class="bi bi-arrow-left me-2"></i>Previous
        </button>
        <div v-else></div>
        <div class="d-flex gap-2">
          <router-link :to="ADMIN_ROUTES.SESSION_LIST.path" class="btn btn-outline-secondary">Cancel</router-link>
          <button v-if="currentStep < 3" @click="nextStep" class="btn btn-admin-primary" :disabled="!canProceed">
            Next<i class="bi bi-arrow-right ms-2"></i>
          </button>
          <button v-else @click="createSession" class="btn btn-admin-primary" :disabled="saving">
            <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Creating...</span>
            <span v-else><i class="bi bi-check-circle me-2"></i>Create Session</span>
          </button>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, BaseInput } from '@/components/shared/common'
import { sessionService, programService, cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Sessions', href: ADMIN_ROUTES.SESSION_LIST.path },
  { name: 'Create Session' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.SESSION_LIST.name }) }
]

const currentStep = ref(1)
const programs = ref([])
const saving = ref(false)
const autoSetupSemesters = ref(true)
const { alert, showAlert } = useAlert()

const formData = ref({
  program: '',
  session_name: '',
  session_code: '',
  start_year: new Date().getFullYear(),
  end_year: null,
  total_capacity: 60,
  status: 'upcoming',
  description: '',
  admission_start_date: null,
  admission_end_date: null
})

const selectedProgram = computed(() => programs.value.find(p => p.id === formData.value.program))
const suggestedEndYear = computed(() => {
  if (selectedProgram.value && formData.value.start_year) {
    return formData.value.start_year + selectedProgram.value.duration_years
  }
  return formData.value.start_year + 4
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1: return !!formData.value.program
    case 2: return formData.value.session_name && formData.value.session_code && formData.value.start_year && formData.value.total_capacity > 0
    default: return true
  }
})

const normalizeToArray = (payload) => {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload?.data)) return payload.data
  return []
}

const extractApiErrorMessage = (error) => {
  const data = error?.response?.data
  if (!data) return 'Failed to create session'

  if (typeof data === 'string') return data
  if (typeof data?.error === 'string') return data.error

  const firstKey = Object.keys(data)[0]
  if (!firstKey) return 'Failed to create session'

  const firstValue = data[firstKey]
  if (Array.isArray(firstValue) && firstValue.length > 0) return firstValue[0]
  if (typeof firstValue === 'string') return firstValue

  return 'Failed to create session'
}


const loadPrograms = async () => {
  try {
    // Check cache first
    const cached = cacheService.get('programs_list')
    if (cached) {
      programs.value = (Array.isArray(cached) ? cached : []).filter(p => p?.is_active !== false)
      return
    }
    
    const data = await programService.getAllPrograms()
    const result = (Array.isArray(data) ? data : (data.results || [])).filter(p => p?.is_active !== false)
    
    // Store in cache
    cacheService.set('programs_list', result)
    programs.value = result
  } catch (error) {
    console.error('Error loading programs:', error)
    showAlert('error', 'Failed to load programs', 'Error!')
  }
}

const onProgramChange = async () => {
  if (selectedProgram.value) {
    const code = selectedProgram.value.code
    
    // Check for existing sessions to determine next start year
    try {
      const res = await sessionService.getSessionsByProgram(selectedProgram.value.id)
      const sessions = normalizeToArray(res)
      
      if (sessions.length > 0) {
        // Find latest session by start year
        // We want to sort descending by start_year
        sessions.sort((a, b) => b.start_year - a.start_year)
        const latestSession = sessions[0]
        
        // Suggest next start year based on latest session's end year (as per user request: 2020-2022 -> 2022-2024)
        if (latestSession.end_year) {
          formData.value.start_year = latestSession.end_year
        } else {
             formData.value.start_year = latestSession.start_year + selectedProgram.value.duration_years
        }
        
        // Add a warning if we are just suggesting
        showAlert('info', `Suggested start year based on previous session (${latestSession.session_name})`, 'Smart Suggestion')
      } else {
         // No sessions, default to current year
         formData.value.start_year = new Date().getFullYear()
      }
    } catch (e) {
      console.error('Error checking program sessions:', e)
    }

    const year = formData.value.start_year
    formData.value.session_code = `${code}-${year}`
    formData.value.session_name = `${selectedProgram.value.name} ${year}-${suggestedEndYear.value}`
  }
}

// Watch for start_year changes to update code/name and validate
import { watch } from 'vue'
watch(() => formData.value.start_year, async (newYear) => {
    if (selectedProgram.value) {
        const code = selectedProgram.value.code
        formData.value.session_code = `${code}-${newYear}`
        formData.value.session_name = `${selectedProgram.value.name} ${newYear}-${suggestedEndYear.value}`
        
        // Validation: check if a session with this Start Year already exists
        try {
             const res = await sessionService.getSessionsByProgram(selectedProgram.value.id)
           const existing = normalizeToArray(res).find(s => Number(s.start_year) === Number(newYear))
             if (existing) {
                 showAlert('warning', `A session starting in ${newYear} already exists: ${existing.session_name}`, 'Duplicate Year Warning')
             }
        } catch(e) {}
    }
})

const nextStep = () => { if (canProceed.value && currentStep.value < 3) currentStep.value++ }
const previousStep = () => { if (currentStep.value > 1) currentStep.value-- }

const createSession = async () => {
  if (!formData.value.program) {
    showAlert('error', 'Course/Program missing.', 'Error!')
    return
  }

  saving.value = true
  try {
    const existingRes = await sessionService.getSessionsByProgram(formData.value.program)
    const existingSessions = normalizeToArray(existingRes)
    const duplicateSession = existingSessions.find((s) => {
      const sameCode = String(s.session_code || '').trim().toLowerCase() === String(formData.value.session_code || '').trim().toLowerCase()
      const sameStartYear = Number(s.start_year) === Number(formData.value.start_year)
      return sameCode || sameStartYear
    })

    if (duplicateSession) {
      const message = duplicateSession.session_code?.toLowerCase() === String(formData.value.session_code || '').trim().toLowerCase()
        ? `Session code already exists: ${duplicateSession.session_code}`
        : `A session starting in ${formData.value.start_year} already exists: ${duplicateSession.session_name}`
      showAlert('error', message, 'Duplicate Session')
      return
    }

    if (!formData.value.end_year) formData.value.end_year = suggestedEndYear.value
    const response = await sessionService.createSession(formData.value)
    const sessionId = response?.id
    
    // Clear caches to update list view
    cacheService.clear('sessions_list')
    cacheService.clearPattern('session')
    
    showAlert('success', 'Session created successfully!', 'Success!')
    
    if (autoSetupSemesters.value && response?.status === 'active') {
      try {
        await sessionService.setupSemesters(sessionId)
      } catch (error) {
        console.error('Error setting up semesters:', error)
      }
    } else if (autoSetupSemesters.value && response?.status !== 'active') {
      showAlert('info', 'Semesters were not generated. Activate the session first, then run Setup Semesters.', 'Session Created')
    }
    setTimeout(() => router.push({ name: ADMIN_ROUTES.SESSION_LIST.name, query: { refresh: Date.now() } }), 1500)
  } catch (error) {
    console.error('Error creating session:', error)
    showAlert('error', extractApiErrorMessage(error), 'Error!')
  } finally {
    saving.value = false
  }
}

onMounted(loadPrograms)
</script>


