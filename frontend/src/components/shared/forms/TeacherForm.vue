<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
      <h5 class="card-title mb-0 fw-semibold">
        <i class="bi bi-person-workspace me-2 text-admin"></i>
        Teacher Information
      </h5>
    </div>
    <div class="card-body p-4">
      <!-- Read-only Info (Edit Mode Only) -->
      <div v-if="isEditMode && employeeId" class="mb-4 p-3 bg-light rounded">
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
              <BaseInput v-model="formData.email" label="Email" type="email" placeholder="teacher@college.edu"
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
              <BaseInput v-model="cnicModel" label="CNIC" type="text" placeholder="12345-1234567-1" />
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
                <label class="form-label">Department <span class="text-danger">*</span></label>
                <select v-model="formData.department" class="form-select" required>
                  <option value="">Select Department</option>
                  <option v-for="dept in departments" :key="dept.id" :value="String(dept.id)">
                    {{ dept.name }} ({{ dept.code }})
                  </option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <SelectInput v-model="formData.designation" label="Designation" :options="DESIGNATION_OPTIONS"
                placeholder="Select Designation" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.qualification" label="Qualification" type="text"
                placeholder="e.g., PhD Computer Science" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.specialization" label="Specialization" type="text"
                placeholder="e.g., Machine Learning" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.joining_date" label="Joining Date" type="date" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model.number="formData.experience_years" label="Years of Experience" type="number"
                placeholder="5" />
            </div>
          </div>
        </div>

        <!-- Teaching Subjects -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-book me-2"></i>Teaching Subjects
          </h6>
          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label">Course/Program</label>
              <select v-model="selectedProgramForSubjects" class="form-select" :disabled="loadingPrograms">
                <option value="">{{ loadingPrograms ? 'Loading...' : 'Select Course to Add Subjects' }}</option>
                <option v-for="prog in programs" :key="prog.id" :value="String(prog.id)">
                  {{ prog.name }} ({{ prog.code }})
                </option>
              </select>
              <small class="text-muted">Filter subjects by any course in the institution</small>
            </div>
          </div>
          <div v-if="!selectedProgramForSubjects" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>Select a course to view subjects.
          </div>
          <div v-if="loadingSubjects" class="text-muted">
            <span class="spinner-border spinner-border-sm me-2"></span>Loading subjects...
          </div>
          <div v-else-if="selectedProgramForSubjects && subjects.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>No subjects available.
          </div>
          <div v-else-if="selectedProgramForSubjects" class="subjects-grid p-3 border rounded mb-3 bg-light-subtle">
            <div v-for="subject in subjects" :key="subject.id" class="form-check subject-item">
              <input class="form-check-input" type="checkbox" :id="'teacher-subject-' + subject.id" :value="subject.id"
                v-model="formData.teaching_subjects" @change="onSubjectToggle(subject)">
              <label class="form-check-label" :for="'teacher-subject-' + subject.id">
                <span class="badge bg-dark me-2">{{ subject.code }}</span>
                {{ subject.name }}
                <small v-if="subject.credit_hours" class="text-muted ms-2">({{ subject.credit_hours }} Cr)</small>
              </label>
            </div>
          </div>

          <!-- Selected Subjects Summary -->
          <div v-if="formData.teaching_subjects.length > 0" class="selected-subjects-section mt-3">
            <label class="form-label fw-semibold small text-muted text-uppercase mb-2">Currently Selected ({{ formData.teaching_subjects.length }})</label>
            <div class="d-flex flex-wrap gap-2">
              <div v-for="id in formData.teaching_subjects" :key="id" class="badge bg-dark text-white border border-secondary p-2 d-flex align-items-center gap-2">
                <span>{{ getSubjectDisplayName(id) }}</span>
                <i class="bi bi-x-circle cursor-pointer text-danger-emphasis ms-1" @click="removeSubject(id)"></i>
              </div>
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
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea v-model="formData.address" class="form-control" rows="2"
                  placeholder="Enter full address"></textarea>
              </div>
            </div>
            <div class="col-md-6">
              <BaseInput v-model="formData.city" label="City" type="text" placeholder="e.g., Karachi" />
            </div>
          </div>
        </div>
 <!-- Profile Image -->
        <div class="mb-4 text-center">
          <ImageUpload 
            v-model="formData.profile_image" 
            label="Profile Picture" 
            :existing-image-url="typeof formData.profile_image === 'string' ? getFileUrl(formData.profile_image) : ''"
          />
        </div>
        <!-- Form Actions -->
        <div class="d-flex gap-3 justify-content-end pt-3 border-top">
          <button type="button" @click="$emit('cancel')" class="btn btn-admin-outline px-4" :disabled="submitting">
            <i class="bi bi-x-circle me-2"></i>Cancel
          </button>
          <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
            <span v-if="submitting">
              <span class="spinner-border spinner-border-sm me-2"></span>
              {{ isEditMode ? 'Updating...' : 'Adding Teacher...' }}
            </span>
            <span v-else>
              <i class="bi bi-check-circle me-2"></i>
              {{ isEditMode ? 'Update Teacher' : 'Add Teacher' }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch, reactive } from 'vue'
import { BaseInput, SelectInput, ImageUpload } from '@/components/shared/common'
import { getFileUrl } from '@/utils/constants/config'
import { 
  useCascadingDropdowns, 
  useFormFormatting 
} from '@/composables/shared'
import { GENDER_OPTIONS, DESIGNATION_OPTIONS } from '@/utils/constants/options'
import { api, normalizeToArray } from '@/services/shared'

const props = defineProps({
  modelValue: { type: Object, required: true },
  isEditMode: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
  employeeId: { type: String, default: '' },
  currentDepartmentName: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

// Local form data that syncs with v-model
const formData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Use shared composables
const { cnicModel } = useFormFormatting(formData)
const {
  departments,
  programs,
  loadingDepartments,
  loadingPrograms,
  loadDepartments,
  loadPrograms
} = useCascadingDropdowns()

// Load subjects separately (not part of cascading dropdowns)
const subjects = ref([])
const loadingSubjects = ref(false)
const selectedProgramForSubjects = ref('')

// Keep track of subject details for the selected list display
const subjectDetailsMap = reactive({})

const onSubjectToggle = (subject) => {
  if (subject && subject.id) {
    subjectDetailsMap[subject.id] = subject
  }
}

const getSubjectDisplayName = (id) => {
  const s = subjectDetailsMap[id]
  return s ? `${s.code} - ${s.name}` : `Subject ${id}`
}

const removeSubject = (id) => {
  formData.value.teaching_subjects = formData.value.teaching_subjects.filter(sid => sid !== id)
}

const loadSubjects = async (programId) => {
  if (!programId) {
    subjects.value = []
    return
  }
  loadingSubjects.value = true
  try {
    const response = await api.get('/subjects/', { 
      params: { 
        'semester__program': programId,
        'semester__status': 'active'
      } 
    })
    const data = normalizeToArray(response.data)
    subjects.value = data
    
    // Cache subject details
    data.forEach(s => {
      subjectDetailsMap[s.id] = s
    })
  } catch (error) {
    console.error('Error loading subjects:', error)
    subjects.value = []
  } finally {
    loadingSubjects.value = false
  }
}

// Only clear if the department itself changes significantly, but user wants to KEEP subjects
watch(() => formData.value.department, () => {
  selectedProgramForSubjects.value = ''
  subjects.value = []
})

watch(() => selectedProgramForSubjects.value, async (programId) => {
  if (programId) {
    await loadSubjects(programId)
  }
})

onMounted(async () => {
  await Promise.all([loadDepartments(), loadPrograms()])
  
  // If editing, pre-populate subjectDetailsMap for currently assigned subjects
  if (props.isEditMode && formData.value.teaching_subjects?.length > 0) {
    try {
      // Fetch details for all currently selected subjects so names/codes show up immediately
      const ids = formData.value.teaching_subjects
        .map(s => typeof s === 'object' ? s.id : s)
        .filter(id => !!id)
      
      if (ids.length > 0) {
        // We can fetch them one by one or use a filter if supported
        // For simplicity and correctness across legacy/new data, fetch in bulk if possible
        const response = await api.get('/subjects/', { params: { id__in: ids.join(',') } })
        const data = normalizeToArray(response.data)
        data.forEach(s => {
          subjectDetailsMap[s.id] = s
        })
      }
      
      // Ensure formData.teaching_subjects only contains IDs for the form logic
      formData.value.teaching_subjects = formData.value.teaching_subjects.map(s => typeof s === 'object' ? s.id : s)
    } catch (error) {
      console.error('Error pre-loading subject details:', error)
    }
  }
})
</script>
