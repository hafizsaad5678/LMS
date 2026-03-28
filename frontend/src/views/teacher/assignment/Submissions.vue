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
            <button v-if="row.submission_file" @click="window.open(row.submission_file, '_blank')"
              class="btn btn-sm btn-outline-primary btn-action" title="Download"><i class="bi bi-download"></i></button>
            <button @click="openGradeModal(row)" class="btn btn-sm btn-outline-success btn-action"
              :title="row.status === 'graded' ? 'Edit Grade' : 'Grade'"><i class="bi bi-check2-circle"></i></button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Grading Modal -->
    <BaseModal v-model="showGradeModal" title="Grade Submission" @confirm="submitGrade" :loading="submitting"
      confirm-text="Save Grade">
      <div v-if="selectedSubmission" class="p-2">
        <div class="bg-light p-3 rounded-4 mb-4 border-start border-4 border-teacher">
          <h6 class="fw-bold text-dark mb-1">{{ selectedSubmission.student_name }}</h6>
          <p class="text-muted small mb-0">ROLL NO: {{ selectedSubmission.roll_no }}</p>
        </div>
        <div class="mb-4">
          <BaseInput v-model.number="gradeForm.marks" label="Obtained Marks" type="number"
            :max="assignment?.total_marks" min="0" required :placeholder="`Out of ${assignment?.total_marks}`" />
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
const selectedSubmission = ref(null)
const gradeForm = ref({ marks: 0, feedback: '' })

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

async function submitGrade() {
  if (!selectedSubmission.value?.submission_id) return showAlert('warning', 'Cannot grade a submission that has not been submitted yet.')
  if (gradeForm.value.marks < 0 || gradeForm.value.marks > assignment.value.total_marks) return showAlert('error', `Marks must be between 0 and ${assignment.value.total_marks}`)

  submitting.value = true
  try {
    const gradeData = { submission: selectedSubmission.value.submission_id, marks_obtained: gradeForm.value.marks, feedback: gradeForm.value.feedback, grade_value: calculateLetterGrade((gradeForm.value.marks / assignment.value.total_marks) * 100) }
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
