<template>
  <div class="dash-card" :class="bgClass" @click="$emit('click')">
    <div class="stat-icon"><i :class="icon"></i></div>
    <div class="stat-content">
      <template v-if="loading">
        <div class="skeleton-stat-value bg-white bg-opacity-25 rounded mb-2"></div>
        <div class="skeleton-stat-label bg-white bg-opacity-10 rounded"></div>
      </template>
      <template v-else>
        <h3>{{ formattedValue }}</h3>
        <p>{{ label }}</p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: [String, Number], default: 0 },
  label: { type: String, required: true },
  icon: { type: String, default: 'bi bi-circle' },
  bgClass: { type: String, default: 'bg-gradient-blue' },
  loading: { type: Boolean, default: false },
  isCurrency: { type: Boolean, default: false },
  currencySymbol: { type: String, default: 'PKR' }
})

defineEmits(['click'])

const formattedValue = computed(() => {
  if (props.isCurrency) {
    return `${props.currencySymbol} ${Number(props.value).toLocaleString()}`
  }
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})
</script>
