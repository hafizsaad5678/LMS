<template>
  <BaseModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="isEditing ? 'Edit Assessment' : 'New Assessment'"
    @confirm="handleSubmit"
    :loading="loading"
    :confirm-text="isEditing ? 'Update' : 'Create'"
    size="md"
  >
    <div class="px-3 pb-2 mt-n2">
      <div class="row g-2">
        <!-- Optional Link Dropdown -->
        <div v-if="!isEditing" class="col-md-12">
          <div class="mb-2 p-2 rounded-3" style="background-color: #f8fbff; border: 1px dashed #cfe2ff;">
            <label class="form-label fw-bold text-primary extra-small-label mb-1">
              <i class="bi bi-link-45deg me-1"></i>LINK WITH EXISTING ASSIGNMENT (OPTIONAL)
            </label>
            <select 
              v-model="linkedAssignmentId" 
              @change="handleAssignmentLink" 
              class="form-select form-select-sm rounded-3 border-0 shadow-none bg-white font-monospace small"
            >
              <option :value="null">-- Select to Autofill --</option>
              <option v-for="asgn in assignments" :key="asgn.id" :value="asgn.id">
                {{ asgn.title }} ({{ asgn.total_marks }} Marks)
              </option>
            </select>
          </div>
        </div>

        <div class="col-md-12">
          <div class="mb-2">
            <label class="form-label fw-bold text-dark extra-small-label mb-1">ASSESSMENT NAME *</label>
            <input v-model="localForm.name" type="text" class="form-control form-control-sm rounded-3 bg-light border-0 shadow-none border-focus" placeholder="e.g., Midterm Exam">
          </div>
        </div>

        <div class="col-md-6">
          <div class="mb-2">
            <label class="form-label fw-bold text-dark extra-small-label mb-1">SUBJECT/CLASS *</label>
            <select v-model="localForm.subject" class="form-select form-select-sm rounded-3 bg-light border-0 shadow-none" required>
              <option value="">Select Subject</option>
              <option v-for="subj in subjects" :key="subj.id" :value="subj.subject_id || subj.id">
                {{ subj.subject_name || subj.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="col-md-6">
          <div class="mb-2">
            <label class="form-label fw-bold text-dark extra-small-label mb-1">TYPE *</label>
            <select v-model="localForm.component_type" class="form-select form-select-sm rounded-3 bg-light border-0 shadow-none" required>
              <option v-for="type in assessmentTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="col-md-6">
          <div class="mb-2">
            <label class="form-label fw-bold text-dark extra-small-label mb-1">MAX MARKS *</label>
            <input v-model.number="localForm.max_marks" type="number" class="form-control form-control-sm rounded-3 bg-light border-0 shadow-none" placeholder="100" min="1">
          </div>
        </div>

        <div class="col-md-6">
          <div class="mb-2">
            <label class="form-label fw-bold text-dark extra-small-label mb-1">WEIGHTAGE (%) *</label>
            <input v-model.number="localForm.weightage" type="number" class="form-control form-control-sm rounded-3 bg-light border-0 shadow-none" placeholder="20" min="0" max="100">
          </div>
        </div>

        <div class="col-md-12">
          <div class="form-check small mb-1">
            <input 
              v-model="localForm.is_visible_to_students" 
              type="checkbox" 
              class="form-check-input shadow-none" 
              id="visibility"
            >
            <label class="form-check-label fw-bold text-dark" for="visibility">
              Visible to Students
            </label>
          </div>
        </div>

        <div class="col-md-12">
          <label class="form-label fw-bold text-dark extra-small-label mb-1">DESCRIPTION (OPTIONAL)</label>
          <RichTextEditor 
            v-model="localForm.description" 
            placeholder="Notes..."
            height="100px"
          />
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
.border-focus:focus {
  background-color: #fff !important;
  border: 1px solid var(--teacher-primary) !important;
}
</style>

<script setup>
import { ref, watch } from 'vue'
import { BaseModal, RichTextEditor } from '@/components/shared/common'
import { ASSESSMENT_TYPES } from '@/utils/constants/options'

const props = defineProps({
  modelValue: Boolean,
  form: Object,
  subjects: Array,
  isEditing: Boolean,
  loading: Boolean,
  assessmentTypes: { type: Array, default: () => ASSESSMENT_TYPES }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const localForm = ref({ ...props.form })
const assignments = ref([])
const linkedAssignmentId = ref(null)

import teacherPanelService from '@/services/teacher/teacherPanelService'

const loadAssignments = async () => {
    try {
        const res = await teacherPanelService.getMyAssignments()
        assignments.value = (res.results || res || []).filter(a => !a.is_graded)
    } catch (e) {
        console.error('Failed to load assignments:', e)
    }
}

watch(() => props.modelValue, (isOpen) => {
    if (isOpen && !props.isEditing) {
        loadAssignments()
        linkedAssignmentId.value = null
    }
})

const handleAssignmentLink = () => {
    const selected = assignments.value.find(a => a.id === linkedAssignmentId.value)
    if (selected) {
        localForm.value.name = selected.title
        localForm.value.subject = selected.subject
        localForm.value.max_marks = selected.total_marks || 100
        localForm.value.component_type = 'assignment'
        localForm.value.assignment_id = selected.id // Pass this to backend
    } else {
        // Reset if unselected
        localForm.value.name = ''
        localForm.value.max_marks = 100
        localForm.value.assignment_id = null
    }
}

watch(() => props.form, (newForm) => {
  localForm.value = { ...newForm }
}, { deep: true })

const handleSubmit = () => {
  emit('submit', localForm.value)
}
</script>
