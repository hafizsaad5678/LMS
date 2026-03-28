<template>
  <div class="row justify-content-center">
    <div class="col-lg-6">
      <div class="card border-0 shadow-sm border-top-danger">
        <div class="card-body p-4 text-center">
          <div class="mb-4">
            <div class="avatar-circle-lg mx-auto mb-3 bg-danger-light text-danger">
              <i class="bi bi-exclamation-triangle-fill display-6"></i>
            </div>
            <h4 class="fw-bold text-danger mb-2">{{ title }}</h4>
            <p class="text-muted mb-0">{{ message }}</p>
          </div>

          <!-- Entity Info -->
          <div class="bg-light p-3 rounded-3 mb-4 text-start">
            <div v-for="(item, index) in infoItems" :key="index" class="d-flex align-items-center" :class="{ 'mb-2': index < infoItems.length - 1 }">
              <span class="text-muted small me-2">{{ item.label }}:</span>
              <span class="fw-semibold">{{ item.value || 'N/A' }}</span>
            </div>
          </div>

          <div class="alert alert-warning border-0 d-flex align-items-start text-start mb-4">
            <i class="bi bi-info-circle-fill me-2 mt-1"></i>
            <small>Please type <strong>DELETE</strong> to confirm.</small>
          </div>

          <div class="mb-4">
            <input 
              v-model="confirmText"
              type="text" 
              class="form-control text-center" 
              placeholder="Type DELETE to confirm"
              @keyup.enter="handleDelete"
            >
          </div>

          <div class="d-flex gap-2 justify-content-center">
            <button @click="$emit('cancel')" class="btn btn-light px-4" :disabled="loading">Cancel</button>
            <button @click="handleDelete" class="btn btn-danger px-4" :disabled="loading || confirmText !== 'DELETE'">
              <span v-if="loading"><span class="spinner-border spinner-border-sm me-2"></span>Deleting...</span>
              <span v-else>{{ confirmButtonText }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Delete Item?' },
  message: { type: String, default: 'This action cannot be undone.' },
  infoItems: { type: Array, default: () => [] }, // [{ label: 'Name', value: 'John' }]
  confirmButtonText: { type: String, default: 'Delete' },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel'])
const confirmText = ref('')

const handleDelete = () => {
  if (confirmText.value === 'DELETE') {
    emit('confirm')
  }
}
</script>
