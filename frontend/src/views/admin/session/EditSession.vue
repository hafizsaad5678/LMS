<template>
  <AdminPageTemplate
    title="Edit Academic Session"
    subtitle="Update session details"
    icon="bi bi-pencil-square"
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

    <!-- Loading State -->
    <LoadingSpinner v-if="loading && sessionId" text="Loading session data..." theme="admin" />

    <!-- No ID provided -->
    <div v-else-if="!sessionId" class="text-center py-5">
      <i class="bi bi-pencil-square display-1 text-muted"></i>
      <h4 class="text-muted mt-3">No Session Selected</h4>
      <p class="text-muted">Select a session from the list to edit.</p>
      <router-link :to="ADMIN_ROUTES.SESSION_LIST.path" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Go to Session List
      </router-link>
    </div>

    <!-- Edit Form -->
    <div v-else class="row justify-content-center">
      <div class="col-lg-10">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-calendar-event me-2 text-admin"></i>Session Information
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="updateSession">
              <!-- Program Info (Read-only) -->
              <div class="mb-4 p-3 bg-light rounded">
                <h6 class="text-admin fw-semibold mb-3">Program Information (Read-only)</h6>
                <div class="row">
                  <div class="col-md-4">
                    <label class="form-label text-muted small mb-1">Program</label>
                    <p class="fw-semibold mb-0">{{ session.program_name }}</p>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label text-muted small mb-1">Department</label>
                    <p class="fw-semibold mb-0">{{ session.department_name || 'N/A' }}</p>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label text-muted small mb-1">Total Semesters</label>
                    <p class="fw-semibold mb-0">{{ session.total_semesters }}</p>
                  </div>
                </div>
              </div>

              <!-- Basic Info -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-info-circle me-2"></i>Basic Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Session Name <span class="text-danger">*</span></label>
                    <input v-model="formData.session_name" type="text" class="form-control" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Session Code <span class="text-danger">*</span></label>
                    <input v-model="formData.session_code" type="text" class="form-control" required>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Start Year <span class="text-danger">*</span></label>
                    <input v-model.number="formData.start_year" type="number" class="form-control" required>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">End Year <span class="text-danger">*</span></label>
                    <input v-model.number="formData.end_year" type="number" class="form-control" required>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Total Capacity <span class="text-danger">*</span></label>
                    <input v-model.number="formData.total_capacity" type="number" class="form-control" min="1" required>
                    <small class="text-muted">Current: {{ session.current_enrollment || 0 }} enrolled</small>
                  </div>
                  <div class="col-md-4">
                    <SelectInput
                      v-model="formData.status"
                      :options="SESSION_STATUS_OPTIONS"
                      label="Status"
                      placeholder="Select status"
                    />
                  </div>
                  <div class="col-12">
                    <label class="form-label">Description</label>
                    <textarea v-model="formData.description" class="form-control" rows="2"></textarea>
                  </div>
                </div>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <router-link :to="ADMIN_ROUTES.SESSION_LIST.path" class="btn btn-admin-outline px-4">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </router-link>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="saving">
                  <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Updating...</span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Update Session</span>
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
import { ref, onMounted, watch, computed } from 'vue'
import { useAlert } from '@/composables/shared'
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, LoadingSpinner, SelectInput } from '@/components/shared/common'
import { sessionService, cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { SESSION_STATUS_OPTIONS } from '@/utils/constants/options'

const router = useRouter()
const route = useRoute()
const sessionId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Sessions', href: ADMIN_ROUTES.SESSION_LIST.path },
  { name: 'Edit Session' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.SESSION_LIST.name }) }
]

const loading = ref(true)
const saving = ref(false)
const { alert, showAlert } = useAlert()
const session = ref({})

const formData = ref({
  session_name: '',
  session_code: '',
  start_year: null,
  end_year: null,
  total_capacity: 0,
  status: 'upcoming',
  description: ''
})


const loadSession = async () => {
  const id = sessionId.value
  if (!id) {
    loading.value = false
    return
  }
  loading.value = true
  try {
    // sessionService.getSession already returns response.data
    const sessionData = await sessionService.getSession(id)
    session.value = sessionData

    // Assign each field individually to ensure reactivity
    formData.value.session_name = sessionData.session_name || ''
    formData.value.session_code = sessionData.session_code || ''
    formData.value.start_year = sessionData.start_year || null
    formData.value.end_year = sessionData.end_year || null
    formData.value.total_capacity = sessionData.total_capacity || 0
    formData.value.status = sessionData.status || 'upcoming'
    formData.value.description = sessionData.description || ''
  } catch (error) {
    console.error('Error loading session:', error)
    showAlert('error', 'Failed to load session data', 'Error!')
  } finally {
    loading.value = false
  }
}

const updateSession = async () => {
  saving.value = true
  try {
    const updateData = {
      session_name: formData.value.session_name,
      session_code: formData.value.session_code,
      start_year: formData.value.start_year,
      end_year: formData.value.end_year,
      total_semesters: session.value.total_semesters,
      total_capacity: formData.value.total_capacity,
      status: formData.value.status
    }
    
    if (formData.value.description) updateData.description = formData.value.description
    
    await sessionService.updateSession(sessionId.value, updateData)
    
    // Clear cache to ensure list refreshes with updated data
    cacheService.clear('sessions_list')
    cacheService.clearPattern('session')
    
    showAlert('success', 'Session updated successfully!', 'Success!')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.SESSION_LIST.name }), 1500)
  } catch (error) {
    console.error('Error updating session:', error)
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Failed to update session'
    showAlert('error', errorMsg, 'Error!')
  } finally {
    saving.value = false
  }
}

// Watch for route param changes to reload data
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadSession()
  }
}, { immediate: false })

onMounted(async () => {
  await loadSession()
})
</script>


