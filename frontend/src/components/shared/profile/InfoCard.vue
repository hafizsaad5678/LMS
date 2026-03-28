<template>
  <div class="card border-0 shadow-sm h-100">
    <div class="card-header bg-white border-bottom">
      <h6 class="mb-0 fw-semibold">
        <i :class="[icon, 'me-2', iconColorClass]"></i>{{ title }}
      </h6>
    </div>
    <div class="card-body">
      <div v-for="(item, index) in items" :key="index" class="info-row">
        <span class="info-label">{{ item.label }}</span>
        <span class="info-value" :class="item.class">
          <a v-if="item.href" :href="item.href">{{ item.value || 'N/A' }}</a>
          <span v-else :class="{ 'text-capitalize': item.capitalize }">{{ item.value || 'N/A' }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: 'bi bi-info-circle'
  },
  iconColor: {
    type: String,
    default: 'admin'
  },
  items: {
    type: Array,
    required: true,
    validator: (value) => value.every(item => 'label' in item)
  }
})

const iconColorClass = computed(() => {
  const colorMap = {
    admin: 'text-admin',
    teacher: 'text-teacher',
    student: 'text-student',
    success: 'text-success',
    info: 'text-info',
    warning: 'text-warning',
    danger: 'text-danger'
  }
  return colorMap[props.iconColor] || 'text-admin'
})
</script>

<style scoped>
.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #6c757d;
  font-size: 0.875rem;
}

.info-value {
  font-weight: 500;
  color: #212529;
}

.info-value a {
  color: inherit;
  text-decoration: none;
}

.info-value a:hover {
  text-decoration: underline;
}
</style>
