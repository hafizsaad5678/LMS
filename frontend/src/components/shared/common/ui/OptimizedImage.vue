<template>
  <picture>
    <!-- WebP format for modern browsers -->
    <source 
      v-if="webpSrc" 
      :srcset="webpSrc" 
      type="image/webp"
    >
    <!-- Fallback to original format -->
    <img 
      :src="src" 
      :alt="alt"
      :class="imgClass"
      :style="imgStyle"
      :loading="loading"
      @load="onLoad"
      @error="onError"
    >
  </picture>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  imgClass: {
    type: String,
    default: ''
  },
  imgStyle: {
    type: [String, Object],
    default: ''
  },
  loading: {
    type: String,
    default: 'lazy', // 'lazy' | 'eager'
    validator: (value) => ['lazy', 'eager'].includes(value)
  }
})

const emit = defineEmits(['load', 'error'])

// Automatically generate WebP source if available
const webpSrc = computed(() => {
  if (!props.src) return null
  
  // Check if it's a PNG or JPG
  if (/\.(png|jpg|jpeg)$/i.test(props.src)) {
    return props.src.replace(/\.(png|jpg|jpeg)$/i, '.webp')
  }
  
  return null
})

const onLoad = (event) => {
  emit('load', event)
}

const onError = (event) => {
  emit('error', event)
}
</script>

<style scoped>
/* Ensure images maintain aspect ratio */
img {
  max-width: 100%;
  height: auto;
}
</style>
