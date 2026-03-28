<template>
  <AdminPageTemplate
    title="Edit Semester"
    subtitle="Update semester details"
    icon="bi bi-pencil-square"
    :breadcrumbs="breadcrumbs"
  >
    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Discard Changes"
      message="Are you sure? All unsaved changes will be lost."
      type="warning"
      theme="admin"
      confirm-text="Discard"
      @confirm="confirmCancel"
    />

    <div class="row justify-content-center">
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-light border-bottom px-4 py-3">
            <h5 class="card-title mb-0">Semester Information</h5>
          </div>
          <div class="card-body p-4">
            <AlertMessage
              v-if="alert.show"
              :type="alert.type"
              :message="alert.message"
              :title="alert.title"
              :auto-close="true"
              :auto-close-duration="3000"
              @close="alert.show = false"
            />
            <LoadingSpinner v-if="loading" theme="admin" />
            <form v-else @submit.prevent="submitForm">
              <div class="mb-3">
                <label for="program-select" class="form-label">Program <span class="text-danger">*</span></label>
                <select id="program-select" v-model="form.program" class="form-select" required>
                  <option value="" disabled>Select Program</option>
                  <option v-for="p in programs" :key="p.id" :value="String(p.id)">{{ p.name }}</option>
                </select>
              </div>

              <div class="mb-3">
                <label for="semester-name" class="form-label">Semester Name <span class="text-danger">*</span></label>
                <input id="semester-name" v-model="form.name" type="text" class="form-control" placeholder="e.g. Fall 2023" required>
              </div>

              <div class="mb-3">
                <label for="semester-number" class="form-label">Semester Number <span class="text-danger">*</span></label>
                <input id="semester-number" v-model.number="form.number" type="number" class="form-control" required min="1">
              </div>

              <div class="row">
                <div class="col-md-6">
                  <BaseInput v-model="form.start_date" label="Start Date" type="date" />
                </div>
                <div class="col-md-6">
                  <BaseInput v-model="form.end_date" label="End Date" type="date" />
                </div>
              </div>

              <div class="mb-3">
                <SelectInput
                  v-model="form.status"
                  :options="SEMESTER_STATUS_OPTIONS"
                  label="Status"
                  placeholder="Select status"
                />
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" @click="handleCancel" class="btn btn-light">Cancel</button>
                <button type="submit" class="btn btn-admin-primary" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  <span v-if="!submitting"><i class="bi bi-check-circle me-2"></i></span>
                  Update Semester
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
import { BaseInput, AlertMessage, ConfirmDialog, LoadingSpinner, BaseButton, SelectInput } from '@/components/shared/common'
import { semesterService, programService, cacheService } from '@/services/shared'
import { api } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { SEMESTER_STATUS_OPTIONS } from '@/utils/constants/options'

const router = useRouter()
const route = useRoute()
const semesterId = computed(() => route.params.id)
const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Semesters', href: ADMIN_ROUTES.SEMESTER_LIST.path },
  { name: 'Edit' }
]

const loading = ref(true)
const submitting = ref(false)
const programs = ref([])
const { alert, showAlert } = useAlert()
const showConfirmDialog = ref(false)

const form = ref({
  program: '',
  name: '',
  number: 1,
  start_date: '',
  end_date: '',
  status: 'draft'
})


const loadSemester = async () => {
  const id = semesterId.value
  if (!id) {
    loading.value = false
    return
  }
  
  loading.value = true
  try {
    const [sem, progRes] = await Promise.all([
      semesterService.getById(id),
      api.get('/programs/')
    ])
    
    programs.value = Array.isArray(progRes.data) ? progRes.data : (progRes.data.results || progRes.data)
    
    // Assign each field individually to ensure reactivity
    // Extract program ID - it can be an object or a string/UUID
    form.value.program = sem.program ? (typeof sem.program === 'object' ? String(sem.program.id) : String(sem.program)) : ''
    form.value.name = sem.name || ''
    form.value.number = sem.number || 1
    form.value.start_date = sem.start_date || ''
    form.value.end_date = sem.end_date || ''
    form.value.status = sem.status || 'draft'
  } catch (e) {
    console.error('Error loading semester:', e)
    showAlert('error', 'Failed to load semester details', 'Error')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.SEMESTER_LIST.name }), 2000)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadSemester()
})

const handleCancel = () => {
  showConfirmDialog.value = true
}

const confirmCancel = () => {
  showConfirmDialog.value = false
  router.back()
}

const submitForm = async () => {
  submitting.value = true
  try {
    if (!form.value.program || !form.value.name) {
      showAlert('error', 'Please fill in all required fields', 'Validation Error')
      submitting.value = false
      return
    }

    await semesterService.update(semesterId.value, form.value)
    
    // Clear cache to ensure list refreshes with updated data
    cacheService.clear('semesters_list')
    cacheService.clearPattern('semester')
    
    showAlert('success', 'Semester updated successfully!', 'Success!')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.SEMESTER_LIST.name }), 1500)
  } catch (e) {
    console.error('Error updating semester:', e.response?.data || e.message)
    const msg = e.response?.data?.detail || e.response?.data?.non_field_errors?.[0] || 'Failed to update semester'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

// Watch for route param changes to reload data
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadSemester()
  }
}, { immediate: false })
</script>


