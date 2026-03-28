<template>
  <div class="row g-4">
    <div v-for="(stat, index) in stats" :key="index" :class="colClass">
      <div :class="['stat-card', stat.bgClass || 'bg-admin-light']">
        <i :class="[stat.icon, 'stat-icon', stat.iconColor || 'text-admin']"></i>
        <div class="stat-content">
          <h3>{{ stat.value }}</h3>
          <p>{{ stat.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: {
    type: Array,
    required: true,
    validator: (value) => value.every(stat => 'value' in stat && 'label' in stat && 'icon' in stat)
  },
  columns: {
    type: Number,
    default: 4,
    validator: (value) => [2, 3, 4, 6].includes(value)
  }
})

const colClass = computed(() => {
  const colMap = {
    2: 'col-md-6',
    3: 'col-md-4',
    4: 'col-md-3',
    6: 'col-md-2'
  }
  return colMap[props.columns] || 'col-md-3'
})
</script>
