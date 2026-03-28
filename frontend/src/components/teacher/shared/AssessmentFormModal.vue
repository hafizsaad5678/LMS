<template>
  <BaseModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="isEditing ? 'Edit Assessment' : 'New Assessment'"
    @confirm="handleSubmit"
    :loading="loading"
    :confirm-text="isEditing ? 'Update' : 'Create'"
    size="lg"
  >
    <div class="p-2">
      <div class="row g-3">
        <div class="col-md-12">
          <BaseInput
            v-model="localForm.name"
            label="Assessment Name"
            placeholder="e.g., Midterm Exam, Quiz 1"
            required
          />
        </div>

        <div class="col-md-6">
          <label class="form-label fw-bold text-dark small">Subject/Class *</label>
          <select v-model="localForm.subject" class="form-select rounded-4 bg-light border-0 p-3" required>
            <option value="">Select Subject</option>
            <option v-for="subj in subjects" :key="subj.id" :value="subj.subject_id">
              {{ subj.subject_name }} ({{ subj.subject_code }})
            </option>
          </select>
        </div>

        <div class="col-md-6">
          <label class="form-label fw-bold text-dark small">Assessment Type *</label>
          <select v-model="localForm.component_type" class="form-select rounded-4 bg-light border-0 p-3" required>
            <option v-for="type in assessmentTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>

        <div class="col-md-6">
          <BaseInput
            v-model.number="localForm.max_marks"
            label="Maximum Marks"
            type="number"
            placeholder="100"
            min="1"
            required
          />
        </div>

        <div class="col-md-6">
          <BaseInput
            v-model.number="localForm.weightage"
            label="Weightage (%)"
            type="number"
            placeholder="20"
            min="0"
            max="100"
            required
          />
          <small class="text-muted">Percentage contribution to final grade</small>
        </div>

        <div class="col-md-12">
          <div class="form-check">
            <input 
              v-model="localForm.is_visible_to_students" 
              type="checkbox" 
              class="form-check-input" 
              id="visibility"
            >
            <label class="form-check-label fw-bold text-dark" for="visibility">
              Visible to Students
            </label>
            <div class="form-text">Students can see this assessment and their grades</div>
          </div>
        </div>

        <div class="col-md-12">
          <label class="form-label fw-bold text-dark small">Description (Optional)</label>
          <RichTextEditor 
            v-model="localForm.description" 
            placeholder="Add any notes or instructions..."
          />
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { BaseModal, BaseInput, RichTextEditor } from '@/components/shared/common'
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

watch(() => props.form, (newForm) => {
  localForm.value = { ...newForm }
}, { deep: true })

const handleSubmit = () => {
  emit('submit', localForm.value)
}
</script>
