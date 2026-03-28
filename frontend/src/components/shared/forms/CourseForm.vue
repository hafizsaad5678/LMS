<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
      <h5 class="card-title mb-0 fw-semibold">
        <i class="bi bi-mortarboard me-2 text-admin"></i>
        Course Information
      </h5>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="$emit('submit')">
        <!-- Basic Information -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-info-circle me-2"></i>Basic Information
          </h6>
          <div class="row g-3">
            <div class="col-md-8">
              <BaseInput v-model="modelValue.name" label="Course Name" type="text" placeholder="e.g., Bachelor of Computer Science" :required="true" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.code" label="Course Code" type="text" placeholder="e.g., BSCS" :required="true" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Department <span class="text-danger">*</span></label>
              <select v-model="modelValue.department" class="form-select" required>
                <option value="">Select Department</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }} ({{ dept.code }})</option>
              </select>
            </div>
            <div class="col-md-6">
              <BaseInput v-model.number="modelValue.duration_years" label="Duration (Years)" type="number" placeholder="4" :required="true" />
            </div>
          </div>
        </div>

        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-text-paragraph me-2"></i>Description
          </h6>
          <RichTextEditor v-model="modelValue.description" placeholder="Enter course description..." />
        </div>

        <!-- Form Actions -->
        <div class="d-flex gap-3 justify-content-end pt-3 border-top">
          <button type="button" @click="$emit('cancel')" class="btn btn-admin-outline px-4" :disabled="submitting">
            <i class="bi bi-x-circle me-2"></i>Cancel
          </button>
          <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
            <span v-if="submitting"><span class="spinner-border spinner-border-sm me-2"></span>{{ isEditMode ? 'Updating...' : 'Adding...' }}</span>
            <span v-else><i class="bi bi-check-circle me-2"></i>{{ isEditMode ? 'Update' : 'Add' }} Course</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { BaseInput, RichTextEditor } from '@/components/shared/common'

defineProps({
  modelValue: { type: Object, required: true },
  departments: { type: Array, default: () => [] },
  isEditMode: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'submit', 'cancel'])
</script>
