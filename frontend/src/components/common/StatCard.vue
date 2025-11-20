<template>
  <div class="card border-0 shadow-sm h-100 stat-card">
    <div class="card-body d-flex justify-content-between align-items-start">
      <div class="flex-grow-1">
        <p class="text-muted small fw-medium mb-2">{{ title }}</p>
        <p class="display-6 fw-bold text-dark mb-3">{{ value }}</p>
        <p class="small" :class="changeColor">
          <i :class="isPositive ? 'bi bi-arrow-up' : 'bi bi-arrow-down'" class="me-1"></i>
          {{ change }} from last month
        </p>
      </div>
      <div class="rounded-3 d-flex align-items-center justify-content-center" :class="iconBgColor" style="width: 56px; height: 56px;">
        <i :class="[icon, 'fs-4', iconColorClass]"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  title: String,
  value: [String, Number],
  change: String,
  icon: String,
  bgColor: {
    type: String,
    default: 'bg-primary-light'
  },
  iconColor: {
    type: String,
    default: 'text-primary'
  },
  isPositive: {
    type: Boolean,
    default: true
  }
});

const changeColor = computed(() => 
  props.isPositive ? 'text-success' : 'text-danger'
);

const iconBgColor = computed(() => props.bgColor);

const iconColorClass = computed(() => props.iconColor);
</script>

<style scoped>
.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
}

.bg-primary-light {
  background-color: rgba(13, 110, 253, 0.1);
}
</style>