<template>
  <Transition name="slide-fade">
    <div 
      v-if="message"
      :class="[
        'alert-custom',
        alertTypeClass
      ]"
      role="alert"
    >
      <div class="alert-content">
        <div class="alert-icon-wrapper">
          <div :class="['alert-icon', iconClass]">
            <i :class="iconName"></i>
          </div>
        </div>
        
        <div class="alert-body">
          <h5 class="alert-title">{{ title }}</h5>
          <p class="alert-message">{{ message }}</p>
        </div>
        
        <div class="alert-actions">
          <button 
            v-if="showConfirmButton"
            @click="$emit('confirm')"
            :class="['btn-confirm', confirmButtonClass]"
          >
            {{ confirmText }}
          </button>
          <button 
            @click="handleClose"
            :class="['btn-close-custom', closeButtonClass]"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
      
      <div class="alert-progress" v-if="autoClose && !showConfirmButton">
        <div class="alert-progress-bar" :style="{ animationDuration: `${autoCloseDuration}ms` }"></div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  message: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: null
  },
  showConfirmButton: {
    type: Boolean,
    default: false
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  autoClose: {
    type: Boolean,
    default: false
  },
  autoCloseDuration: {
    type: Number,
    default: 5000
  }
})

const emit = defineEmits(['close', 'confirm'])

const alertTypeClass = computed(() => {
  const classes = {
    success: 'alert-success',
    error: 'alert-error',
    warning: 'alert-warning',
    info: 'alert-info'
  }
  return classes[props.type]
})

const iconClass = computed(() => {
  const classes = {
    success: 'icon-success',
    error: 'icon-error',
    warning: 'icon-warning',
    info: 'icon-info'
  }
  return classes[props.type]
})

const iconName = computed(() => {
  const icons = {
    success: 'bi bi-check-circle-fill',
    error: 'bi bi-x-circle-fill',
    warning: 'bi bi-exclamation-triangle-fill',
    info: 'bi bi-info-circle-fill'
  }
  return icons[props.type]
})

const title = computed(() => {
  if (props.title) return props.title
  const titles = {
    success: 'Success!',
    error: 'Error!',
    warning: 'Warning!',
    info: 'Information'
  }
  return titles[props.type]
})

const confirmButtonClass = computed(() => {
  const classes = {
    success: 'btn-success',
    error: 'btn-error',
    warning: 'btn-warning',
    info: 'btn-info'
  }
  return classes[props.type]
})

const closeButtonClass = computed(() => {
  return props.showConfirmButton ? 'btn-secondary' : 'btn-ghost'
})

const handleClose = () => {
  emit('close')
}

// Auto close functionality
if (props.autoClose && !props.showConfirmButton) {
  onMounted(() => {
    setTimeout(() => {
      handleClose()
    }, props.autoCloseDuration)
  })
}
</script>

<style scoped>
.alert-custom {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 400px;
  max-width: 500px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
  z-index: 9999;
  overflow: hidden;
}

.alert-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
}

.alert-icon-wrapper {
  flex-shrink: 0;
}

.alert-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.icon-success {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  color: #155724;
}

.icon-error {
  background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
  color: #721c24;
}

.icon-warning {
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  color: #856404;
}

.icon-info {
  background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
  color: #0c5460;
}

.alert-body {
  flex: 1;
  min-width: 0;
}

.alert-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.3;
}

.alert-message {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.alert-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-confirm,
.btn-close-custom {
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-confirm {
  min-width: 80px;
}

.btn-confirm.btn-success {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
}

.btn-confirm.btn-error {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
}

.btn-confirm.btn-warning {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
  color: #1a1a1a;
}

.btn-confirm.btn-info {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
  color: white;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-close-custom {
  width: 32px;
  height: 32px;
  padding: 0;
  background: transparent;
  color: #999;
}

.btn-close-custom.btn-secondary {
  background: #e9ecef;
  color: #495057;
}

.btn-close-custom:hover {
  background: #f8f9fa;
  color: #1a1a1a;
}

.btn-close-custom.btn-secondary:hover {
  background: #dee2e6;
}

.alert-progress {
  height: 4px;
  background: rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.alert-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  animation: progress linear forwards;
  transform-origin: left;
}

@keyframes progress {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

/* Alert type specific borders */
.alert-success {
  border-left: 4px solid #28a745;
}

.alert-error {
  border-left: 4px solid #dc3545;
}

.alert-warning {
  border-left: 4px solid #ffc107;
}

.alert-info {
  border-left: 4px solid #17a2b8;
}

/* Transition animations */
.slide-fade-enter-active {
  animation: slideIn 0.3s ease-out;
}

.slide-fade-leave-active {
  animation: slideOut 0.3s ease-in;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0) translateY(0);
  }
}

@keyframes slideOut {
  from {
    opacity: 1;
    transform: translateX(0) translateY(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%) translateY(-20px);
  }
}

/* Responsive */
@media (max-width: 576px) {
  .alert-custom {
    min-width: calc(100vw - 40px);
    max-width: calc(100vw - 40px);
    right: 20px;
    left: 20px;
    top: 10px;
  }
  
  .alert-content {
    padding: 16px;
    gap: 12px;
  }
  
  .alert-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .alert-title {
    font-size: 16px;
  }
  
  .alert-message {
    font-size: 13px;
  }
}
</style>
