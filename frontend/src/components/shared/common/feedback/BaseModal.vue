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
          <div v-if="showFooter" :class="['modal-footer', variant === 'student' ? 'modal-footer-student' : '']">
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
                :class="['btn', resolvedConfirmVariant]" 
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
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
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
  showFooter: {
    type: Boolean,
    default: true
  },
  confirmVariant: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: '', // '', 'teacher', or 'student'
    validator: (value) => ['', 'teacher', 'student'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'hidden', 'confirm'])

const modalRef = ref(null)
let modalInstance = null

const isTeacherContext = computed(() => {
  if (typeof window === 'undefined') return false
  return window.location.pathname.startsWith('/teacher-dashboard')
})

const isStudentContext = computed(() => {
  if (typeof window === 'undefined') return false
  return window.location.pathname.startsWith('/student-dashboard')
})

const resolvedConfirmVariant = computed(() => {
  if (props.confirmVariant) return props.confirmVariant

  if (props.variant === 'teacher' || (!props.variant && isTeacherContext.value)) {
    return 'btn-teacher-primary'
  }

  if (props.variant === 'student' || (!props.variant && isStudentContext.value)) {
    return 'btn-student-primary'
  }

  return 'btn-primary'
})

const syncBodyModalState = () => {
  const hasVisibleModal = Boolean(document.querySelector('.modal.show'))

  if (hasVisibleModal) {
    // Keep scroll lock while at least one modal is still open.
    document.body.classList.add('modal-open')
    document.body.style.overflow = 'hidden'
    return
  }

  document.body.classList.remove('modal-open')
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''

  const backdrops = document.querySelectorAll('.modal-backdrop')
  backdrops.forEach(backdrop => backdrop.remove())
}

onMounted(() => {
  if (modalRef.value) {
    modalInstance = new Modal(modalRef.value)
    
    modalRef.value.addEventListener('hidden.bs.modal', () => {
      emit('update:modelValue', false)
      emit('hidden')

      syncBodyModalState()
    })
  }
})

onUnmounted(() => {
  if (modalInstance) {
    modalInstance.dispose()
  }

  // Cleanup only when no other modal is open.
  syncBodyModalState()
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
