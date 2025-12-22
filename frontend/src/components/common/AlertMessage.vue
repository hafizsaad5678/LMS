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
