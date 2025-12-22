<template>
  <AdminPageTemplate
    title="Delete Institution"
    subtitle="Permanently remove an institution from the system"
    icon="bi bi-trash"
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
      <p class="text-muted mt-3">Loading institution details...</p>
    </div>

    <div v-else-if="!institutionId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-bank2 display-4"></i>
      </div>
      <h4 class="text-muted">No Institution Selected</h4>
      <p class="text-muted mb-4">Please select an institution from the list to delete.</p>
      <button @click="router.push('/admin-dashboard/institution')" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Institution List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm border-danger">
          <div class="card-header bg-danger text-white">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-exclamation-triangle me-2"></i>
              Confirm Deletion
            </h5>
          </div>
          <div class="card-body p-4">
            <!-- Warning Message -->
            <div class="alert alert-danger mb-4">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              <strong>Warning!</strong> This action cannot be undone. Deleting this institution will also remove all associated departments and related data.
            </div>

            <!-- Institution Details -->
            <div class="mb-4 p-4 bg-light rounded">
              <h6 class="text-dark fw-semibold mb-3">Institution to be deleted:</h6>
              <div class="row">
                <div class="col-md-6">
                  <p class="mb-2"><strong>Name:</strong> {{ institution.name }}</p>
                  <p class="mb-2"><strong>Code:</strong> {{ institution.code }}</p>
                  <p class="mb-2"><strong>Short Name:</strong> {{ institution.short_name || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <p class="mb-2"><strong>City:</strong> {{ institution.city || '-' }}</p>
                  <p class="mb-2"><strong>Email:</strong> {{ institution.email || '-' }}</p>
                  <p class="mb-2"><strong>Status:</strong> 
                    <span :class="['badge', institution.is_active ? 'bg-success' : 'bg-secondary']">
                      {{ institution.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </p>
                </div>
              </div>
            </div>

            <!-- Confirmation Input -->
            <div class="mb-4">
              <label class="form-label fw-semibold">
                To confirm deletion, type <code>DELETE</code> below:
              </label>
              <input 
                v-model="confirmText" 
                type="text" 
                class="form-control" 
                placeholder="Type DELETE to confirm"
                @keyup.enter="handleDelete"
              >
            </div>

            <!-- Actions -->
            <div class="d-flex gap-3 justify-content-end pt-3 border-top">
              <button @click="handleCancel" class="btn btn-secondary px-4" :disabled="deleting">
                <i class="bi bi-x-circle me-2"></i>Cancel
              </button>
              <button 
                @click="handleDelete" 
                class="btn btn-danger px-4" 
                :disabled="confirmText !== 'DELETE' || deleting"
              >
                <span v-if="deleting">
                  <span class="spinner-border spinner-border-sm me-2"></span>Deleting...
                </span>
                <span v-else><i class="bi bi-trash me-2"></i>Delete Institution</span>
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
import { institutionService } from '@/services/institutionService'

const router = useRouter()
const route = useRoute()
const institutionId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Institutions', href: '/admin-dashboard/institution' },
  { name: 'Delete Institution' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-outline-secondary', onClick: () => router.push('/admin-dashboard/institution') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(true)
const deleting = ref(false)
const confirmText = ref('')
const institution = ref({})

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadInstitution = async () => {
  loading.value = true
  try {
    institution.value = await institutionService.getInstitutionById(institutionId)
  } catch (error) {
    console.error('Error loading institution:', error)
    showAlert('error', 'Failed to load institution', 'Error')
    setTimeout(() => router.push('/admin-dashboard/institution'), 2000)
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  if (confirmText.value !== 'DELETE') return
  
  deleting.value = true
  try {
    await institutionService.deleteInstitution(institutionId)
    showAlert('success', 'Institution has been deleted successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/institution'), 1500)
  } catch (error) {
    console.error('Error deleting institution:', error)
    const msg = error.response?.data?.detail || 'Failed to delete institution.'
    showAlert('error', msg, 'Error!')
  } finally {
    deleting.value = false
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


