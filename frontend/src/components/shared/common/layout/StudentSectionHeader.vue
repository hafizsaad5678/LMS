<template>
  <div class="card-header bg-student-light border-bottom border-student">
    <h5 class="mb-0" :class="titleClass">
      <i v-if="iconClass" :class="iconClass" class="me-2"></i>{{ title }}
    </h5>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  titleClass: { type: String, default: 'text-student' },
  iconClass: { type: String, default: '' }
})
</script>