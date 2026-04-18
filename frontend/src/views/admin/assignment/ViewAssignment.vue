<template>
  <AdminPageTemplate
    title="Assignment Details"
    subtitle="View assignment record and submission summary"
    icon="bi bi-eye"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <LoadingSpinner v-if="loading" text="Loading assignment details..." theme="admin" />

    <div v-else-if="!assignmentId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-file-earmark-text display-4"></i>
      </div>
      <h4 class="text-muted">No Assignment Selected</h4>
      <p class="text-muted mb-4">Open an assignment from the list to view details.</p>
      <button @click="goToList" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Assignment List
      </button>
    </div>

    <div v-else-if="!assignment.id" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-file-earmark-x display-4"></i>
      </div>
      <h4 class="text-muted">Assignment Not Found</h4>
      <p class="text-muted mb-4">The selected assignment record could not be loaded.</p>
      <button @click="goToList" class="btn btn-admin-primary">
        <i class="bi bi-arrow-left me-2"></i>Back to Assignment List
      </button>
    </div>

    <div v-else>
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="d-flex flex-wrap justify-content-between gap-3 align-items-start">
            <div>
              <h4 class="mb-1">{{ assignment.title }}</h4>
              <p class="text-muted mb-2">{{ assignment.subject_name || 'N/A' }} ({{ assignment.subject_code || 'N/A' }})</p>
              <span :class="getStatusBadge(assignment.due_date)">{{ getStatus(assignment.due_date) }}</span>
            </div>
            <div class="text-end">
              <div class="small text-muted">Due Date</div>
              <div class="fw-semibold">{{ formatDate(assignment.due_date) }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-info-circle me-2 text-admin"></i>Assignment Info</h6>
            </div>
            <div class="card-body p-0">
              <table class="table table-sm mb-0 align-middle">
                <tbody>
                  <tr>
                    <th class="w-50 ps-3">Created By</th>
                    <td>{{ assignment.created_by_name || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <th class="ps-3">Total Marks</th>
                    <td>{{ assignment.total_marks }}</td>
                  </tr>
                  <tr>
                    <th class="ps-3">Submissions</th>
                    <td>{{ assignment.submission_count || 0 }}</td>
                  </tr>
                  <tr>
                    <th class="ps-3">Created At</th>
                    <td>{{ formatDate(assignment.created_at) }}</td>
                  </tr>
                  <tr>
                    <th class="ps-3">Last Updated</th>
                    <td>{{ formatDate(assignment.updated_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-text-paragraph me-2 text-admin"></i>Description</h6>
            </div>
            <div class="card-body">
              <p class="mb-0 text-muted" style="white-space: pre-wrap;">{{ assignment.description || 'No description available.' }}</p>
            </div>
          </div>
        </div>

        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-upload me-2 text-admin"></i>Submissions</h6>
            </div>
            <div class="card-body p-0">
              <div v-if="submissions.length === 0" class="p-4 text-muted">No submissions found for this assignment.</div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      <th class="ps-3">Student</th>
                      <th>Enrollment</th>
                      <th>Submitted At</th>
                      <th>Grade</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="submission in submissions" :key="submission.id">
                      <td class="ps-3">{{ submission.student_name || 'N/A' }}</td>
                      <td>{{ submission.student_enrollment || 'N/A' }}</td>
                      <td>{{ formatDate(submission.submitted_at) }}</td>
                      <td>{{ submission.grade?.grade_value || 'Not graded' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { LoadingSpinner } from '@/components/shared/common'
import { assignmentService } from '@/services/shared'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()

const assignmentId = computed(() => route.params.id)
const loading = ref(true)
const assignment = ref({})
const submissions = ref([])

const breadcrumbs = computed(() => [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: ADMIN_ROUTES.ASSIGNMENTS.path },
  { name: 'View Assignment' }
])

const actions = [
  {
    label: 'Back to List',
    icon: 'bi bi-arrow-left',
    variant: 'btn-admin-outline',
    onClick: () => goToList()
  }
]

const toDate = (value) => {
  const date = value ? new Date(value) : null
  return date && !Number.isNaN(date.getTime()) ? date : null
}

const isSameCalendarDay = (left, right) => (
  left.getFullYear() === right.getFullYear() &&
  left.getMonth() === right.getMonth() &&
  left.getDate() === right.getDate()
)

const getStatus = (dueDate) => {
  const due = toDate(dueDate)
  if (!due) return 'Unknown'
  const now = new Date()
  if (isSameCalendarDay(due, now)) return 'Due Today'
  return due < now ? 'Overdue' : 'Upcoming'
}

const getStatusBadge = (dueDate) => {
  const status = getStatus(dueDate)
  if (status === 'Overdue') return 'badge bg-danger'
  if (status === 'Due Today') return 'badge bg-info'
  if (status === 'Upcoming') return 'badge bg-success'
  return 'badge bg-secondary'
}

const formatDate = (value) => formatDateUtil(value)

const goToList = () => {
  router.push(ADMIN_ROUTES.ASSIGNMENTS.path)
}

const loadAssignment = async () => {
  if (!assignmentId.value) {
    loading.value = false
    return
  }

  loading.value = true
  try {
    const [assignmentResponse, submissionsResponse] = await Promise.allSettled([
      assignmentService.getAssignmentById(assignmentId.value),
      assignmentService.getSubmissions(assignmentId.value)
    ])

    assignment.value = assignmentResponse.status === 'fulfilled' ? assignmentResponse.value : {}
    const rawSubmissions = submissionsResponse.status === 'fulfilled' ? submissionsResponse.value : []
    submissions.value = Array.isArray(rawSubmissions) ? rawSubmissions : (rawSubmissions.results || [])
  } catch (error) {
    console.error('Error loading assignment details:', error)
    assignment.value = {}
    submissions.value = []
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) loadAssignment()
}, { immediate: false })

onMounted(() => {
  loadAssignment()
})
</script>
