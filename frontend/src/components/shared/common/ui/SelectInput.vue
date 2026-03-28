<template>
  <div :class="noMargin ? '' : 'mb-3'">
    <label v-if="label" :for="inputId" class="form-label" :class="labelClass">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <select
      :id="inputId"
      v-model="modelValue"
      class="form-select"
      :class="{ 'is-invalid': error }"
      :required="required"
      :disabled="disabled"
      @change="$emit('change', $event)"
    >
      <option value="">{{ placeholder }}</option>
      <option 
        v-for="option in options" 
        :key="option.value" 
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    <div v-if="error" class="invalid-feedback">{{ error }}</div>
    <small v-if="hint" class="text-muted">{{ hint }}</small>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    required: true,
    validator: (value) => value.every(opt => 'value' in opt && 'label' in opt)
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  id: {
    type: String,
    default: ''
  },
  noMargin: {
    type: Boolean,
    default: false
  },
  labelClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const modelValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const inputId = computed(() => props.id || `select-${Math.random().toString(36).slice(2, 11)}`)
</script>
