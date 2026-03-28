<template>
  <Teleport to="body">
    <div 
      class="modal fade" 
      :id="id" 
      tabindex="-1" 
      ref="modalRef"
      :class="{ 'modal-student': variant === 'student' }"
    >
      <div :class="['modal-dialog', size ? `modal-${size}` : '']">
        <div :class="['modal-content', variant === 'student' ? 'modal-content-student' : '']">
          <div :class="['modal-header', variant === 'student' ? 'modal-header-student' : '']">
            <h5 class="modal-title" :class="titleClass">
              <slot name="title">{{ title }}</slot>
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <slot></slot>
          </div>
          <div :class="['modal-footer', variant === 'student' ? 'modal-footer-student' : '']">
            <slot name="footer">
              <button 
                type="button" 
                class="btn btn-light" 
                data-bs-dismiss="modal"
                :disabled="loading"
              >
                {{ cancelText }}
              </button>
              <button 
                type="button" 
                :class="['btn', confirmVariant]" 
                @click="$emit('confirm')"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ confirmText }}
              </button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Modal from 'bootstrap/js/dist/modal'

const props = defineProps({
  id: {
    type: String,
    required: false,
    default: () => `modal-${Math.random().toString(36).slice(2, 11)}`
  },
  title: {
    type: String,
    default: 'Modal Title'
  },
  titleClass: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: '' // 'sm', 'lg', 'xl'
  },
  modelValue: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  confirmVariant: {
    type: String,
    default: 'btn-primary'
  },
  variant: {
    type: String,
    default: '', // 'student' for green theme
    validator: (value) => ['', 'student'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'hidden', 'confirm'])

const modalRef = ref(null)
let modalInstance = null

onMounted(() => {
  if (modalRef.value) {
    modalInstance = new Modal(modalRef.value)
    
    modalRef.value.addEventListener('hidden.bs.modal', () => {
      emit('update:modelValue', false)
      emit('hidden')
      
      // Ensure body classes are cleaned up
      document.body.classList.remove('modal-open')
      document.body.style.overflow = ''
      document.body.style.paddingRight = ''
      
      // Remove any leftover backdrops
      const backdrops = document.querySelectorAll('.modal-backdrop')
      backdrops.forEach(backdrop => backdrop.remove())
    })
  }
})

onUnmounted(() => {
  if (modalInstance) {
    modalInstance.dispose()
  }
  
  // Cleanup on unmount
  document.body.classList.remove('modal-open')
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
  
  const backdrops = document.querySelectorAll('.modal-backdrop')
  backdrops.forEach(backdrop => backdrop.remove())
})

watch(() => props.modelValue, (newVal) => {
  if (modalInstance) {
    if (newVal) {
      modalInstance.show()
    } else {
      modalInstance.hide()
    }
  }
})
</script>
