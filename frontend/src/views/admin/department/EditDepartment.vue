<template>
  <AdminPageTemplate
    title="Edit Department"
    subtitle="Update department information"
    icon="bi bi-building-gear"
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
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading department details...</p>
    </div>

    <div v-else-if="!departmentId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-building display-4"></i>
      </div>
      <h4 class="text-muted">No Department Selected</h4>
      <p class="text-muted mb-4">Please select a department from the list to edit.</p>
      <button @click="router.push('/admin-dashboard/departments')" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Department List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-building me-2 text-admin"></i>
              Department Information
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit">
              <!-- Basic Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-info-circle me-2"></i>Basic Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-8">
                    <BaseInput
                      v-model="form.name"
                      label="Department Name"
                      type="text"
                      placeholder="e.g., Computer Science"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-4">
                    <BaseInput
                      v-model="form.code"
                      label="Department Code"
                      type="text"
                      placeholder="e.g., CS"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Institution</label>
                      <select v-model="form.institution" class="form-select">
                        <option value="">Select Institution</option>
                        <option v-for="inst in institutions" :key="inst.id" :value="inst.id">
                          {{ inst.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model="form.head_of_department"
                      label="Head of Department"
                      type="text"
                      placeholder="e.g., Dr. John Smith"
                    />
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
                    <BaseInput v-model="form.email" label="Email" type="email" placeholder="department@university.edu" />
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model="form.phone" label="Phone" type="tel" placeholder="+92 000-0000000" />
                  </div>
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-text-paragraph me-2"></i>Description
                </h6>
                <textarea v-model="form.description" class="form-control" rows="4" placeholder="Enter description..."></textarea>
              </div>

              <!-- Status -->
              <div class="mb-4">
                <div class="form-check form-switch">
                  <input v-model="form.is_active" class="form-check-input" type="checkbox" id="isActive">
                  <label class="form-check-label" for="isActive">Active Department</label>
                </div>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-admin-outline px-4" :disabled="submitting">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
                  <span v-if="submitting">
                    <span class="spinner-border spinner-border-sm me-2"></span>Updating...
                  </span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Update Department</span>
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
import { departmentService } from '@/services/departmentService'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const departmentId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Departments', href: '/admin-dashboard/departments' },
  { name: 'Edit Department' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/departments') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(true)
const submitting = ref(false)
const institutions = ref([])

const form = ref({
  name: '', code: '', institution: '', head_of_department: '', email: '', phone: '', description: '', is_active: true
})

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadInstitutions = async () => {
  try {
    const response = await api.get('/institutions/')
    institutions.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading institutions:', error)
  }
}

const loadDepartment = async () => {
  loading.value = true
  try {
    const dept = await departmentService.getDepartmentById(departmentId)
    form.value = {
      name: dept.name || '',
      code: dept.code || '',
      institution: dept.institution || '',
      head_of_department: dept.head_of_department || '',
      email: dept.email || '',
      phone: dept.phone || '',
      description: dept.description || '',
      is_active: dept.is_active !== false
    }
  } catch (error) {
    console.error('Error loading department:', error)
    showAlert('error', 'Failed to load department', 'Error')
    setTimeout(() => router.push('/admin-dashboard/departments'), 2000)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.institution) delete data.institution
    
    await departmentService.updateDepartment(departmentId, data)
    showAlert('success', 'Department updated successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/departments'), 1500)
  } catch (error) {
    console.error('Error updating department:', error)
    const msg = error.response?.data?.detail || 'Failed to update department.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => router.push('/admin-dashboard/departments')

onMounted(() => {
  loadInstitutions()
  if (departmentId) loadDepartment()
})
</script>


