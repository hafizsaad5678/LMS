<template>
  <div class="mb-3">
    <label 
      v-if="label" 
      :for="inputId" 
      class="form-label"
    >
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>

    <!-- Date Picker -->
    <div v-if="type === 'date'" class="custom-datepicker-wrapper">
      <VueDatePicker
        :uid="inputId"
        v-model="proxyModel"
        :enable-time-picker="false"
        model-type="yyyy-MM-dd"
        format="yyyy-MM-dd"
        auto-apply
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :state="error ? false : null"
        text-input
        :teleport="true"
        position="left"
      >
        <template #input-icon>
          <i class="bi bi-calendar-event input-icon-slot"></i>
        </template>
      </VueDatePicker>
    </div>

    <!-- Standard Input -->
    <input
      v-else
      :id="inputId"
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :class="[
        'form-control',
        error ? 'is-invalid' : ''
      ]"
    />
    
    <div v-if="error" class="invalid-feedback d-block mt-1">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

const props = defineProps({
  modelValue: {
    type: [String, Number, Date],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const proxyModel = computed({
  get() {
    return props.modelValue
  },
  set(val) {
    emit('update:modelValue', val)
  }
})
</script>

<style>
/* Override VueDatePicker variables to match Bootstrap */
:root {
  --dp-font-family: inherit;
  --dp-border-radius: 0.375rem; /* Bootstrap .rounded */
  --dp-input-padding: 0.375rem 0.75rem 0.375rem 2.5rem; /* Bootstrap .form-control padding with space for icon */
  --dp-menu-min-width: 100%; /* Full width menu */
  --dp-primary-color: #0d6efd; /* Bootstrap primary */
}

/* Specific adjustments */
.dp__input {
  display: block;
  width: 100%;
  padding: 0.375rem 0.75rem 0.375rem 2.5rem;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;
  color: #212529;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid #dee2e6;
  appearance: none;
  border-radius: 0.375rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  height: 38px; /* Match bootstrap standard input height */
}

.dp__input:focus {
  color: #212529;
  background-color: #fff;
  border-color: #86b7fe;
  outline: 0;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.dp__input_invalid {
  border-color: #dc3545;
  padding-right: calc(1.5em + 0.75rem);
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' width='12' height='12' fill='none' stroke='%23dc3545'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5zM6 8.2a.3.3 0 00-.6 0 .3.3 0 00.6 0z'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right calc(0.375em + 0.1875rem) center;
  background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
}

.dp__input_invalid:focus {
  border-color: #dc3545;
  box-shadow: 0 0 0 0.25rem rgba(220, 53, 69, 0.25);
}

.input-icon-slot {
  margin-left: 10px;
  color: #6c757d;
}
</style>