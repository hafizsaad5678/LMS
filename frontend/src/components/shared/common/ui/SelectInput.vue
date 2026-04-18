<template>
  <div :class="wrapperClass">
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
        v-for="(option, index) in normalizedOptions" 
        :key="getOptionKey(option, index)" 
        :value="getOptionValue(option)"
      >
        {{ getOptionLabel(option) }}
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
    required: true
  },
  optionValueKey: {
    type: String,
    default: 'value'
  },
  optionLabelKey: {
    type: String,
    default: 'label'
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
  },
  colClass: {
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

const wrapperClass = computed(() => {
  if (props.colClass && props.noMargin) return props.colClass
  if (props.colClass) return `${props.colClass} mb-3`
  return props.noMargin ? '' : 'mb-3'
})

const normalizedOptions = computed(() => Array.isArray(props.options) ? props.options : [])

const isObjectOption = (option) => option !== null && typeof option === 'object'

const getOptionValue = (option) => {
  if (!isObjectOption(option)) return option
  return option[props.optionValueKey] ?? ''
}

const getOptionLabel = (option) => {
  if (!isObjectOption(option)) return option
  return option[props.optionLabelKey] ?? ''
}

const getOptionKey = (option, index) => {
  const value = getOptionValue(option)
  return value !== '' && value != null ? String(value) : `opt-${index}`
}
</script>
