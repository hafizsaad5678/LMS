<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
      <h5 class="card-title mb-0 fw-semibold">
        <i class="bi bi-building me-2 text-admin"></i>
        Department Information
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
              <BaseInput v-model="modelValue.name" label="Department Name" type="text" placeholder="e.g., Computer Science" :required="true" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.code" label="Department Code" type="text" placeholder="e.g., CS" :required="true" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Institution</label>
              <select v-model="modelValue.institution" class="form-select">
                <option value="">Select Institution</option>
                <option v-for="inst in institutions" :key="inst.id" :value="String(inst.id)">{{ inst.name }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <BaseInput v-model="modelValue.head_of_department" label="Head of Department" type="text" placeholder="e.g., Dr. John Smith" />
            </div>
          </div>
        </div>

        <!-- Contact Information -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-envelope me-2"></i>Contact Information
          </h6>
          <div class="row g-3">
            <div class="col-md-6">
              <BaseInput v-model="modelValue.email" label="Email" type="email" placeholder="department@university.edu" />
            </div>
            <div class="col-md-6">
              <BaseInput v-model="modelValue.phone" label="Phone" type="tel" placeholder="+92 000-0000000" />
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="mb-4">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-text-paragraph me-2"></i>Description
          </h6>
          <textarea v-model="modelValue.description" class="form-control" rows="4" placeholder="Enter department description..."></textarea>
        </div>

        <!-- Status (Edit Mode) -->
        <div v-if="isEditMode" class="mb-4">
          <div class="form-check form-switch">
            <input v-model="modelValue.is_active" class="form-check-input" type="checkbox" id="isActive">
            <label class="form-check-label" for="isActive">Active Department</label>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="d-flex gap-3 justify-content-end pt-3 border-top">
          <button type="button" @click="$emit('cancel')" class="btn btn-admin-outline px-4" :disabled="submitting">
            <i class="bi bi-x-circle me-2"></i>Cancel
          </button>
          <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
            <span v-if="submitting"><span class="spinner-border spinner-border-sm me-2"></span>{{ isEditMode ? 'Updating...' : 'Adding...' }}</span>
            <span v-else><i class="bi bi-check-circle me-2"></i>{{ isEditMode ? 'Update' : 'Add' }} Department</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { BaseInput } from '@/components/shared/common'

defineProps({
  modelValue: { type: Object, required: true },
  institutions: { type: Array, default: () => [] },
  isEditMode: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'submit', 'cancel'])
</script>
