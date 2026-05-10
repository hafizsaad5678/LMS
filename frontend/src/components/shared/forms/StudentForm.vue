<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
      <h5 class="card-title mb-0 fw-semibold">
        <i class="bi bi-person-badge me-2 text-admin"></i>
        Student Information
      </h5>
    </div>
    <div class="card-body p-4">
      <!-- Read-only Info (Edit Mode Only) -->
      <div v-if="isEditMode && enrollmentNumber" class="mb-4 p-3 bg-light rounded">
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

      <form @submit.prevent="$emit('submit')">
        <!-- Personal Information -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-person me-2"></i>Personal Information
          </h6>
          <div class="row g-3">
            <div class="col-md-6">
              <BaseInput v-model="formData.full_name" label="Full Name" type="text" placeholder="Enter full name"
                :required="true" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.email" label="Email" type="email" placeholder="student@college.edu"
                :required="true" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.phone" label="Phone Number" type="tel" placeholder="+92 300-1234567" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.date_of_birth" label="Date of Birth" type="date" />
            </div>
            <div class="col-md-6">
              <SelectInput v-model="formData.gender" label="Gender" :options="GENDER_OPTIONS"
                placeholder="Select Gender" :required="true" />
            </div>
            <div class="col-md-6">
              <SelectInput v-model="formData.blood_group" label="Blood Group" :options="BLOOD_GROUP_OPTIONS"
                placeholder="Select Blood Group" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="cnicModel" label="CNIC" type="text" placeholder="12345-1234567-1" />
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
                <label class="form-label">Department <span class="text-danger">*</span></label>
                <select v-model="selectedDepartment" class="form-select" required @change="onDepartmentChange">
                  <option value="">Select Department</option>
                  <option v-for="dept in departments" :key="dept.id" :value="String(dept.id)">
                    {{ dept.name }} ({{ dept.code }})
                  </option>
                </select>
                <small class="text-muted">Step 1: First select the department</small>
              </div>
            </div>

            <!-- Program/Course Selection -->
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Course/Program <span class="text-danger">*</span></label>
                <select v-model="formData.program" class="form-select" required :disabled="!selectedDepartment"
                  @change="onProgramChange">
                  <option value="">{{ !selectedDepartment ? 'Select Department First' : 'Select Course' }}</option>
                  <option v-for="prog in filteredPrograms" :key="prog.id" :value="String(prog.id)">
                    {{ prog.name }} ({{ prog.code }})
                  </option>
                </select>
                <small class="text-muted">Step 2: Select course like BSCS, BBA</small>
              </div>
            </div>

            <div class="col-md-3">
              <BaseInput v-model.number="formData.enrollment_year" label="Enrollment Year" type="number"
                placeholder="Auto from session" :required="true" :disabled="!formData.session || loadingSessionSemester" />
            </div>
            <div class="col-md-3">
              <div class="mb-3">
                <label class="form-label">Current Semester <span class="text-danger">*</span></label>
                <select v-model="activeSemesterId" class="form-select"
                  :disabled="!formData.session || loadingSessionSemester || !sessionSemesters.length"
                  required>
                  <option value="">{{ loadingSessionSemester ? 'Loading...' : 'Select Semester' }}</option>
                  <option v-for="sem in sessionSemesters" :key="sem.id" :value="String(sem.id)">
                    {{ sem.name }} {{ sem.status === 'active' ? '✓ Active' : '' }}
                  </option>
                </select>
                <small class="text-muted">Step 4: Auto-selects active semester</small>
              </div>
            </div>

            <!-- Session/Batch Selection -->
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Session/Batch <span class="text-danger">*</span></label>
                <select v-model="formData.session" class="form-select" :disabled="!formData.program" required
                  @change="onSessionChange">
                  <option value="">Select Session</option>
                  <option v-for="sess in filteredSessions" :key="sess.id" :value="String(sess.id)">
                    {{ sess.session_name }} ({{ sess.start_year }}-{{ sess.end_year }})
                  </option>
                </select>
                <small class="text-muted">Step 3: Select academic session/batch</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Subject Enrollment -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-book me-2"></i>Subject Enrollment
          </h6>
          <div v-if="loadingSubjects || loadingSessionSemester" class="text-muted">
            <span class="spinner-border spinner-border-sm me-2"></span>Loading subjects...
          </div>
          <div v-else-if="!formData.program || !formData.session" class="alert alert-secondary">
            <i class="bi bi-info-circle me-2"></i>
            <span v-if="!formData.program">Select a department and course first.</span>
            <span v-else>Select a session/batch to load subjects.</span>
          </div>
          <div v-else-if="availableSubjects.length === 0" class="alert alert-warning">
            <i class="bi bi-exclamation-triangle me-2"></i>
            No subjects found for Semester {{ formData.current_semester || '?' }} of this session.
          </div>
          <div v-else class="subjects-grid">
            <div v-for="subject in availableSubjects" :key="subject.id" class="form-check subject-item">
              <input class="form-check-input" type="checkbox" :id="'subject-' + subject.id" :value="subject.id"
                v-model="formData.enrolled_subjects">
              <label class="form-check-label" :for="'subject-' + subject.id">
                <span class="badge bg-dark me-2">{{ subject.code }}</span>
                {{ subject.name }}
                <small v-if="subject.credit_hours" class="text-muted ms-2">({{ subject.credit_hours }} Cr)</small>
              </label>
            </div>
          </div>
          <small class="text-muted mt-2 d-block">Selected: {{ formData.enrolled_subjects.length }} subject(s)</small>
        </div>

        <!-- Guardian & Address -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-people me-2"></i>Guardian & Address
          </h6>
          <div class="row g-3">
            <div class="col-md-6">
              <BaseInput v-model="formData.father_name" label="Father's Name" type="text" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.guardian_phone" label="Guardian Phone" type="tel" />
            </div>
            <div class="col-12">
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea v-model="formData.address" class="form-control" rows="2"
                  placeholder="Enter address"></textarea>
              </div>
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.city" label="City" type="text" placeholder="e.g., Karachi" />
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="d-flex gap-3 justify-content-end pt-3 border-top">
          <button type="button" @click="$emit('cancel')" class="btn btn-admin-outline px-4" :disabled="submitting">
            <i class="bi bi-x-circle me-2"></i>Cancel
          </button>
          <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
            <span v-if="submitting">
              <span class="spinner-border spinner-border-sm me-2"></span>
              {{ isEditMode ? 'Updating...' : 'Adding Student...' }}
            </span>
            <span v-else>
              <i class="bi bi-check-circle me-2"></i>
              {{ isEditMode ? 'Update Student' : 'Add Student' }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { BaseInput, SelectInput } from '@/components/shared/common'
import { 
  useCascadingDropdowns, 
  useFormFormatting, 
  useAcademicSync 
} from '@/composables/shared'
import { GENDER_OPTIONS, BLOOD_GROUP_OPTIONS } from '@/utils/constants/options'
import { api, normalizeToArray } from '@/services/shared'

const props = defineProps({
  modelValue: { type: Object, required: true },
  isEditMode: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
  enrollmentNumber: { type: String, default: '' },
  currentDepartmentName: { type: String, default: '' },
  currentProgramName: { type: String, default: '' },
  initialDepartment: { type: [String, Number], default: '' }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

// Local form data that syncs with v-model
const formData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Use shared composables for formatting and dropdowns
const { cnicModel } = useFormFormatting(formData)
const {
  departments,
  programs,
  sessions,
  filteredPrograms,
  selectedDepartment,
  loadDepartments,
  loadPrograms,
  loadSessions,
  onDepartmentChange: handleDepartmentChange,
  onProgramChange: handleProgramChange
} = useCascadingDropdowns()

// Filter sessions by selected program
const filteredSessions = computed(() => {
  if (!formData.value.program) return []
  return sessions.value.filter(s =>
    !s.program || String(s.program) === String(formData.value.program)
  )
})

// Subjects state
const availableSubjects = ref([])
const loadingSubjects = ref(false)

// Use shared composable for academic sync
const {
  activeSemesterId,
  sessionSemesters,
  loadingSessionSemester,
  syncAcademicFieldsFromSession
} = useAcademicSync(formData, sessions)

// Fetch subjects for a given semester ID
const loadSubjectsBySemester = async (semesterId) => {
  if (!semesterId) {
    availableSubjects.value = []
    return
  }
  loadingSubjects.value = true
  try {
    const response = await api.get(`/semesters/${semesterId}/subjects/`)
    availableSubjects.value = normalizeToArray(response)
  } catch (error) {
    console.error('Error loading subjects:', error)
    availableSubjects.value = []
  } finally {
    loadingSubjects.value = false
  }
}

// Wrap academic sync with subject loading
const handleSessionSync = async (sessionId) => {
  const currentIdBefore = activeSemesterId.value
  const target = await syncAcademicFieldsFromSession(sessionId)
  
  if (target) {
    // Force reload if ID hasn't changed (to ensure subjects list refreshes)
    if (activeSemesterId.value === currentIdBefore) {
      await loadSubjectsBySemester(activeSemesterId.value)
    }
  }
}

// Watch semester selection — fetch subjects whenever it changes
watch(activeSemesterId, async (newId) => {
  if (!newId) {
    availableSubjects.value = []
    return
  }
  const sem = sessionSemesters.value.find(s => String(s.id) === newId)
  if (sem) {
    formData.value.current_semester = parseInt(sem.number) || 1
    if (!props.isEditMode) {
      formData.value.enrolled_subjects = []
    }
    await loadSubjectsBySemester(sem.id)
  }
})

// Cascading event handlers
const onDepartmentChange = () => {
  handleDepartmentChange(selectedDepartment.value)
  formData.value.program = ''
  formData.value.session = ''
  formData.value.current_semester = ''
  formData.value.enrollment_year = new Date().getFullYear()
  formData.value.enrolled_subjects = []
  activeSemesterId.value = ''
  availableSubjects.value = []
  sessionSemesters.value = []
}

const onProgramChange = async () => {
  formData.value.session = ''
  formData.value.current_semester = ''
  formData.value.enrollment_year = new Date().getFullYear()
  formData.value.enrolled_subjects = []
  activeSemesterId.value = ''
  sessionSemesters.value = []
  availableSubjects.value = []
  if (formData.value.program) {
    await handleProgramChange(formData.value.program)
  }
}

const onSessionChange = async () => {
  formData.value.enrolled_subjects = []
  if (formData.value.session) {
    await handleSessionSync(formData.value.session)
  } else {
    formData.value.enrollment_year = new Date().getFullYear()
    formData.value.current_semester = ''
    activeSemesterId.value = ''
    availableSubjects.value = []
    sessionSemesters.value = []
  }
}

// Initialize and handles edit mode state
onMounted(async () => {
  await Promise.all([loadDepartments(), loadPrograms(), loadSessions()])

  if (props.isEditMode && formData.value.program) {
    const prog = programs.value.find(p => String(p.id) === String(formData.value.program))
    if (prog?.department) {
      selectedDepartment.value = String(prog.department)
    }
  }

  if (formData.value.session) {
    await handleSessionSync(formData.value.session)
  }
})

// Watchers for edit mode synchronization
watch(() => props.initialDepartment, (newVal) => { if (newVal) selectedDepartment.value = newVal })
watch(() => formData.value.program, async (newVal) => {
  if (newVal && props.isEditMode && formData.value.session) {
    await handleSessionSync(formData.value.session)
  }
})
</script>
