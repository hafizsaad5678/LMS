<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'btn w-100 d-flex align-items-center justify-content-center gap-2',
      variantClasses,
      (disabled || loading) ? 'disabled' : ''
    ]"
  >
    <span 
      v-if="loading" 
      class="spinner-border spinner-border-sm me-2" 
      role="status" 
      aria-hidden="true"
    ></span>
    <span>{{ loading ? loadingText : label }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'button'
  },
  label: {
    type: String,
    required: true
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger', 'warning'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Loading...'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const variantClasses = computed(() => {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
    warning: 'btn-warning'
  }
  return variants[props.variant]
})
</script>