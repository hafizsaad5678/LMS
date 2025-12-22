<template>
  <AdminPageTemplate
    title="Add New Department"
    subtitle="Create a new academic department"
    icon="bi bi-building-add"
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

    <div class="row justify-content-center">
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
                    <BaseInput
                      v-model="form.email"
                      label="Email"
                      type="email"
                      placeholder="department@university.edu"
                    />
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model="form.phone"
                      label="Phone"
                      type="tel"
                      placeholder="+92 000-0000000"
                    />
                  </div>
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-text-paragraph me-2"></i>Description
                </h6>
                <div class="mb-3">
                  <textarea 
                    v-model="form.description" 
                    class="form-control" 
                    rows="4" 
                    placeholder="Enter department description..."
                  ></textarea>
                </div>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button 
                  type="button" 
                  @click="handleCancel" 
                  class="btn btn-admin-outline px-4"
                  :disabled="submitting"
                >
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button 
                  type="submit" 
                  class="btn btn-admin-primary px-4"
                  :disabled="submitting"
                >
                  <span v-if="submitting">
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Adding...
                  </span>
                  <span v-else>
                    <i class="bi bi-check-circle me-2"></i>Add Department
                  </span>
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
import { useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { departmentService } from '@/services/departmentService'
import api from '@/services/api'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Departments', href: '/admin-dashboard/departments' },
  { name: 'Add Department' }
]

const actions = [
  {
    label: 'Back to List',
    icon: 'bi bi-arrow-left',
    variant: 'btn-admin-outline',
    onClick: () => router.push('/admin-dashboard/departments')
  }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const submitting = ref(false)
const institutions = ref([])

const form = ref({
  name: '',
  code: '',
  institution: '',
  head_of_department: '',
  email: '',
  phone: '',
  description: ''
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

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.institution) delete data.institution
    
    await departmentService.createDepartment(data)
    showAlert('success', 'Department has been added successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/departments'), 1500)
  } catch (error) {
    console.error('Error adding department:', error)
    const msg = error.response?.data?.detail || error.response?.data?.message || 'Failed to add department.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  const hasData = Object.values(form.value).some(val => val !== '')
  if (hasData) {
    if (confirm('Are you sure? All unsaved changes will be lost.')) {
      router.push('/admin-dashboard/departments')
    }
  } else {
    router.push('/admin-dashboard/departments')
  }
}

onMounted(() => {
  loadInstitutions()
})
</script>


