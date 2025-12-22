<template>
  <Teleport to="body">
    <div 
      class="modal fade" 
      :id="id" 
      tabindex="-1" 
      ref="modalRef"
    >
      <div :class="['modal-dialog', size ? `modal-${size}` : '']">
        <div class="modal-content">
          <div class="modal-header">
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
          <div class="modal-footer" v-if="$slots.footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Modal } from 'bootstrap'

const props = defineProps({
  id: {
    type: String,
    required: true
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
  }
})

const emit = defineEmits(['update:modelValue', 'hidden'])

const modalRef = ref(null)
let modalInstance = null

onMounted(() => {
  if (modalRef.value) {
    modalInstance = new Modal(modalRef.value)
    
    modalRef.value.addEventListener('hidden.bs.modal', () => {
      emit('update:modelValue', false)
      emit('hidden')
    })
  }
})

onUnmounted(() => {
  if (modalInstance) {
    modalInstance.dispose()
  }
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
