<template>
  <AdminPageTemplate
    title="Edit Institution"
    subtitle="Update institution information"
    icon="bi bi-bank2"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="alert.show = false"
    />

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-admin" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading institution details...</p>
    </div>

    <div v-else-if="!institutionId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-bank2 display-4"></i>
      </div>
      <h4 class="text-muted">No Institution Selected</h4>
      <p class="text-muted mb-4">Please select an institution from the list to edit.</p>
      <button @click="router.push('/admin-dashboard/institution')" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Institution List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-10">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-bank2 me-2 text-admin"></i>
              Institution Information
            </h5>
          </div>
          <div class="card-body p-4">
            <!-- Read-only Info -->
            <div class="mb-4 p-3 bg-light rounded">
              <div class="row">
                <div class="col-md-4">
                  <label class="form-label text-muted small mb-1">Institution Code</label>
                  <p class="fw-semibold mb-0">{{ form.code }}</p>
                </div>
                <div class="col-md-4">
                  <label class="form-label text-muted small mb-1">Established</label>
                  <p class="fw-semibold mb-0">{{ form.established_year || 'N/A' }}</p>
                </div>
                <div class="col-md-4">
                  <label class="form-label text-muted small mb-1">Status</label>
                  <p class="mb-0">
                    <span :class="['badge', form.is_active ? 'bg-success' : 'bg-secondary']">
                      {{ form.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </p>
                </div>
              </div>
            </div>

            <form @submit.prevent="handleSubmit">
              <!-- Basic Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-info-circle me-2"></i>Basic Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-8">
                    <BaseInput v-model="form.name" label="Institution Name" type="text" :required="true" />
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model="form.short_name" label="Short Name" type="text" />
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model="form.code" label="Institution Code" type="text" :required="true" />
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model.number="form.established_year" label="Established Year" type="number" />
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model="form.website" label="Website" type="url" />
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
                    <BaseInput v-model="form.email" label="Email" type="email" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.phone" label="Phone" type="tel" />
                  </div>
                </div>
              </div>

              <!-- Address Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-geo-alt me-2"></i>Address Information
                </h6>
                <div class="row g-3">
                  <div class="col-12">
                    <div class="mb-3">
                      <label class="form-label">Full Address</label>
                      <textarea v-model="form.address" class="form-control" rows="2"></textarea>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model="form.city" label="City" type="text" />
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model="form.state" label="State/Province" type="text" />
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model="form.postal_code" label="Postal Code" type="text" />
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Country</label>
                      <select v-model="form.country" class="form-select">
                        <option value="Pakistan">Pakistan</option>
                        <option value="India">India</option>
                        <option value="Bangladesh">Bangladesh</option>
                        <option value="United States">United States</option>
                        <option value="United Kingdom">United Kingdom</option>
                        <option value="Canada">Canada</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-text-paragraph me-2"></i>Description
                </h6>
                <textarea v-model="form.description" class="form-control" rows="4"></textarea>
              </div>

              <!-- Status -->
              <div class="mb-4">
                <div class="form-check form-switch">
                  <input v-model="form.is_active" class="form-check-input" type="checkbox" id="isActive">
                  <label class="form-check-label" for="isActive">Active Institution</label>
                </div>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-outline-secondary px-4" :disabled="submitting">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
                  <span v-if="submitting">
                    <span class="spinner-border spinner-border-sm me-2"></span>Updating...
                  </span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Update Institution</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { institutionService } from '@/services/institutionService'

const router = useRouter()
const route = useRoute()
const institutionId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Institutions', href: '/admin-dashboard/institution' },
  { name: 'Edit Institution' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-outline-secondary', onClick: () => router.push('/admin-dashboard/institution') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(true)
const submitting = ref(false)

const form = ref({
  name: '',
  short_name: '',
  code: '',
  established_year: null,
  website: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  postal_code: '',
  country: 'Pakistan',
  description: '',
  is_active: true
})

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadInstitution = async () => {
  loading.value = true
  try {
    const inst = await institutionService.getInstitutionById(institutionId)
    form.value = {
      name: inst.name || '',
      short_name: inst.short_name || '',
      code: inst.code || '',
      established_year: inst.established_year || null,
      website: inst.website || '',
      email: inst.email || '',
      phone: inst.phone || '',
      address: inst.address || '',
      city: inst.city || '',
      state: inst.state || '',
      postal_code: inst.postal_code || '',
      country: inst.country || 'Pakistan',
      description: inst.description || '',
      is_active: inst.is_active !== false
    }
  } catch (error) {
    console.error('Error loading institution:', error)
    showAlert('error', 'Failed to load institution', 'Error')
    setTimeout(() => router.push('/admin-dashboard/institution'), 2000)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    // Clean empty fields
    Object.keys(data).forEach(key => {
      if (data[key] === '' || data[key] === null) {
        if (key !== 'is_active') delete data[key]
      }
    })
    
    await institutionService.updateInstitution(institutionId, data)
    showAlert('success', 'Institution updated successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/institution'), 1500)
  } catch (error) {
    console.error('Error updating institution:', error)
    const msg = error.response?.data?.detail || 'Failed to update institution.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  router.push('/admin-dashboard/institution')
}

onMounted(() => {
  if (institutionId) loadInstitution()
  else loading.value = false
})
</script>

<style scoped>
.form-control:focus, .form-select:focus { 
  border-color: #0d6efd; 
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.15); 
}
.card { border-radius: 12px; }
.card-header { 
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.05) 0%, rgba(13, 110, 253, 0.02) 100%); 
}
.avatar-circle-lg { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
</style>
