<template>
  <BaseModal v-model="isOpen" title="Confirm Submission" variant="student" size="md">
    <div class="quiz-summary-grid">
      <div class="summary-item">
        <span>Total Questions</span>
        <strong>{{ summary.total_questions }}</strong>
      </div>
      <div class="summary-item">
        <span>Answered</span>
        <strong>{{ summary.answered }}</strong>
      </div>
      <div class="summary-item">
        <span>Not Answered</span>
        <strong>{{ summary.not_answered }}</strong>
      </div>
      <div class="summary-item">
        <span>Flagged</span>
        <strong>{{ summary.flagged }}</strong>
      </div>
    </div>

    <p class="text-muted small mt-3 mb-0">
      Once submitted, this quiz is locked and cannot be changed.
    </p>

    <template #footer>
      <button type="button" class="btn btn-outline-secondary" @click="isOpen = false">Cancel</button>
      <button type="button" class="btn btn-student-primary" :disabled="submitting" @click="confirmSubmit">
        <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
        Submit Quiz
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  summary: {
    type: Object,
    default: () => ({ total_questions: 0, answered: 0, not_answered: 0, flagged: 0 })
  },
  submitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const confirmSubmit = () => emit('confirm')
</script>
