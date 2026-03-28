<template>
  <div class="text-center py-5">
    <div class="spinner-border" :class="spinnerClass" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="text-muted mt-3">{{ text }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: { type: String, default: 'Loading...' },
  theme: { type: String, default: 'admin' }
})

const spinnerClass = computed(() => {
  const classes = { admin: 'text-danger', teacher: 'text-primary', student: 'text-success' }
  return classes[props.theme] || 'text-danger'
})
</script>
