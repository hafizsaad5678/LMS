<template>
  <TeacherPageTemplate
    title="Create Assignment"
    subtitle="Add a new assignment for your students"
    icon="bi bi-file-earmark-plus"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Discard Changes?"
      message="All unsaved changes will be lost. Are you sure?"
      type="warning"
      theme="teacher"
      confirm-text="Discard"
      @confirm="confirmCancel"
    />

    <AlertMessage
      v-if="alert.show"
      v-bind="alert"
      :auto-close="true"
      @close="clearAlert"
    />

    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-file-earmark-text me-2 text-teacher"></i>Assignment Details
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="submitForm">
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom"><i class="bi bi-info-circle me-2"></i>Basic Information</h6>
                <div class="row g-3">
                  <div class="col-12">
                    <BaseInput v-model="form.title" label="Assignment Title" placeholder="e.g., Week 1 Quiz" required />
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label fw-semibold">Subject *</label>
                      <select v-model="form.subject" class="form-select border-0 shadow-sm p-3 bg-light" required>
                        <option value="">Select Subject/Class</option>
                        <option v-for="subj in subjects" :key="subj.id" :value="subj.subject_id">{{ subj.subject_name }} ({{ subj.subject_code }})</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model.number="form.total_marks" label="Total Marks" type="number" required />
                  </div>
                </div>
              </div>

              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom"><i class="bi bi-calendar-event me-2"></i>Deadline & Instructions</h6>
                <div class="row g-3">
                  <div class="col-12">
                    <BaseInput v-model="form.due_date" label="Due Date & Time" type="datetime-local" required />
                  </div>
                  <div class="col-12">
                    <RichTextEditor v-model="form.description" placeholder="Provide detailed instructions for the students..." />
                  </div>
                </div>
              </div>

              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-teacher-outline px-4" :disabled="submitting"><i class="bi bi-x-circle me-2"></i>Cancel</button>
                <button type="submit" class="btn btn-teacher-primary px-4" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-circle me-2"></i>Create Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { BaseInput, AlertMessage, ConfirmDialog, RichTextEditor } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { cacheService } from '@/services/shared'
import { useAlert, useFormSubmit, createForm } from '@/composables/shared'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const { alert, showSuccess, showError, clearAlert } = useAlert()
const { submitting, handleSubmit } = useFormSubmit()
const form = createForm('assignment')

const subjects = ref([])
const showConfirmDialog = ref(false)

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: TEACHER_ROUTES.ASSIGNMENT_LIST.path },
  { name: 'Create' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-teacher-outline', onClick: () => router.push(TEACHER_ROUTES.ASSIGNMENT_LIST.path) }
]

const loadSubjects = async () => {
  try {
    const response = await teacherPanelService.getMyClasses()
    subjects.value = response.results || response || []
  } catch (error) {
    console.error('Error loading subjects:', error)
  }
}

const submitForm = () => {
  handleSubmit(async () => {
    await teacherPanelService.createAssignment({ ...form.value, total_marks: Number(form.value.total_marks) })
    cacheService.clearPattern('teacher_assignments')
    showSuccess('Assignment created successfully!')
    setTimeout(() => router.push(TEACHER_ROUTES.ASSIGNMENT_LIST.path), 1500)
  }, null, (error) => {
    const errorData = error.response?.data
    const msg = typeof errorData === 'object' ? Object.entries(errorData).map(([k, v]) => `${k}: ${v}`).join('\n') : errorData || 'Failed to create assignment.'
    showError(msg)
  })
}

const handleCancel = () => {
  if (form.value.title || form.value.description) showConfirmDialog.value = true
  else router.push(TEACHER_ROUTES.ASSIGNMENT_LIST.path)
}

const confirmCancel = () => router.push(TEACHER_ROUTES.ASSIGNMENT_LIST.path)

onMounted(loadSubjects)
</script>
