<template>
  <button :type="type" :disabled="disabled || loading" :class="[
    'btn w-100 d-flex align-items-center justify-content-center gap-2',
    variantClasses,
    (disabled || loading) ? 'disabled' : ''
  ]">
    <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    <slot>
      <span>{{ loading ? loadingText : label }}</span>
    </slot>
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
    required: false,
    default: ''
  },
  variant: {
    type: String,
    default: 'primary'
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
    warning: 'btn-warning',
    success: 'btn-success',
    info: 'btn-info',
    light: 'btn-light',
    dark: 'btn-dark',
    link: 'btn-link'
  }
  return variants[props.variant] || `btn-${props.variant}`
})
</script>
