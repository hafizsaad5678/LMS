<template>
  <div class="text-center py-5">
    <div v-if="showAvatar" class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
      <i :class="[icon, 'display-4']"></i>
    </div>
    <i v-else :class="[icon, 'display-1 text-muted']"></i>
    <h4 class="text-muted mt-3">{{ title }}</h4>
    <p v-if="subtitle" class="text-muted mb-4">{{ subtitle }}</p>
    <button v-if="buttonText" @click="$emit('action')" :class="buttonClass">
      <i v-if="buttonIcon" :class="[buttonIcon, 'me-2']"></i>{{ buttonText }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: String, default: 'bi bi-inbox' },
  title: { type: String, default: 'No Data Found' },
  subtitle: { type: String, default: '' },
  buttonText: { type: String, default: '' },
  buttonIcon: { type: String, default: 'bi bi-list-ul' },
  buttonVariant: { type: String, default: 'btn-admin-primary' },
  showAvatar: { type: Boolean, default: false }
})

defineEmits(['action'])

const buttonClass = computed(() => `btn ${props.buttonVariant}`)
</script>
