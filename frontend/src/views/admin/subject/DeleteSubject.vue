<template>
  <AdminPageTemplate
    title="Delete Subject"
    subtitle="Permanently remove subject record"
    icon="bi bi-book-x"
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
      <p class="text-muted mt-3">Loading subject details...</p>
    </div>

    <div v-else-if="!subjectId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-book-x display-4"></i>
      </div>
      <h4 class="text-muted">No Subject Selected</h4>
      <p class="text-muted mb-4">Please select a subject from the list to delete.</p>
      <button @click="router.push('/admin-dashboard/subjects')" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Subject List
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
              <h4 class="fw-bold text-danger mb-2">Delete Subject?</h4>
              <p class="text-muted mb-0">
                This will permanently delete the subject and all associated assignments, enrollments, and attendance records.
              </p>
            </div>

            <div class="subject-info-card bg-light p-3 rounded-3 mb-4 text-start">
              <div class="d-flex align-items-center mb-2">
                <span class="text-muted small me-2">Code:</span>
                <span class="badge bg-dark">{{ subject.code }}</span>
              </div>
              <div class="d-flex align-items-center mb-2">
                <span class="text-muted small me-2">Name:</span>
                <span class="fw-semibold">{{ subject.name }}</span>
              </div>
              <div class="d-flex align-items-center">
                <span class="text-muted small me-2">Credits:</span>
                <span class="fw-semibold">{{ subject.credit_hours }} hours</span>
              </div>
            </div>

            <div class="alert alert-warning border-0 d-flex align-items-start text-start mb-4">
              <i class="bi bi-info-circle-fill me-2 mt-1"></i>
              <small>Please type <strong>DELETE</strong> in the box below to confirm.</small>
            </div>

            <div class="mb-4">
              <input v-model="confirmationText" type="text" class="form-control text-center" placeholder="Type DELETE to confirm" @keyup.enter="handleDelete">
            </div>

            <div class="d-flex gap-2 justify-content-center">
              <button @click="handleCancel" class="btn btn-light px-4" :disabled="submitting">Cancel</button>
              <button @click="handleDelete" class="btn btn-danger px-4" :disabled="submitting || confirmationText !== 'DELETE'">
                <span v-if="submitting"><span class="spinner-border spinner-border-sm me-2"></span>Deleting...</span>
                <span v-else>Delete Subject</span>
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
import { subjectService } from '@/services/subjectService'

const router = useRouter()
const route = useRoute()
const subjectId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Subjects', href: '/admin-dashboard/subjects' },
  { name: 'Delete Subject' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/subjects') }
]

const loading = ref(true)
const submitting = ref(false)
const confirmationText = ref('')
const subject = ref({})
const alert = ref({ show: false, type: 'success', title: '', message: '' })

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadSubject = async () => {
  loading.value = true
  try {
    subject.value = await subjectService.getSubjectById(subjectId)
  } catch (error) {
    console.error('Error loading subject:', error)
    showAlert('error', 'Failed to load subject details', 'Error')
    setTimeout(() => router.push('/admin-dashboard/subjects'), 2000)
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  if (confirmationText.value !== 'DELETE') return
  
  submitting.value = true
  try {
    await subjectService.deleteSubject(subjectId)
    showAlert('success', 'Subject deleted successfully', 'Success')
    setTimeout(() => router.push('/admin-dashboard/subjects'), 1500)
  } catch (error) {
    console.error('Error deleting subject:', error)
    showAlert('error', 'Failed to delete subject', 'Error')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => router.push('/admin-dashboard/subjects')

onMounted(() => {
  if (subjectId) loadSubject()
})
</script>


