<template>
  <div 
    :class="[
      'card border-0 shadow-sm',
      hover ? 'shadow-hover' : '',
      paddingClass
    ]"
  >
    <div v-if="title || $slots.header" class="card-header bg-white border-bottom">
      <slot name="header">
        <h3 class="card-title mb-0 fw-semibold">{{ title }}</h3>
      </slot>
    </div>
    
    <div class="card-body">
      <slot></slot>
    </div>
    
    <div v-if="$slots.footer" class="card-footer bg-light border-top">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  padding: {
    type: String,
    default: 'normal',
    validator: (value) => ['none', 'small', 'normal', 'large'].includes(value)
  },
  hover: {
    type: Boolean,
    default: false
  }
})

const paddingClass = computed(() => {
  const paddings = {
    none: '',
    small: 'p-2',
    normal: 'p-3',
    large: 'p-4'
  }
  return paddings[props.padding]
})
</script>

<style scoped>
.shadow-hover:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
}
</style>