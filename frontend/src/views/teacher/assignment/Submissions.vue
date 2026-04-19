<template>
  <TeacherPageTemplate title="Assignment Submissions"
    :subtitle="assignment ? `Submissions for: ${assignment.title}` : 'View and grade student submissions'"
    icon="bi bi-person-check" :breadcrumbs="breadcrumbs" :actions="actions">
    <AlertMessage v-if="alert.show" v-bind="alert" :auto-close="true" @close="clearAlert" />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 mb-4">
        <div v-for="stat in statsCards" :key="stat.title" class="col-md-4">
          <StatCard v-bind="stat" />
        </div>
      </div>
    </template>

    <LoadingSpinner v-if="loading" text="Loading submissions..." theme="teacher" />

    <div v-else>
      <SearchFilter v-model="searchQuery" :show-card="true" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search students or roll no..."
        search-col-size="col-md-5" actions-col-size="col-md-3" theme="teacher" @refresh="loadData"
        @reset="resetFilters">
        <template #filters>
          <div class="col-md-4">
            <SelectInput v-model="filters.status" :options="TEACHER_SUBMISSION_STATUS_OPTIONS"
              placeholder="All Statuses" :no-margin="true" />
          </div>
        </template>
      </SearchFilter>

      <!-- Submissions Table -->
      <DataTable :columns="tableColumns" :data="filteredSubmissions" empty-icon="bi bi-folder-x"
        empty-title="No submissions match your filters">
        <template #cell-student="{ row }">
          <div class="d-flex align-items-center">
            <div class="avatar-circle-teacher me-2">{{ row.student_name?.charAt(0) || 'S' }}</div>
            <div>
              <div class="fw-bold text-dark">{{ row.student_name }}</div>
              <div class="small text-muted">{{ row.roll_no || 'No ID' }}</div>
            </div>
          </div>
        </template>

        <template #cell-status="{ value }">
          <span :class="getStatusBadge(value)">{{ value || 'Pending' }}</span>
        </template>

        <template #cell-submitted_at="{ value }">
          <div v-if="value" class="small text-muted fw-medium">
            <i class="bi bi-calendar-event me-1"></i>{{ formatDateTime(value) }}
          </div>
          <span v-else class="badge bg-light text-muted fw-normal">Not detected</span>
        </template>

        <template #cell-marks="{ row }">
          <div v-if="row.status === 'graded'" class="text-center">
            <span class="badge bg-success-light text-success fs-6 px-3">{{ row.obtained_marks }} / {{
              assignment?.total_marks }}</span>
          </div>
          <div v-else class="text-center text-muted">- / {{ assignment?.total_marks }}</div>
        </template>

        <template #cell-actions="{ row }">
          <div class="d-flex gap-2 justify-content-center">
            <button @click="openDetailsModal(row)"
              class="btn btn-sm btn-outline-secondary btn-action" title="View Details"><i class="bi bi-eye"></i></button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Submission Details Modal -->
    <BaseModal v-model="showDetailsModal" title="Submission Details" :show-footer="false">
      <div v-if="detailsSubmission" class="p-2">
        <div class="bg-light p-3 rounded-4 mb-3 border-start border-4 border-primary">
          <h6 class="fw-bold text-dark mb-1">{{ detailsSubmission.student_name }}</h6>
          <p class="text-muted small mb-0">ROLL NO: {{ detailsSubmission.roll_no }}</p>
        </div>

        <div v-if="!detailsSubmission.submission_id" class="alert alert-warning py-2 px-3 mb-3" role="alert">
          User has not submitted this assignment yet.
        </div>

        <div class="mb-3">
          <div class="small text-muted text-uppercase fw-bold mb-1">Submitted At</div>
          <div class="fw-medium">{{ detailsSubmission.submitted_at ? formatDateTime(detailsSubmission.submitted_at) : 'N/A' }}</div>
        </div>

        <div class="mb-3">
          <div class="small text-muted text-uppercase fw-bold mb-1">Student Notes / Comments</div>
          <div class="border rounded-3 p-3 bg-light-subtle" style="white-space: pre-wrap;">
            {{ detailsSubmission.comments || 'No text/comments provided by student.' }}
          </div>
        </div>

        <div class="mb-2">
          <div class="small text-muted text-uppercase fw-bold mb-1">Attachment</div>
          <div v-if="detailsSubmission.submission_file" class="d-flex align-items-center gap-2">
            <button type="button" class="btn btn-outline-primary btn-sm" @click="downloadSubmissionFile(detailsSubmission.submission_file)">
              <i class="bi bi-download me-1"></i>
              Download File
            </button>
            <span class="small text-muted text-truncate">{{ getFileName(detailsSubmission.submission_file) }}</span>
          </div>
          <div v-else class="text-muted small">No attachment submitted.</div>
        </div>

        <div class="d-flex justify-content-end mt-3">
          <button
            v-if="detailsSubmission.submission_id"
            type="button"
            class="btn btn-outline-success"
            @click="openGradeFromDetails"
          >
            <i class="bi bi-check2-circle me-1"></i>
            {{ detailsSubmission.status === 'graded' ? 'Edit Grade' : 'Grade Submission' }}
          </button>
          <button
            v-else-if="isAssignmentExpired"
            type="button"
            class="btn btn-outline-danger"
            :disabled="markingZero"
            @click="markZeroFromDetails"
          >
            <span v-if="markingZero" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            <i v-else class="bi bi-exclamation-circle me-1"></i>
            Mark 0 (No Submission)
          </button>
          <span v-else class="text-muted small">Due date not expired yet.</span>
        </div>
      </div>
    </BaseModal>

    <!-- Grading Modal -->
    <BaseModal v-model="showGradeModal" title="Grade Submission" @confirm="submitGrade" :loading="submitting"
      confirm-text="Save Grade">
      <div v-if="selectedSubmission" class="p-2">
        <div class="bg-light p-3 rounded-4 mb-4 border-start border-4 border-teacher">
          <h6 class="fw-bold text-dark mb-1">{{ selectedSubmission.student_name }}</h6>
          <p class="text-muted small mb-0">ROLL NO: {{ selectedSubmission.roll_no }}</p>
        </div>
        <div class="mb-4">
          <BaseInput
            v-model.number="gradeForm.marks"
            :label="`Obtained Marks (Out of ${maxMarks.toFixed(2)})`"
            type="number"
            :max="maxMarks"
            min="0"
            required
            placeholder="Enter obtained marks"
          />
          <div class="small mt-1" :class="marksRangeError ? 'text-danger' : 'text-muted'">
            {{ Number(gradeForm.marks || 0) }} out of {{ maxMarks }}
            <span v-if="marksRangeError" class="ms-1">(Marks must be between 0 and {{ maxMarks }})</span>
          </div>
        </div>
        <div class="mb-2">
          <label class="form-label fw-bold text-dark small text-uppercase">Feedback</label>
          <RichTextEditor v-model="gradeForm.feedback" placeholder="Write constructive feedback..." />
        </div>
      </div>
    </BaseModal>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { smartSearch } from '@/utils'
import { useRoute, useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { DataTable, BaseModal, BaseInput, StatCard, SearchFilter, SelectInput, AlertMessage, LoadingSpinner, RichTextEditor } from '@/components/shared/common'
import { useAlert } from '@/composables/shared'
import { useFilterLogic } from '@/composables/teacher/useFilterLogic'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { api } from '@/services/shared'
import { formatDateTime } from '@/utils/formatters'
import { calculateLetterGrade } from '@/utils/badgeHelpers'
import { TEACHER_SUBMISSION_STATUS_OPTIONS } from '@/utils/constants/options'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const route = useRoute()
const router = useRouter()
const { alert, showAlert, clearAlert } = useAlert()
const assignmentId = route.query.id || route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: TEACHER_ROUTES.ASSIGNMENT_LIST.path },
  { name: 'Submissions' }
]

const actions = [{ label: 'Back', icon: 'bi bi-arrow-left', variant: 'btn-teacher-outline', onClick: () => router.push(TEACHER_ROUTES.ASSIGNMENT_LIST.path) }]

const loading = ref(true)
const assignment = ref(null)
const submissions = ref([])
const submitting = ref(false)
const filters = ref({ status: '' })
const showGradeModal = ref(false)
const showDetailsModal = ref(false)
const markingZero = ref(false)
const selectedSubmission = ref(null)
const detailsSubmission = ref(null)
const gradeForm = ref({ marks: 0, feedback: '' })
const maxMarks = computed(() => Number(assignment.value?.total_marks || 0))
const isAssignmentExpired = computed(() => {
  if (!assignment.value?.due_date) return false
  const due = new Date(assignment.value.due_date)
  return !Number.isNaN(due.getTime()) && due < new Date()
})
const marksRangeError = computed(() => {
  const marks = Number(gradeForm.value?.marks ?? 0)
  return Number.isFinite(marks) && (marks < 0 || marks > maxMarks.value)
})

const { searchQuery, filteredItems: searchFilteredSubmissions } = useFilterLogic(
  submissions,
  { searchFields: ['student_name', 'roll_no'] }
)

const tableColumns = [
  { key: 'student', label: 'Student Info' },
  { key: 'submitted_at', label: 'Completion Date' },
  { key: 'status', label: 'Current Status' },
  { key: 'marks', label: 'Grading', center: true },
  { key: 'actions', label: 'Actions', center: true }
]

const statsCards = computed(() => [
  { title: 'Total Students', value: submissions.value.length, icon: 'bi bi-people', bgColor: 'bg-admin-light', iconColor: 'text-teacher' },
  { title: 'Submissions Received', value: submissions.value.filter(s => !!s.submitted_at).length, icon: 'bi bi-upload', bgColor: 'bg-success-light', iconColor: 'text-success' },
  { title: 'Pending Grading', value: submissions.value.filter(s => s.status === 'pending' || !s.status).length, icon: 'bi bi-clock-history', bgColor: 'bg-warning-light', iconColor: 'text-warning' }
])

const filteredSubmissions = computed(() => {
  // Note: Custom status match logic ('pending' handling) requires manual filtering. 
  // Base useFilterLogic handles the search mapping correctly.
  return searchFilteredSubmissions.value.filter(s => {
    return !filters.value.status || (filters.value.status === 'pending' && (!s.status || s.status === 'pending')) || s.status === filters.value.status
  })
})

const getStatusBadge = (status) => {
  const badges = { graded: 'badge bg-success-light text-success px-3', submitted: 'badge bg-primary-light text-primary px-3', late: 'badge bg-warning-light text-warning px-3' }
  return badges[status?.toLowerCase()] || 'badge bg-light text-muted px-3'
}

async function loadData() {
  if (!assignmentId) {
    showAlert('error', 'No assignment ID provided.', 'Missing Assignment')
    loading.value = false
    return
  }
  loading.value = true
  try {
    const assignmentData = await teacherPanelService.getAssignment(assignmentId)
    assignment.value = assignmentData

    const [students, submissionsData] = await Promise.all([
      teacherPanelService.getStudentsBySubject(assignmentData.subject),
      teacherPanelService.getAssignmentSubmissions(assignmentId)
    ])
    const submissionsList = Array.isArray(submissionsData) ? submissionsData : (submissionsData.results || [])
    const submissionsMap = new Map(submissionsList.map(sub => [String(sub.student), sub]))

    submissions.value = students.map(student => {
      const submission = submissionsMap.get(String(student.id))
      return {
        student: student.id,
        student_name: student.full_name || student.name,
        roll_no: student.enrollment_number || student.roll_no,
        submitted_at: submission?.submitted_at || null,
        submission_file: submission?.submission_file || null,
        comments: submission?.comments || submission?.submission_text || '',
        status: submission ? (submission.grade ? 'graded' : 'submitted') : 'pending',
        obtained_marks: submission?.grade?.marks_obtained || null,
        feedback: submission?.grade?.feedback || '',
        submission_id: submission?.id || null,
        grade_id: submission?.grade?.id || null
      }
    })
  } catch (error) {
    showAlert('error', error.response?.data?.detail || 'Failed to load submissions.', 'Error')
  } finally {
    loading.value = false
  }
}

function openGradeModal(submission) {
  selectedSubmission.value = submission
  gradeForm.value = { marks: submission.obtained_marks || 0, feedback: submission.feedback || '' }
  showGradeModal.value = true
}

function openDetailsModal(submission) {
  detailsSubmission.value = submission
  showDetailsModal.value = true
}

async function markZeroFromDetails() {
  if (!detailsSubmission.value?.student || !assignmentId) return
  if (!isAssignmentExpired.value) {
    showAlert('warning', 'Cannot assign zero marks before due date expires.')
    return
  }

  markingZero.value = true
  try {
    await teacherPanelService.markZeroForMissingSubmission(assignmentId, detailsSubmission.value.student)
    showAlert('success', '0 marks assigned for non-submission.')
    showDetailsModal.value = false
    await loadData()
  } catch (error) {
    showAlert('error', error?.response?.data?.detail || 'Failed to assign 0 marks.')
  } finally {
    markingZero.value = false
  }
}

function openGradeFromDetails() {
  if (!detailsSubmission.value) return
  showDetailsModal.value = false
  openGradeModal(detailsSubmission.value)
}

function getFileName(fileUrl) {
  if (!fileUrl) return 'Attachment'
  try {
    const cleanUrl = String(fileUrl).split('?')[0]
    const parts = cleanUrl.split('/')
    return decodeURIComponent(parts[parts.length - 1] || 'Attachment')
  } catch {
    return 'Attachment'
  }
}

async function downloadSubmissionFile(fileUrl) {
  if (!fileUrl) return
  try {
    const response = await api.get(fileUrl, { responseType: 'blob' })
    const blob = response?.data
    if (!blob) throw new Error('No file data received')

    const objectUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = getFileName(fileUrl)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(objectUrl)
  } catch {
    // Fallback when direct blob download fails (e.g., browser/network restrictions).
    window.open(fileUrl, '_blank', 'noopener')
    showAlert('warning', 'Direct download was blocked. File opened in a new tab instead.')
  }
}

async function submitGrade() {
  if (!selectedSubmission.value?.submission_id) return showAlert('warning', 'Cannot grade a submission that has not been submitted yet.')
  if (marksRangeError.value) return showAlert('error', `Marks must be between 0 and ${maxMarks.value}`)

  submitting.value = true
  try {
    const gradeData = { submission: selectedSubmission.value.submission_id, marks_obtained: gradeForm.value.marks, feedback: gradeForm.value.feedback, grade_value: calculateLetterGrade((gradeForm.value.marks / maxMarks.value) * 100) }
    if (selectedSubmission.value.grade_id) await teacherPanelService.updateGrade(selectedSubmission.value.grade_id, gradeData)
    else await teacherPanelService.submitGrades(gradeData)
    showAlert('success', 'Grade submitted successfully!')
    showGradeModal.value = false
    loadData()
  } catch (error) {
    showAlert('error', error.response?.data?.detail || 'Failed to submit grade.')
  } finally {
    submitting.value = false
  }
}

const resetFilters = () => { searchQuery.value = ''; filters.value = { status: '' } }

onMounted(loadData)
</script>
