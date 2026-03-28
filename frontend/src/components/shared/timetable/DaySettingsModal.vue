<template>
  <div v-if="show" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-admin text-white">
          <h5 class="modal-title"><i class="bi bi-gear me-2"></i>Day-Specific Period Settings</h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <p class="text-muted mb-3">Set different period durations for each day</p>
          <div v-for="(day, index) in days" :key="day" class="row g-3 mb-3 align-items-center">
            <div class="col-md-4">
              <label class="form-label fw-semibold">{{ dayLabels[index] }}</label>
            </div>
            <div class="col-md-4">
              <select v-model="settings[day].duration" class="form-select form-select-sm">
                <option v-for="opt in durationOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <input v-model="settings[day].startTime" type="time" class="form-control form-control-sm">
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" @click="$emit('close')" class="btn btn-secondary">Close</button>
          <button type="button" @click="$emit('apply')" class="btn btn-admin-primary">Apply Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { DAYS_OF_WEEK, DAY_LABELS, PERIOD_DURATIONS } from '@/utils/constants/config'

defineProps({
  show: { type: Boolean, default: false },
  settings: { type: Object, required: true },
  days: { type: Array, default: () => DAYS_OF_WEEK },
  dayLabels: { type: Array, default: () => DAY_LABELS },
  durationOptions: { type: Array, default: () => PERIOD_DURATIONS }
})

defineEmits(['close', 'apply'])
</script>
