<template>
  <AdminPageTemplate
    title="Create Assignment"
    subtitle="Create a new assignment for students"
    icon="bi bi-file-earmark-plus"
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
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-file-earmark-text me-2 text-admin"></i>
              Assignment Details
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
                  <div class="col-12">
                    <BaseInput
                      v-model="form.title"
                      label="Assignment Title"
                      type="text"
                      placeholder="e.g., Data Structures Lab 1"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Subject <span class="text-danger">*</span></label>
                      <select v-model="form.subject" class="form-select" required>
                        <option value="">Select Subject</option>
                        <option v-for="subj in subjects" :key="subj.id" :value="subj.id">
                          {{ subj.code }} - {{ subj.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Created By (Teacher)</label>
                      <select v-model="form.created_by" class="form-select">
                        <option value="">Select Teacher</option>
                        <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                          {{ teacher.full_name }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Assignment Settings -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-gear me-2"></i>Assignment Settings
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <BaseInput
                      v-model="form.due_date"
                      label="Due Date & Time"
                      type="date"
                      :enable-time-picker="true"
                      :required="true"
                    />
                  </div>
                  <div class="col-md-6">
                    <BaseInput
                      v-model.number="form.total_marks"
                      label="Total Marks"
                      type="number"
                      placeholder="100"
                      :required="true"
                    />
                  </div>
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-text-paragraph me-2"></i>Description & Instructions
                </h6>
                <textarea 
                  v-model="form.description" 
                  class="form-control" 
                  rows="5" 
                  placeholder="Enter detailed assignment description, requirements, and submission guidelines..."
                  required
                ></textarea>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-admin-outline px-4" :disabled="submitting">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
                  <span v-if="submitting">
                    <span class="spinner-border spinner-border-sm me-2"></span>Creating...
                  </span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Create Assignment</span>
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
import { AdminPageTemplate } from '@/components/shared/panels'
import { BaseInput, AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { assignmentService, subjectService, teacherService, cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: ADMIN_ROUTES.ASSIGNMENTS.path },
  { name: 'Create Assignment' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.ASSIGNMENTS.path) }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const submitting = ref(false)
const subjects = ref([])
const teachers = ref([])
const showConfirmDialog = ref(false)

const form = ref({
  title: '',
  description: '',
  subject: '',
  created_by: '',
  due_date: '',
  total_marks: 100
})

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadSubjects = async () => {
  try {
    const response = await subjectService.getAllSubjects()
    subjects.value = Array.isArray(response) ? response : (response.results || [])
  } catch (error) {
    // Silent fail - subjects dropdown will be empty
  }
}

const loadTeachers = async () => {
  try {
    const response = await teacherService.getAllTeachers()
    teachers.value = Array.isArray(response) ? response : (response.results || [])
  } catch (error) {
    // Silent fail - teachers dropdown will be empty
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.subject) delete data.subject
    if (!data.created_by) delete data.created_by
    
    await assignmentService.createAssignment(data)
    
    // Clear caches to update list view
    cacheService.clear('assignments_list')
    cacheService.clearPattern('assignment')
    
    showAlert('success', 'Assignment created successfully!', 'Success!')
    setTimeout(() => router.push(ADMIN_ROUTES.ASSIGNMENTS.path), 1500)
  } catch (error) {
    const msg = error.response?.data?.detail || 'Failed to create assignment.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  const hasData = form.value.title || form.value.description
  if (hasData) {
    showConfirmDialog.value = true
  } else {
    router.push(ADMIN_ROUTES.ASSIGNMENTS.path)
  }
}

const confirmCancel = () => {
  showConfirmDialog.value = false
  router.push(ADMIN_ROUTES.ASSIGNMENTS.path)
}

onMounted(() => {
  loadSubjects()
  loadTeachers()
})
</script>




