<template>
  <BaseModal 
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)" 
    :title="isEditing ? 'Edit Exam' : 'Schedule New Exam'" 
    size="lg"
    @confirm="handleSubmit"
    :loading="loading"
    :confirm-text="isEditing ? 'Update' : 'Schedule Exam'"
    confirm-variant="btn-teacher-primary"
  >
    <div class="row g-3">
      <div class="col-md-12">
        <label class="form-label fw-semibold">Subject *</label>
        <select v-model="localForm.subject" class="form-select" required>
          <option value="">Select subject...</option>
          <option v-for="subject in subjects" :key="subject.subject_id" :value="subject.subject_id">
            {{ subject.subject_name }} ({{ subject.subject_code }})
          </option>
        </select>
      </div>

      <div class="col-md-6">
        <label class="form-label fw-semibold">Exam Type *</label>
        <select v-model="localForm.exam_type" class="form-select" required>
          <option v-for="opt in examTypes" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>

      <div class="col-md-6">
        <label class="form-label fw-semibold">Phase (Optional)</label>
        <input 
          v-model="localForm.phase" 
          type="text" 
          class="form-control" 
          placeholder="e.g., Spring 2024"
        >
      </div>

      <div class="col-md-6">
        <BaseInput 
          v-model="localForm.exam_date" 
          label="Exam Date *" 
          type="date" 
          required
        />
      </div>

      <div class="col-md-6">
        <BaseInput 
          v-model="localForm.exam_time" 
          label="Start Time *" 
          type="time" 
          required
        />
      </div>

      <div class="col-md-6">
        <label class="form-label fw-semibold">Duration (Minutes) *</label>
        <input 
          v-model="localForm.duration_minutes" 
          type="number" 
          class="form-control" 
          placeholder="e.g., 120"
          required
        >
      </div>

      <div class="col-md-6">
        <label class="form-label fw-semibold">Venue/Room</label>
        <input 
          v-model="localForm.room" 
          type="text" 
          class="form-control" 
          placeholder="e.g., Room 101"
        >
      </div>

      <div class="col-md-6">
        <label class="form-label fw-semibold">Total Marks *</label>
        <input 
          v-model="localForm.total_marks" 
          type="number" 
          step="0.01" 
          class="form-control" 
          required
        >
      </div>

      <div class="col-md-6">
        <label class="form-label fw-semibold">Status</label>
        <select v-model="localForm.status" class="form-select">
          <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>

      <div class="col-12">
        <label class="form-label fw-semibold">Instructions</label>
        <RichTextEditor
          v-model="localForm.instructions"
          placeholder="Enter any special instructions for the exam..."
        />
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { BaseModal, BaseInput, RichTextEditor } from '@/components/shared/common'
import { EXAM_TYPE_OPTIONS, SCHEDULE_STATUS_OPTIONS } from '@/utils/constants/options'

const props = defineProps({
  modelValue: Boolean,
  form: Object,
  subjects: Array,
  isEditing: Boolean,
  loading: Boolean,
  examTypes: { type: Array, default: () => EXAM_TYPE_OPTIONS },
  statusOptions: { type: Array, default: () => SCHEDULE_STATUS_OPTIONS }
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
