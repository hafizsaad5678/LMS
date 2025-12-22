<template>
  <AdminPageTemplate
    title="Delete Department"
    subtitle="Permanently remove department record"
    icon="bi bi-building-x"
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
        <i class="bi bi-building-x display-4"></i>
      </div>
      <h4 class="text-muted">No Department Selected</h4>
      <p class="text-muted mb-4">Please select a department from the list to delete.</p>
      <button @click="router.push('/admin-dashboard/departments')" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Department List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm border-top-danger">
          <div class="card-body p-4 text-center">
            <div class="mb-4">
              <div class="avatar-circle-lg mx-auto mb-3">
                <i class="bi bi-exclamation-triangle-fill"></i>
              </div>
              <h4 class="fw-bold text-danger mb-2">Delete Department?</h4>
              <p class="text-muted mb-0">
                This action cannot be undone. This will permanently delete the department and may affect associated programs and teachers.
              </p>
            </div>

            <div class="department-info-card bg-light p-3 rounded-3 mb-4 text-start">
              <div class="d-flex align-items-center mb-2">
                <span class="text-muted small me-2">Code:</span>
                <span class="fw-semibold">{{ department.code }}</span>
              </div>
              <div class="d-flex align-items-center mb-2">
                <span class="text-muted small me-2">Name:</span>
                <span class="fw-semibold">{{ department.name }}</span>
              </div>
              <div class="d-flex align-items-center">
                <span class="text-muted small me-2">Head:</span>
                <span class="fw-semibold">{{ department.head_of_department || 'Not Assigned' }}</span>
              </div>
            </div>

            <div class="alert alert-warning border-0 d-flex align-items-start text-start mb-4">
              <i class="bi bi-info-circle-fill me-2 mt-1"></i>
              <small>Please type <strong>DELETE</strong> in the box below to confirm.</small>
            </div>

            <div class="mb-4">
              <input 
                v-model="confirmationText"
                type="text" 
                class="form-control text-center" 
                placeholder="Type DELETE to confirm"
                @keyup.enter="handleDelete"
              >
            </div>

            <div class="d-flex gap-2 justify-content-center">
              <button @click="handleCancel" class="btn btn-light px-4" :disabled="submitting">Cancel</button>
              <button 
                @click="handleDelete" 
                class="btn btn-danger px-4"
                :disabled="submitting || confirmationText !== 'DELETE'"
              >
                <span v-if="submitting">
                  <span class="spinner-border spinner-border-sm me-2"></span>Deleting...
                </span>
                <span v-else>Delete Department</span>
              </button>
            </div>
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
import AlertMessage from '@/components/common/AlertMessage.vue'
import { departmentService } from '@/services/departmentService'

const router = useRouter()
const route = useRoute()
const departmentId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Departments', href: '/admin-dashboard/departments' },
  { name: 'Delete Department' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/departments') }
]

const loading = ref(true)
const submitting = ref(false)
const confirmationText = ref('')
const department = ref({})
const alert = ref({ show: false, type: 'success', title: '', message: '' })

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadDepartment = async () => {
  loading.value = true
  try {
    department.value = await departmentService.getDepartmentById(departmentId)
  } catch (error) {
    console.error('Error loading department:', error)
    showAlert('error', 'Failed to load department details', 'Error')
    setTimeout(() => router.push('/admin-dashboard/departments'), 2000)
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  if (confirmationText.value !== 'DELETE') return
  
  submitting.value = true
  try {
    await departmentService.deleteDepartment(departmentId)
    showAlert('success', 'Department deleted successfully', 'Success')
    setTimeout(() => router.push('/admin-dashboard/departments'), 1500)
  } catch (error) {
    console.error('Error deleting department:', error)
    showAlert('error', 'Failed to delete department', 'Error')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => router.push('/admin-dashboard/departments')

onMounted(() => {
  if (departmentId) loadDepartment()
})
</script>


