<template>
  <AdminPageTemplate
    title="Edit Assignment"
    subtitle="Update assignment details and requirements"
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

    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Discard Changes"
      message="Are you sure? All unsaved changes will be lost."
      type="warning"
      theme="admin"
      confirm-text="Discard"
      @confirm="confirmCancel"
    />

    <LoadingSpinner v-if="loading" text="Loading assignment details..." theme="admin" />

    <div v-else-if="!assignmentId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-pencil-square display-4"></i>
      </div>
      <h4 class="text-muted">No Assignment Selected</h4>
      <p class="text-muted mb-4">Please select an assignment from the list to edit.</p>
      <button @click="goToList" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Assignment List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-file-earmark-text me-2 text-admin"></i>Assignment Details
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit">
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom"><i class="bi bi-info-circle me-2"></i>Basic Information</h6>
                <div class="row g-3">
                  <div class="col-12">
                    <BaseInput v-model="form.title" label="Assignment Title" required />
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label fw-semibold">Subject <span class="text-danger">*</span></label>
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
                      <label class="form-label fw-semibold">Created By (Teacher)</label>
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

              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom"><i class="bi bi-calendar-event me-2"></i>Deadline & Marks</h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label fw-semibold">Due Date & Time <span class="text-danger">*</span></label>
                      <input v-model="form.due_date" type="datetime-local" class="form-control" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <BaseInput v-model.number="form.total_marks" label="Total Marks" type="number" required />
                  </div>
                </div>
              </div>

              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom"><i class="bi bi-text-paragraph me-2"></i>Description & Instructions</h6>
                <textarea
                  v-model="form.description"
                  class="form-control"
                  rows="5"
                  placeholder="Enter detailed assignment description, requirements, and submission guidelines..."
                  required
                ></textarea>
              </div>

              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-admin-outline px-4" :disabled="submitting">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-circle me-2"></i>Update Assignment
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
import { computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { BaseInput, AlertMessage, ConfirmDialog, LoadingSpinner } from '@/components/shared/common'
import { assignmentService, subjectService, teacherService, cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const assignmentId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: ADMIN_ROUTES.ASSIGNMENTS.path },
  { name: 'Edit Assignment' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => goToList() }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const showConfirmDialog = ref(false)
const loading = ref(true)
const submitting = ref(false)
const subjects = ref([])
const teachers = ref([])
const initialSnapshot = ref('')

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

const goToList = () => {
  router.push(ADMIN_ROUTES.ASSIGNMENTS.path)
}

const toDateTimeLocal = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return local.toISOString().slice(0, 16)
}

const extractId = (value) => {
  if (value && typeof value === 'object') return value.id || value.pk || ''
  return value || ''
}

const normalizeForm = (data) => ({
  title: String(data.title || '').trim(),
  description: String(data.description || '').trim(),
  subject: data.subject || '',
  created_by: data.created_by || '',
  due_date: data.due_date || '',
  total_marks: Number(data.total_marks || 0)
})

const hasUnsavedChanges = computed(() => {
  if (!initialSnapshot.value) return false
  return JSON.stringify(normalizeForm(form.value)) !== initialSnapshot.value
})

const loadData = async () => {
  if (!assignmentId.value) {
    loading.value = false
    return
  }

  loading.value = true
  try {
    const [subjectsRes, teachersRes, assignment] = await Promise.all([
      subjectService.getAllSubjects(),
      teacherService.getAllTeachers(),
      assignmentService.getAssignmentById(assignmentId.value)
    ])

    subjects.value = Array.isArray(subjectsRes) ? subjectsRes : (subjectsRes.results || [])
    teachers.value = Array.isArray(teachersRes) ? teachersRes : (teachersRes.results || [])

    form.value = {
      title: assignment.title || '',
      description: assignment.description || '',
      subject: extractId(assignment.subject),
      created_by: extractId(assignment.created_by),
      due_date: toDateTimeLocal(assignment.due_date),
      total_marks: Number(assignment.total_marks || 100)
    }

    initialSnapshot.value = JSON.stringify(normalizeForm(form.value))
  } catch (error) {
    const msg = error.response?.data?.detail || 'Failed to load assignment details.'
    showAlert('error', msg, 'Error!')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!assignmentId.value) return

  submitting.value = true
  try {
    const normalized = normalizeForm(form.value)
    const payload = {
      title: normalized.title,
      description: normalized.description,
      subject: normalized.subject,
      due_date: normalized.due_date,
      total_marks: normalized.total_marks
    }

    if (normalized.created_by) {
      payload.created_by = normalized.created_by
    }

    await assignmentService.patchAssignment(assignmentId.value, payload)

    cacheService.clear('assignments_list')
    cacheService.clearPattern('assignment')

    showAlert('success', 'Assignment updated successfully!', 'Success!')
    setTimeout(() => goToList(), 1200)
  } catch (error) {
    const errData = error.response?.data
    const msg = typeof errData === 'object'
      ? Object.entries(errData).map(([key, value]) => `${key}: ${value}`).join('\n')
      : (errData || 'Failed to update assignment.')
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  if (hasUnsavedChanges.value) {
    showConfirmDialog.value = true
    return
  }
  goToList()
}

const confirmCancel = () => {
  showConfirmDialog.value = false
  goToList()
}

onMounted(loadData)
</script>
