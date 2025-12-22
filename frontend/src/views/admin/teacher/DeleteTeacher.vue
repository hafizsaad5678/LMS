<template>
  <AdminPageTemplate
    title="Delete Teacher"
    subtitle="Permanently remove teacher record"
    icon="bi bi-person-x-fill"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- Alert Message -->
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
      <p class="text-muted mt-3">Loading teacher details...</p>
    </div>

    <!-- Default Screen when no ID selected -->
    <div v-if="!teacherId" class="text-center py-5">
      <div class="mb-4">
        <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
          <i class="bi bi-person-x display-4"></i>
        </div>
        <h4 class="text-muted">No Teacher Selected</h4>
        <p class="text-muted mb-4">Please select a teacher from the list to delete.</p>
        <button @click="router.push('/admin-dashboard/teachers')" class="btn btn-admin-primary">
          <i class="bi bi-list-ul me-2"></i>
          Go to Teacher List
        </button>
      </div>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm border-top-danger">
          <div class="card-body p-4 text-center">
            <div class="mb-4">
              <div class="avatar-circle-lg mx-auto mb-3">
                <i class="bi bi-exclamation-triangle-fill"></i>
              </div>
              <h4 class="fw-bold text-danger mb-2">Delete Teacher Account?</h4>
              <p class="text-muted mb-0">
                This action cannot be undone. This will permanently delete the teacher account and remove all associated data.
              </p>
            </div>

            <div class="teacher-info-card bg-light p-3 rounded-3 mb-4 text-start">
              <div class="d-flex align-items-center mb-2">
                <span class="text-muted small me-2">Employee ID:</span>
                <span class="fw-semibold">{{ teacher.employee_id }}</span>
              </div>
              <div class="d-flex align-items-center mb-2">
                <span class="text-muted small me-2">Name:</span>
                <span class="fw-semibold">{{ teacher.full_name }}</span>
              </div>
              <div class="d-flex align-items-center mb-2">
                <span class="text-muted small me-2">Department:</span>
                <span class="fw-semibold">{{ teacher.department }}</span>
              </div>
              <div class="d-flex align-items-center">
                <span class="text-muted small me-2">Email:</span>
                <span class="fw-semibold">{{ teacher.email }}</span>
              </div>
            </div>

            <div class="alert alert-warning border-0 d-flex align-items-start text-start mb-4">
              <i class="bi bi-info-circle-fill me-2 mt-1"></i>
              <small>
                Please type <strong>DELETE</strong> in the box below to confirm.
              </small>
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
              <button 
                @click="handleCancel" 
                class="btn btn-light px-4"
                :disabled="submitting"
              >
                Cancel
              </button>
              <button 
                @click="handleDelete" 
                class="btn btn-danger px-4"
                :disabled="submitting || confirmationText !== 'DELETE'"
              >
                <span v-if="submitting">
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  Deleting...
                </span>
                <span v-else>
                  Delete Teacher
                </span>
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
import { teacherService } from '@/services/teacherService'

const router = useRouter()
const route = useRoute()
const teacherId = route.params.id

// Breadcrumbs
const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Teachers', href: '/admin-dashboard/teachers' },
  { name: 'Delete Teacher' }
]

// Action buttons
const actions = [
  {
    label: 'Back to List',
    icon: 'bi bi-arrow-left',
    variant: 'btn-admin-outline',
    onClick: () => router.push('/admin-dashboard/teachers')
  }
]

// State
const loading = ref(true)
const submitting = ref(false)
const confirmationText = ref('')
const teacher = ref({})
const alert = ref({
  show: false,
  type: 'success',
  title: '',
  message: ''
})

// Methods
const showAlert = (type, message, title = null) => {
  alert.value = {
    show: true,
    type,
    title,
    message
  }
}

const loadTeacher = async () => {
  loading.value = true
  try {
    teacher.value = await teacherService.getTeacher(teacherId)
  } catch (error) {
    console.error('Error loading teacher:', error)
    showAlert('error', 'Failed to load teacher details', 'Error')
    setTimeout(() => router.push('/admin-dashboard/teachers'), 2000)
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  if (confirmationText.value !== 'DELETE') return
  
  submitting.value = true
  try {
    await teacherService.deleteTeacher(teacherId)
    showAlert('success', 'Teacher deleted successfully', 'Success')
    setTimeout(() => router.push('/admin-dashboard/teachers'), 1500)
  } catch (error) {
    console.error('Error deleting teacher:', error)
    showAlert('error', 'Failed to delete teacher', 'Error')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  router.push('/admin-dashboard/teachers')
}

// Lifecycle
onMounted(() => {
  if (teacherId) {
    loadTeacher()
  }
})
</script>


