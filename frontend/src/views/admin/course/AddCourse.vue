<template>
  <AdminPageTemplate
    title="Add New Course"
    subtitle="Create a new academic program/course"
    icon="bi bi-mortarboard-fill"
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
              <i class="bi bi-mortarboard me-2 text-admin"></i>
              Course Information
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
                      label="Course Name"
                      type="text"
                      placeholder="e.g., Bachelor of Computer Science"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-4">
                    <BaseInput
                      v-model="form.code"
                      label="Course Code"
                      type="text"
                      placeholder="e.g., BSCS"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Department <span class="text-danger">*</span></label>
                      <select v-model="form.department" class="form-select" required>
                        <option value="">Select Department</option>
                        <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                          {{ dept.name }} ({{ dept.code }})
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model.number="form.duration_years"
                      label="Duration (Years)"
                      type="number"
                      placeholder="4"
                      :required="true"
                    />
                  </div>
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-text-paragraph me-2"></i>Description
                </h6>
                <textarea 
                  v-model="form.description" 
                  class="form-control" 
                  rows="4" 
                  placeholder="Enter course description, objectives, career opportunities..."
                ></textarea>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-admin-outline px-4" :disabled="submitting">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
                  <span v-if="submitting">
                    <span class="spinner-border spinner-border-sm me-2"></span>Adding...
                  </span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Add Course</span>
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
import { programService } from '@/services/programService'
import api from '@/services/api'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Courses', href: '/admin-dashboard/courses' },
  { name: 'Add Course' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/courses') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const submitting = ref(false)
const departments = ref([])

const form = ref({
  name: '',
  code: '',
  department: '',
  duration_years: 4,
  description: ''
})

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadDepartments = async () => {
  try {
    const response = await api.get('/departments/')
    departments.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.department) delete data.department
    
    await programService.createProgram(data)
    showAlert('success', 'Course has been added successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/courses'), 1500)
  } catch (error) {
    console.error('Error adding course:', error)
    const msg = error.response?.data?.detail || error.response?.data?.code?.[0] || 'Failed to add course.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  const hasData = Object.values(form.value).some(val => val !== '' && val !== 4)
  if (hasData) {
    if (confirm('Are you sure? All unsaved changes will be lost.')) {
      router.push('/admin-dashboard/courses')
    }
  } else {
    router.push('/admin-dashboard/courses')
  }
}

onMounted(() => {
  loadDepartments()
})
</script>


