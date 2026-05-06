<template>
  <div class="image-upload-container">
    <label v-if="label" class="form-label">{{ label }} <span v-if="required" class="text-danger">*</span></label>
    
    <div 
      class="upload-area rounded-4 d-flex flex-column align-items-center justify-content-center p-4"
      :class="{ 'has-preview': displayUrl, 'is-dragging': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="$refs.fileInput.click()"
    >
      <input 
        type="file" 
        ref="fileInput" 
        class="d-none" 
        accept="image/*" 
        @change="handleFileChange"
      >
      
      <div v-if="displayUrl" class="preview-wrapper w-100 h-100 position-relative">
        <img :src="displayUrl" class="img-fluid rounded-3 preview-img" alt="Preview">
        <div class="preview-overlay d-flex align-items-center justify-content-center">
          <i class="bi bi-camera-fill text-white fs-4"></i>
          <span class="text-white ms-2 small">Change Image</span>
        </div>
        <button 
          type="button" 
          class="btn btn-sm btn-danger position-absolute top-0 end-0 m-2 rounded-circle shadow-sm"
          @click.stop="removeImage"
          title="Remove image"
        >
          <i class="bi bi-x"></i>
        </button>
      </div>
      
      <div v-else class="upload-placeholder text-center">
        <div class="icon-circle mb-3 mx-auto">
          <i class="bi bi-cloud-arrow-up fs-2"></i>
        </div>
        <p class="mb-1 fw-semibold text-dark">Click or drag to upload</p>
        <p class="text-muted small mb-0">PNG, JPG or WEBP (Max 5MB)</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { getFileUrl } from '@/utils/constants/config'

const props = defineProps({
  modelValue: { type: [String, File, Object], default: null },
  label: { type: String, default: '' },
  required: { type: Boolean, default: false },
  existingImageUrl: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue', 'change'])

const fileInput = ref(null)
const localPreviewUrl = ref('')
const isDragging = ref(false)

// Determine what to show
const displayUrl = computed(() => {
  // 1. If we have a local preview (from FileReader), show it
  if (localPreviewUrl.value) return localPreviewUrl.value
  
  // 2. If modelValue is a string (URL from server), show it
  let url = props.modelValue
  if (typeof url !== 'string') {
    url = props.existingImageUrl
  }
  
  if (typeof url === 'string' && url) {
    return getFileUrl(url)
  }
  
  return ''
})

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = (file) => {
  // Validate size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('File size exceeds 5MB limit.')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    localPreviewUrl.value = e.target.result
    emit('update:modelValue', file)
    emit('change', file)
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  localPreviewUrl.value = ''
  if (fileInput.value) fileInput.value.value = ''
  emit('update:modelValue', null)
  emit('change', null)
}

// If modelValue changes externally to a string or null, clear local preview
watch(() => props.modelValue, (newVal) => {
  if (!(newVal instanceof File)) {
    localPreviewUrl.value = ''
  }
})
</script>


<style scoped>
/* Component styles are extracted to institution.css */
</style>
