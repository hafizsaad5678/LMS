<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="modelValue" class="confirm-overlay" @click.self="handleCancel">
        <Transition name="scale">
          <div v-if="modelValue" class="confirm-dialog" :class="themeClass">
            <!-- Icon -->
            <div class="confirm-icon" :class="iconBgClass">
              <i :class="iconClass"></i>
            </div>
            
            <!-- Content -->
            <h4 class="confirm-title">{{ title }}</h4>
            <p class="confirm-message">{{ message }}</p>
            
            <!-- Actions -->
            <div class="confirm-actions">
              <button 
                class="btn-cancel" 
                @click="handleCancel"
                :disabled="loading"
              >
                {{ cancelText }}
              </button>
              <button 
                :class="['btn-confirm', confirmBtnClass]"
                @click="handleConfirm"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    default: 'Are you sure you want to proceed?'
  },
  type: {
    type: String,
    default: 'warning',
    validator: (v) => ['warning', 'danger', 'info', 'success'].includes(v)
  },
  theme: {
    type: String,
    default: 'admin',
    validator: (v) => ['admin', 'teacher', 'student'].includes(v)
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  loading: {
    type: Boolean,
    default: false
  },
  iconClass: { type: String, default: '' },
  iconBgClass: { type: String, default: '' },
  confirmBtnClass: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const themeColors = {
  admin: { primary: '#dc3545', light: 'rgba(220, 53, 69, 0.1)' },
  teacher: { primary: '#0d6efd', light: 'rgba(13, 110, 253, 0.1)' },
  student: { primary: '#198754', light: 'rgba(25, 135, 84, 0.1)' }
}

const typeConfig = {
  warning: { icon: 'bi bi-exclamation-triangle-fill', color: '#ffc107', bg: 'rgba(255, 193, 7, 0.15)' },
  danger: { icon: 'bi bi-x-circle-fill', color: '#dc3545', bg: 'rgba(220, 53, 69, 0.15)' },
  info: { icon: 'bi bi-info-circle-fill', color: '#0dcaf0', bg: 'rgba(13, 202, 240, 0.15)' },
  success: { icon: 'bi bi-check-circle-fill', color: '#198754', bg: 'rgba(25, 135, 84, 0.15)' }
}

const themeClass = computed(() => `theme-${props.theme}`)
const iconClass = computed(() => props.iconClass || typeConfig[props.type].icon)
const iconBgClass = computed(() => props.iconBgClass || `icon-${props.type}`)
const confirmBtnClass = computed(() => props.confirmBtnClass || `btn-${props.theme}`)

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('update:modelValue', false)
  emit('cancel')
}
</script>

<!-- All styles moved to assets/css/components.css -->
