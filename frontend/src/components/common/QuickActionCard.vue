<template>
  <div class="card border-0 p-4 quick-action-card" :class="bgGradient">
    <div class="d-flex align-items-start justify-content-between mb-3">
      <div class="rounded-2 d-flex align-items-center justify-content-center" :class="iconBgColor" style="width: 48px; height: 48px;">
        <i :class="[icon, 'fs-5', iconColor]"></i>
      </div>
    </div>
    <h5 class="fw-semibold text-dark mb-1">{{ title }}</h5>
    <p class="small text-muted mb-0">{{ description }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
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
});
</script>

<style scoped>
.quick-action-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.quick-action-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-2px);
}

.bg-primary-light {
  background-color: rgba(13, 110, 253, 0.1);
}
</style>