<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal show d-block" tabindex="-1" 
         style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
      <div class="modal-dialog modal-dialog-centered" :class="sizeClass">
        <div class="modal-content">
          <div class="modal-header" :class="headerClass">
            <h5 class="modal-title">
              <i v-if="icon" :class="[icon, 'me-2']"></i>
              {{ title }}
            </h5>
            <button type="button" class="btn-close" :class="{ 'btn-close-white': headerVariant }" @click="close"></button>
          </div>
          <div class="modal-body">
            <slot></slot>
          </div>
          <div v-if="showFooter" class="modal-footer">
            <slot name="footer">
              <button type="button" @click="close" class="btn btn-secondary" :disabled="loading">
                {{ cancelText }}
              </button>
              <button type="button" @click="$emit('confirm')" :class="['btn', confirmVariant]" :disabled="loading">
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
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Modal' },
  icon: { type: String, default: '' },
  size: { type: String, default: 'md' }, // sm, md, lg, xl
  loading: { type: Boolean, default: false },
  showFooter: { type: Boolean, default: true },
  confirmText: { type: String, default: 'Save' },
  cancelText: { type: String, default: 'Cancel' },
  confirmVariant: { type: String, default: 'btn-primary' },
  headerVariant: { type: String, default: '' } // danger, success, warning, admin, teacher
})

const emit = defineEmits(['update:modelValue', 'confirm', 'close'])

const sizeClass = computed(() => {
  const sizes = { sm: 'modal-sm', lg: 'modal-lg', xl: 'modal-xl' }
  return sizes[props.size] || ''
})

const headerClass = computed(() => {
  if (!props.headerVariant) return ''
  const variants = {
    danger: 'bg-danger text-white',
    success: 'bg-success text-white',
    warning: 'bg-warning',
    admin: 'bg-admin text-white',
    teacher: 'bg-teacher text-white',
    student: 'bg-student text-white'
  }
  return variants[props.headerVariant] || ''
})

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}
</script>
