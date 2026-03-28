<template>
  <div class="card border-0 p-4 quick-action-card" :class="bgGradient">
    <div class="d-flex align-items-start justify-content-between mb-3">
      <div class="quick-action-icon rounded-2 d-flex align-items-center justify-content-center" :class="iconBgColor">
        <i :class="[icon, 'fs-5', iconColor]"></i>
      </div>
    </div>
    <h5 class="fw-semibold text-dark mb-1">{{ title }}</h5>
    <p class="small text-muted mb-0">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  description: String,
  icon: String,
  bgGradient: {
    type: String,
    default: 'bg-light'
  },
  iconBgColor: {
    type: String,
    default: 'bg-primary-light'
  },
  iconColor: {
    type: String,
    default: 'text-primary'
  }
})
</script>
