<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
      <h5 class="card-title mb-0 fw-semibold">
        <i class="bi bi-bank2 me-2 text-admin"></i>
        Institution Information
      </h5>
    </div>
    <div class="card-body p-4">
      <!-- Read-only Info (Edit Mode) -->
      <div v-if="isEditMode" class="mb-4 p-3 bg-light rounded">
        <div class="row">
          <div class="col-md-4">
            <label class="form-label text-muted small mb-1">Institution Code</label>
            <p class="fw-semibold mb-0">{{ modelValue.code }}</p>
          </div>
          <div class="col-md-4">
            <label class="form-label text-muted small mb-1">Established</label>
            <p class="fw-semibold mb-0">{{ modelValue.established_year || 'N/A' }}</p>
          </div>
          <div class="col-md-4">
            <label class="form-label text-muted small mb-1">Status</label>
            <p class="mb-0">
              <span :class="['badge', modelValue.is_active ? 'bg-success' : 'bg-warning']">
                {{ modelValue.is_active ? 'Active' : 'Inactive' }}
              </span>
            </p>
          </div>
        </div>
      </div>

      <form @submit.prevent="$emit('submit')">
        <!-- Basic Information -->
        <div class="mb-5">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-info-circle me-2 text-admin"></i>Basic Information
          </h6>
          <div class="row g-4">
            <div class="col-md-8">
              <BaseInput v-model="modelValue.name" label="Institution Name" type="text" placeholder="e.g., Govt Graduate College" :required="true" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.short_name" label="Short Name" type="text" placeholder="e.g., GGCA" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.code" label="Institution Code" type="text" placeholder="e.g., GGCA-001" :required="true" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.slug" label="URL Slug" type="text" placeholder="e.g., gc-aroop" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model.number="modelValue.established_year" label="Established Year" type="number" placeholder="e.g., 1990" />
            </div>
          </div>
        </div>

        <!-- Contact Information -->
        <div class="mb-5">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-envelope me-2 text-admin"></i>Contact Information
          </h6>
          <div class="row g-4">
            <div class="col-md-4">
              <BaseInput v-model="modelValue.email" label="Public Email" type="email" placeholder="info@institution.edu.pk" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.phone" label="Public Phone" type="tel" placeholder="+92 51 1234567" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.website" label="Website URL" type="url" placeholder="https://www.example.edu.pk" />
            </div>
          </div>
        </div>

        <!-- Address Information -->
        <div class="mb-5">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-geo-alt me-2 text-admin"></i>Address Information
          </h6>
          <div class="row g-4">
            <div class="col-12">
              <label class="form-label">Full Address</label>
              <textarea v-model="modelValue.address" class="form-control" rows="2" placeholder="Enter complete address..."></textarea>
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.city" label="City" type="text" placeholder="e.g., Islamabad" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.state" label="State/Province" type="text" placeholder="e.g., Federal" />
            </div>
            <div class="col-md-4">
              <BaseInput v-model="modelValue.postal_code" label="Postal Code" type="text" placeholder="e.g., 44000" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Country</label>
              <select v-model="modelValue.country" class="form-select">
                <option v-for="country in COUNTRIES" :key="country" :value="country">{{ country }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="mb-4 pt-3 border-top">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-text-paragraph me-2"></i>Description
          </h6>
          <textarea v-model="modelValue.description" class="form-control" rows="4" placeholder="Enter institution description..."></textarea>
        </div>

        <!-- Status -->
        <div class="mb-4">
          <div class="form-check form-switch">
            <input v-model="modelValue.is_active" class="form-check-input" type="checkbox" id="isActive">
            <label class="form-check-label" for="isActive">Active Institution</label>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="d-flex gap-3 justify-content-end pt-3 border-top">
          <button type="button" @click="$emit('cancel')" class="btn btn-outline-secondary px-4" :disabled="submitting">
            <i class="bi bi-x-circle me-2"></i>Cancel
          </button>
          <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
            <span v-if="submitting"><span class="spinner-border spinner-border-sm me-2"></span>{{ isEditMode ? 'Updating...' : 'Adding...' }}</span>
            <span v-else><i class="bi bi-check-circle me-2"></i>{{ isEditMode ? 'Update' : 'Add' }} Institution</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { BaseInput, ImageUpload } from '@/components/shared/common'
import { COUNTRIES } from '@/utils/constants/config'

defineProps({
  modelValue: { type: Object, required: true },
  isEditMode: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'submit', 'cancel'])
</script>
