<template>
  <TeacherPageTemplate
    title="Edit Assignment"
    subtitle="Update assignment details and requirements"
    icon="bi bi-pencil-square"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <AlertMessage
      v-if="alert.show"
      v-bind="alert"
      :auto-close="true"
      @close="clearAlert"
    />

    <LoadingSpinner v-if="loading" text="Loading assignment details..." theme="teacher" />

    <div v-else class="row justify-content-center">
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
                    <BaseInput v-model="form.title" label="Assignment Title" required />
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
                    <RichTextEditor v-model="form.description" placeholder="Update assignment details..." />
                  </div>
                </div>
              </div>

              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="router.push(TEACHER_ROUTES.ASSIGNMENT_LIST.path)" class="btn btn-teacher-outline px-4" :disabled="submitting"><i class="bi bi-x-circle me-2"></i>Cancel</button>
                <button type="submit" class="btn btn-teacher-primary px-4" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-circle me-2"></i>Update Assignment
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
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { BaseInput, AlertMessage, LoadingSpinner, RichTextEditor } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { cacheService } from '@/services/shared'
import { useAlert, useFormSubmit, createForm } from '@/composables/shared'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const assignmentId = route.params.id

const { alert, showSuccess, showError, clearAlert } = useAlert()
const { submitting, handleSubmit } = useFormSubmit()
const form = createForm('assignment')
const loading = ref(true)
const subjects = ref([])

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: TEACHER_ROUTES.ASSIGNMENT_LIST.path },
  { name: 'Edit' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-teacher-outline', onClick: () => router.push(TEACHER_ROUTES.ASSIGNMENT_LIST.path) }
]

const loadData = async () => {
  loading.value = true
  try {
    const [subRes, assignData] = await Promise.all([
      teacherPanelService.getMyClasses(),
      teacherPanelService.getAssignment(assignmentId)
    ])
    subjects.value = subRes.results || subRes || []
    
    // Format date for datetime-local input (YYYY-MM-DD HH:mm)
    let formattedDate = ''
    if (assignData.due_date) {
      const d = new Date(assignData.due_date)
      // Convert to local time string and replace T with space for VueDatePicker
      formattedDate = new Date(d.getTime() - d.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 16)
        .replace('T', ' ')
    }

    // Update form properties
    form.value = {
      title: assignData.title || '',
      description: assignData.description || '',
      subject: (assignData.subject && typeof assignData.subject === 'object') ? assignData.subject.id : (assignData.subject || ''),
      due_date: formattedDate,
      total_marks: assignData.total_marks || 100
    }
  } catch (error) {
    showError('Failed to load assignment details.')
  } finally {
    loading.value = false
  }
}

const submitForm = () => {
  handleSubmit(async () => {
    await teacherPanelService.updateAssignment(assignmentId, { ...form.value, total_marks: Number(form.value.total_marks) })
    showSuccess('Assignment updated successfully!')
    setTimeout(() => router.push(TEACHER_ROUTES.ASSIGNMENT_LIST.path), 1500)
  }, null, (error) => {
    const errData = error.response?.data
    const msg = typeof errData === 'object' ? Object.entries(errData).map(([k, v]) => `${k}: ${v}`).join('\n') : errData || 'Failed to update assignment.'
    showError(msg)
  })
}

onMounted(loadData)
</script>
