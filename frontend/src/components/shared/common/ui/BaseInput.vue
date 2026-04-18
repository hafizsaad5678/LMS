<template>
  <div class="mb-3">
    <label v-if="label" :for="inputId" class="form-label">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>

    <!-- Date Picker -->
    <div v-if="type === 'date'" class="custom-datepicker-wrapper">
      <VueDatePicker :uid="inputId" v-model="proxyModel" :enable-time-picker="false" model-type="yyyy-MM-dd"
        format="yyyy-MM-dd" auto-apply :placeholder="placeholder" :disabled="disabled" :required="required"
        :state="error ? false : null" :text-input="false" :teleport="true" position="left">
        <template #input-icon>
          <i class="bi bi-calendar-event input-icon-slot"></i>
        </template>
      </VueDatePicker>
    </div>

    <!-- Time Picker -->
    <div v-else-if="type === 'time'" class="custom-datepicker-wrapper">
      <VueDatePicker :uid="inputId" v-model="proxyModel" time-picker model-type="HH:mm" format="HH:mm" auto-apply
        :placeholder="placeholder" :disabled="disabled" :required="required" :state="error ? false : null"
        :text-input="false" :teleport="true" position="left">
        <template #input-icon>
          <i class="bi bi-clock input-icon-slot"></i>
        </template>
      </VueDatePicker>
    </div>

    <!-- Datetime Picker -->
    <div v-else-if="type === 'datetime-local'" class="custom-datepicker-wrapper">
      <VueDatePicker :uid="inputId" v-model="proxyModel" model-type="yyyy-MM-dd HH:mm"
        format="yyyy-MM-dd HH:mm" :placeholder="placeholder" :disabled="disabled" :required="required"
        :state="error ? false : null" :text-input="false" :teleport="true" position="left">
        <template #input-icon>
          <i class="bi bi-calendar-check input-icon-slot"></i>
        </template>
      </VueDatePicker>
    </div>

    <!-- Standard Input -->
    <div v-if="!['date', 'time', 'datetime-local'].includes(type)" :class="{ 'position-relative': type === 'password' }">
      <input :id="inputId" :type="inputType" :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)" :placeholder="placeholder" :required="required"
        :disabled="disabled" :class="[
          'form-control',
          error ? 'is-invalid' : '',
          type === 'password' ? 'pe-5' : ''
        ]" />

      <button v-if="type === 'password'" type="button"
        class="btn btn-link position-absolute end-0 top-50 translate-middle-y text-muted text-decoration-none border-0 shadow-none px-3"
        @click="showPassword = !showPassword" tabindex="-1">
        <i :class="['bi', showPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
      </button>
    </div>

    <div v-if="error" class="invalid-feedback d-block mt-1">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
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

const showPassword = ref(false)

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const inputType = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'text' : 'password'
  }
  return props.type
})

const proxyModel = computed({
  get() {
    return props.modelValue
  },
  set(val) {
    emit('update:modelValue', val)
  }
})
</script>
