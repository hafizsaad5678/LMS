<template>
  <BaseModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="isEditing ? 'Edit Announcement' : 'Create Announcement'"
    @confirm="handleSubmit"
    :loading="loading"
    :confirm-text="isEditing ? 'Update' : 'Create'"
    size="lg"
  >
    <div class="p-2">
      <div class="mb-3">
        <BaseInput
          v-model="localForm.title"
          label="Title"
          placeholder="e.g., Important: Class Cancelled Tomorrow"
          required
        />
      </div>

      <div class="mb-3">
        <label class="form-label fw-bold text-dark small">Subject/Class</label>
        <select v-model="localForm.subject" class="form-select rounded-4 bg-light border-0 p-3" required>
          <option value="">Select Subject</option>
          <option v-for="subj in subjects" :key="subj.id" :value="subj.subject_id">
            {{ subj.subject_name }} ({{ subj.subject_code }})
          </option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label fw-bold text-dark small">Priority Level</label>
        <select v-model="localForm.priority" class="form-select rounded-4 bg-light border-0 p-3">
          <option v-for="opt in priorityOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label fw-bold text-dark small">Message</label>
        <RichTextEditor 
          v-model="localForm.message" 
          placeholder="Write your announcement message here..."
          required
        />
      </div>

      <div class="form-check">
        <input 
          v-model="localForm.send_notification" 
          class="form-check-input" 
          type="checkbox" 
          id="sendNotification"
        >
        <label class="form-check-label" for="sendNotification">
          Send notification to students
        </label>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { BaseModal, BaseInput, RichTextEditor } from '@/components/shared/common'
import { ANNOUNCEMENT_PRIORITY_OPTIONS } from '@/utils/constants/options'

const props = defineProps({
  modelValue: Boolean,
  form: Object,
  subjects: Array,
  isEditing: Boolean,
  loading: Boolean,
  priorityOptions: { type: Array, default: () => ANNOUNCEMENT_PRIORITY_OPTIONS }
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
