<template>
  <StudentPageTemplate :title="studentName ? `Submit Assignment: ${studentName}` : 'Submit Assignment'"
    :subtitle="studentEnrollment ? `Enrollment: ${studentEnrollment} - Upload your assignment submission` : 'Upload your assignment submission'"
    icon="bi bi-cloud-upload" :breadcrumbs="breadcrumbs">
    <!-- Alert Message -->
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true"
      :auto-close-duration="3000" @close="alert.show = false" />

    <!-- Assignment Selection -->
    <div class="row justify-content-center mb-4">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm border-start-student-thick">
          <div class="card-body">
            <label class="form-label fw-semibold text-success">Select Assignment</label>
            <select v-model="selectedAssignment" class="form-select" @change="onAssignmentSelect">
              <option value="">Choose an assignment...</option>
              <option v-for="assignment in pendingAssignments" :key="assignment.id" :value="assignment.id">
                {{ assignment.title }} - {{ assignment.subject_name || assignment.subject?.name }}
                (Due: {{ formatDate(assignment.due_date) }})
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Assignment Details -->
    <div v-if="assignmentDetails" class="row justify-content-center mb-4">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-success border-0">
            <h5 class="mb-0 text-white fw-semibold">Assignment Details</h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <div class="d-flex align-items-start">
                  <i class="bi bi-book-fill text-success fs-4 me-3"></i>
                  <div>
                    <small class="text-muted d-block">Subject</small>
                    <strong>{{ assignmentDetails.subject_name || assignmentDetails.subject?.name }}</strong>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="d-flex align-items-start">
                  <i class="bi bi-calendar-event text-success fs-4 me-3"></i>
                  <div>
                    <small class="text-muted d-block">Due Date</small>
                    <strong :class="getDueDateClass(assignmentDetails)">
                      {{ formatDate(assignmentDetails.due_date) }}
                    </strong>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="d-flex align-items-start">
                  <i class="bi bi-star-fill text-success fs-4 me-3"></i>
                  <div>
                    <small class="text-muted d-block">Total Marks</small>
                    <strong>{{ assignmentDetails.total_marks || assignmentDetails.max_marks || 100 }}</strong>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="d-flex align-items-start">
                  <i class="bi bi-person-fill text-success fs-4 me-3"></i>
                  <div>
                    <small class="text-muted d-block">Created By</small>
                    <strong>{{ assignmentDetails.created_by_name || 'Instructor' }}</strong>
                  </div>
                </div>
              </div>
              <div class="col-12">
                <div class="d-flex align-items-start">
                  <i class="bi bi-file-text text-success fs-4 me-3"></i>
                  <div class="flex-grow-1">
                    <small class="text-muted d-block">Description</small>
                    <div class="mb-0" v-html="assignmentDetails.description || 'No description provided'"></div>
                  </div>
                </div>
              </div>
              <div v-if="assignmentDetails.material_file_url" class="col-12">
                <div class="d-flex align-items-start">
                  <i class="bi bi-paperclip text-success fs-4 me-3"></i>
                  <div class="flex-grow-1">
                    <small class="text-muted d-block">Attachment</small>
                    <button type="button" class="btn btn-outline-success btn-sm mt-1" @click="openMaterial(assignmentDetails.material_file_url)">
                      <i class="bi bi-download me-1"></i>
                      {{ assignmentDetails.material_file_name || 'Download Material' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submission Form -->
    <div v-if="selectedAssignment" class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-success border-0">
            <h5 class="mb-0 text-white fw-semibold">Submission Form</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="submitAssignment">
              <!-- Comments -->
              <div class="mb-4">
                <label class="form-label fw-semibold">
                  <i class="bi bi-chat-left-text text-success me-2"></i>
                  Comments / Notes
                </label>
                <textarea v-model="submission.comments" class="form-control" rows="4"
                  placeholder="Add any comments or notes about your submission..."></textarea>
              </div>

              <!-- File Upload -->
              <div class="mb-4">
                <label class="form-label fw-semibold">
                  <i class="bi bi-cloud-upload text-success me-2"></i>
                  Upload File
                </label>
                <input type="file" class="form-control" @change="onFileSelect" accept=".pdf,.doc,.docx,.zip,.rar"
                >
                <small class="text-muted">
                  Accepted formats: PDF, DOC, DOCX, ZIP, RAR (Max 10MB). You can submit with text, file, or both.
                </small>

                <!-- File Preview -->
                <div v-if="submission.file" class="mt-3 p-3 bg-success rounded file-preview-box">
                  <div class="d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center">
                      <i class="bi bi-file-earmark-check-fill text-white fs-4 me-3"></i>
                      <div>
                        <strong class="text-white">{{ submission.file.name }}</strong>
                        <br>
                        <small class="text-white opacity-75">{{ formatFileSize(submission.file.size) }}</small>
                      </div>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-light" @click="removeFile">
                      <i class="bi bi-x-lg"></i>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Submit Button -->
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-success btn-lg" :disabled="submitting || (!submission.file && !submission.comments?.trim())">
                  <span v-if="submitting">
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Submitting...
                  </span>
                  <span v-else>
                    <i class="bi bi-check-circle me-2"></i>
                    Submit Assignment
                  </span>
                </button>
                <button type="button" class="btn btn-outline-secondary" @click="resetForm">
                  <i class="bi bi-arrow-clockwise me-2"></i>
                  Reset Form
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <i class="bi bi-clipboard-check display-1 text-muted"></i>
      <h3 class="mt-3">Select an Assignment</h3>
      <p class="text-muted">Choose an assignment from the dropdown above to submit your work</p>
    </div>

    <!-- Success Modal -->
    <BaseModal v-model="showSuccessModal" title="Congratulations!" :show-footer="false">
      <div class="text-center py-4">
        <div class="mb-4">
          <i class="bi bi-check-circle-fill text-success display-1"></i>
        </div>
        <h3 class="text-success mb-3">Submission Successful!</h3>
        <p class="text-muted mb-4">Your assignment has been submitted successfully.</p>
        <button class="btn btn-success" @click="closeSuccessModal">
          <i class="bi bi-check-lg me-2"></i>
          Done
        </button>
      </div>
    </BaseModal>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, BaseModal } from '@/components/shared/common'
import { useStudentBase } from '@/composables/student/useStudentBase'
import studentPanelService from '@/services/student/studentPanelService'
import { studentService } from '@/services/shared'
import { useRouter, useRoute } from 'vue-router'
import { formatDateTime } from '@/utils/formatters'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const router = useRouter(); const route = useRoute()
const { studentId, studentName, studentEnrollment, loadProfile } = useStudentBase()

const assignments = ref([]); const selectedAssignment = ref(''); const assignmentDetails = ref(null)
const submitting = ref(false); const showSuccessModal = ref(false)
const submission = ref({ comments: '', file: null })
const { alert, showError } = useAlert()

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: STUDENT_ROUTES.VIEW_ASSIGNMENTS.path },
  { name: 'Submit Assignment' }
]

const pendingAssignments = computed(() => {
  const now = new Date()
  return assignments.value.filter(a => {
    const due = a.due_date ? new Date(a.due_date) : null
    return due && due > now && !a.is_submitted
  })
})

const onAssignmentSelect = () => {
  assignmentDetails.value = assignments.value.find(a => a.id === selectedAssignment.value)
  submission.value = { comments: '', file: null }
}

const onFileSelect = (e) => {
  const file = e.target.files[0]
  if (file && file.size > 10 * 1024 * 1024) {
    showError('File must be < 10MB', 'Too Large'); e.target.value = ''
  } else { submission.value.file = file }
}

const formatFileSize = (b) => b < 1024 ? b + ' B' : b < 1048576 ? (b / 1024).toFixed(1) + ' KB' : (b / 1048576).toFixed(1) + ' MB'
const getDueDateClass = (a) => {
  if (!a.due_date) return ''; const diff = Math.ceil((new Date(a.due_date) - new Date()) / 86400000)
  return diff < 0 ? 'text-danger' : diff <= 2 ? 'text-warning' : 'text-success'
}

const submitAssignment = async () => {
  if (!submission.value.file && !submission.value.comments?.trim()) {
    showError('Please add comments/notes or attach a file', 'Required'); return
  }
  submitting.value = true
  try {
    const fd = new FormData(); fd.append('assignment', selectedAssignment.value); fd.append('student', studentId)
    if (submission.value.file) fd.append('file_upload', submission.value.file)
    if (submission.value.comments) fd.append('submission_text', submission.value.comments)
    await studentPanelService.submitAssignment(fd)
    showSuccessModal.value = true; submission.value = { comments: '', file: null }
  } catch (err) {
    showError('Failed to submit. Try again.')
  } finally { submitting.value = false }
}

const formatDate = (d) => formatDateTime(d)
const removeFile = () => submission.value.file = null
const resetForm = () => submission.value = { comments: '', file: null }
const closeSuccessModal = () => { showSuccessModal.value = false; router.push(STUDENT_ROUTES.VIEW_ASSIGNMENTS.path) }
const openMaterial = (url) => {
  if (!url) return
  window.open(url, '_blank', 'noopener')
}

onMounted(async () => {
  loadProfile()
  const res = await studentService.getAssignments(studentId)
  assignments.value = Array.isArray(res) ? res : (res.results || [])
  if (route.query.assignmentId) {
    selectedAssignment.value = route.query.assignmentId; onAssignmentSelect()
  }
})
</script>
