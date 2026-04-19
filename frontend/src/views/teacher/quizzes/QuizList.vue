<template>
  <TeacherPageTemplate title="Online Quizzes" subtitle="Create and manage interactive MCQ & Short Answer quizzes"
    icon="bi bi-question-circle" :breadcrumbs="breadcrumbs" :actions="actions">
    <!-- Alert Message -->
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :auto-close="true"
      @close="alert.show = false" />

    <!-- Delete Confirm Dialog -->
    <ConfirmDialog v-model="showDeleteDialog" title="Delete Quiz"
      :message="`Are you sure you want to delete '${selectedQuiz?.title}'? This action cannot be undone.`"
      confirm-text="Delete" type="danger" theme="teacher" :loading="deleting" @confirm="handleDelete"
      @cancel="showDeleteDialog = false" />

    <!-- Edit Quiz Modal -->
    <BaseModal v-model="showEditModal" title="Edit Quiz Details" @confirm="handleEditSave" :loading="saving"
      confirm-text="Save Changes" confirm-variant="btn-teacher-primary">
      <div class="mb-3">
        <label class="form-label fw-bold small text-muted">QUIZ TITLE</label>
        <input v-model="editForm.title" type="text" class="form-control rounded-3 p-3 bg-light border-0"
          placeholder="Enter quiz title">
      </div>
      <div class="mb-3">
        <label class="form-label fw-bold small text-muted">TIME LIMIT (MINUTES)</label>
        <input v-model.number="editForm.time_limit_minutes" type="number"
          class="form-control rounded-3 p-3 bg-light border-0" min="1">
      </div>
      <div class="form-check form-switch">
        <input class="form-check-input" type="checkbox" id="editPublished" v-model="editForm.is_published">
        <label class="form-check-label" for="editPublished">
          {{ editForm.is_published ? 'Published' : 'Draft' }}
        </label>
      </div>
    </BaseModal>

    <!-- Attempts Detail Modal -->
    <BaseModal v-model="showAttemptsModal" :title="`Student Attempts: ${selectedQuiz?.title}`" size="lg" :show-confirm="false" cancel-text="Close">
      <div v-if="loadingAttempts" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <div class="mt-2 text-muted">Loading attempts...</div>
      </div>
      <div v-else-if="attempts.length === 0" class="text-center py-5">
        <i class="bi bi-people text-muted display-4"></i>
        <p class="mt-3 text-muted">No students have attempted this quiz yet.</p>
      </div>
      <div v-else class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="bg-light">
            <tr>
              <th class="border-0 small fw-bold">STUDENT</th>
              <th class="border-0 small fw-bold text-center">SCORE</th>
              <th class="border-0 small fw-bold text-center">STATUS</th>
              <th class="border-0 small fw-bold text-end">DATE</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="attempt in attempts" :key="attempt.id">
              <td>
                <div class="fw-bold text-dark">{{ attempt.student_name }}</div>
                <div class="extra-small text-muted">{{ attempt.student_enrollment }}</div>
              </td>
              <td class="text-center">
                <span class="badge bg-primary-light text-primary fw-bold">
                  {{ attempt.score }} / {{ selectedQuiz?.total_marks }}
                </span>
              </td>
              <td class="text-center">
                <span :class="['badge rounded-pill', attempt.is_submitted ? 'bg-success-light text-success' : 'bg-warning-light text-warning']">
                  {{ attempt.status }}
                </span>
              </td>
              <td class="text-end small text-muted">
                {{ new Date(attempt.started_at).toLocaleDateString() }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseModal>

    <template #stats>
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <StatCard title="Total Quizzes" :value="quizzes.length" icon="bi bi-journal-check" bg-color="bg-teacher-light"
            icon-color="text-teacher" />
        </div>
        <div class="col-md-3">
          <StatCard title="Active Quizzes" :value="activeQuizzesCount" icon="bi bi-play-circle"
            bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-md-3">
          <StatCard title="Avg. Score" :value="avgScore + '%'" icon="bi bi-graph-up-arrow"
            bg-color="bg-primary-light" icon-color="text-primary" />
        </div>
        <div class="col-md-3">
          <StatCard title="Total Submissions" :value="totalSubmissions" icon="bi bi-people" bg-color="bg-info-light"
            icon-color="text-info" />
        </div>
      </div>
    </template>

    <div class="premium-card border-0 shadow-lg rounded-4 overflow-hidden hover-translate-y">
      <div class="card-body p-0">
        <DataTable :loading="loading" :columns="columns" :data="quizzes" empty-icon="bi bi-question-circle"
          empty-title="No quizzes found" empty-subtitle="Create your first quiz to get started">
          <template #cell-title="{ row }">
            <div class="d-flex align-items-center">
              <div class="avatar-circle-teacher sm me-2">
                <i class="bi bi-puzzle"></i>
              </div>
              <div class="flex-grow-1">
                <div class="fw-bold text-dark">{{ row.title }}</div>
                <div class="d-flex align-items-center gap-2 mt-1">
                  <span class="small text-muted"><i class="bi bi-book me-1"></i>{{ row.subject_name || 'No Subject' }}</span>
                  <span v-if="row.attempt_stats?.total_students > 0" class="badge bg-light text-primary border-primary-subtle extra-small pt-1">
                    <i class="bi bi-people me-1"></i>{{ row.attempt_stats.total_students }} Students
                  </span>
                </div>
              </div>
            </div>
          </template>

          <template #cell-question_count="{ row }">
            <div class="text-center">
              <span class="badge bg-light text-dark border extra-small">{{ row.question_count }} Qs</span>
              <div class="small text-muted mt-1">{{ row.total_marks }} Marks</div>
            </div>
          </template>

          <template #cell-time_limit_minutes="{ row }">
            <div class="text-center">
              <div class="fw-bold text-dark">{{ row.time_limit_minutes }}m</div>
              <div v-if="row.attempt_stats?.max_score > 0" class="extra-small text-success fw-bold">
                Max: {{ row.attempt_stats.max_score }}
              </div>
            </div>
          </template>

          <template #cell-is_published="{ row }">
            <span
              :class="['badge rounded-pill', row.is_published ? 'bg-success-light text-success' : 'bg-warning-light text-warning']">
              {{ row.is_published ? 'Published' : 'Draft' }}
            </span>
          </template>

          <template #cell-actions="{ row }">
            <div class="d-flex gap-2 justify-content-end">
              <!-- Toggle Active/Inactive -->
              <button class="btn btn-sm rounded-3"
                :class="row.is_published ? 'btn-outline-warning' : 'btn-outline-success'"
                :title="row.is_published ? 'Unpublish' : 'Publish'" @click="togglePublish(row)">
                <i :class="row.is_published ? 'bi bi-pause-circle' : 'bi bi-play-circle'"></i>
              </button>
              <!-- Edit -->
              <button class="btn btn-sm btn-teacher-light rounded-3" title="Edit Quiz" @click="openEditModal(row)">
                <i class="bi bi-pencil"></i>
              </button>
              <!-- Details/Attempts -->
              <button class="btn btn-sm btn-outline-primary rounded-3" title="View Student Attempts" @click="viewAttempts(row)">
                <i class="bi bi-eye"></i>
              </button>
              <!-- Delete -->
              <button class="btn btn-sm btn-outline-danger rounded-3" title="Delete Quiz"
                @click="openDeleteDialog(row)">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, AlertMessage, ConfirmDialog, BaseModal } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import '@/assets/css/ai-generator.css'

const router = useRouter()
const loading = ref(false)
const quizzes = ref([])

// UI State
const { alert, showAlert } = useAlert()

// Delete Dialog State
const showDeleteDialog = ref(false)
const selectedQuiz = ref(null)
const deleting = ref(false)

// Attempts Detail State
const showAttemptsModal = ref(false)
const loadingAttempts = ref(false)
const attempts = ref([])

const viewAttempts = async (quiz) => {
  selectedQuiz.value = quiz
  showAttemptsModal.value = true
  loadingAttempts.value = true
  try {
    const data = await teacherPanelService.getQuizAttempts(quiz.id)
    attempts.value = data.results || data || []
  } catch (error) {
    console.error('Error loading attempts:', error)
    showAlert('error', 'Failed to load attempts')
  } finally {
    loadingAttempts.value = false
  }
}

// Edit Modal State
const showEditModal = ref(false)
const saving = ref(false)
const editForm = ref({
  id: null,
  title: '',
  time_limit_minutes: 30,
  is_published: false
})


const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Quizzes' }
]

const actions = [
  {
    label: 'Create New Quiz',
    icon: 'bi bi-plus-lg',
    variant: 'btn-teacher-outline',
    onClick: () => router.push(TEACHER_ROUTES.QUIZ_BUILDER.path)
  }
]

const columns = [
  { key: 'title', label: 'Quiz Title' },
  { key: 'question_count', label: 'Questions', center: true },
  { key: 'time_limit_minutes', label: 'Duration (min)', center: true },
  { key: 'is_published', label: 'Status' },
  { key: 'actions', label: 'Actions' }
]

const activeQuizzesCount = computed(() => quizzes.value.filter(q => q.is_published).length)
const totalSubmissions = computed(() => {
  return quizzes.value.reduce((acc, q) => acc + (q.attempt_stats?.total_attempts || 0), 0)
})
const avgScore = computed(() => {
  const quizzesWithStats = quizzes.value.filter(q => q.attempt_stats?.total_students > 0)
  if (quizzesWithStats.length === 0) return 0
  const sum = quizzesWithStats.reduce((acc, q) => {
    const percentage = (q.attempt_stats.avg_score / q.total_marks) * 100
    return acc + percentage
  }, 0)
  return Math.round(sum / quizzesWithStats.length)
})

const loadQuizzes = async () => {
  loading.value = true
  try {
    const data = await teacherPanelService.getQuizzes()
    quizzes.value = data.results || data || []
  } catch (error) {
    console.error('Error loading quizzes:', error)
    showAlert('error', 'Failed to load quizzes')
  } finally {
    loading.value = false
  }
}

// ==================== Edit Quiz ====================
const openEditModal = (quiz) => {
  selectedQuiz.value = quiz
  editForm.value = {
    id: quiz.id,
    title: quiz.title,
    time_limit_minutes: quiz.time_limit_minutes || 30,
    is_published: quiz.is_published || false
  }
  showEditModal.value = true
}

const handleEditSave = async () => {
  if (!editForm.value.title) {
    showAlert('warning', 'Please enter a quiz title')
    return
  }

  const normalizedTime = Number(editForm.value.time_limit_minutes)
  if (!Number.isFinite(normalizedTime) || normalizedTime <= 0) {
    showAlert('warning', 'Time limit must be greater than 0 minutes')
    return
  }

  saving.value = true
  try {
    const original = selectedQuiz.value
    const shouldPublish = Boolean(editForm.value.is_published)

    await teacherPanelService.updateQuiz(editForm.value.id, {
      title: editForm.value.title,
      time_limit_minutes: Math.floor(normalizedTime)
    })

    if (original && shouldPublish !== Boolean(original.is_published)) {
      if (shouldPublish) {
        await teacherPanelService.publishQuiz(editForm.value.id)
      } else {
        await teacherPanelService.unpublishQuiz(editForm.value.id)
      }
    }

    showAlert('success', 'Quiz updated successfully!')
    showEditModal.value = false
    loadQuizzes()
  } catch (error) {
    console.error('Error updating quiz:', error)
    const apiError = error?.response?.data
    const firstError = typeof apiError === 'string'
      ? apiError
      : Object.values(apiError || {})[0]
    const detail = Array.isArray(firstError) ? firstError[0] : firstError
    showAlert('error', detail || 'Failed to update quiz')
  } finally {
    saving.value = false
  }
}

// ==================== Delete Quiz ====================
const openDeleteDialog = (quiz) => {
  selectedQuiz.value = quiz
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedQuiz.value) return

  deleting.value = true
  try {
    await teacherPanelService.deleteQuiz(selectedQuiz.value.id)
    showAlert('success', 'Quiz deleted successfully!')
    showDeleteDialog.value = false
    loadQuizzes()
  } catch (error) {
    console.error('Error deleting quiz:', error)
    showAlert('error', 'Failed to delete quiz')
  } finally {
    deleting.value = false
  }
}

// ==================== Toggle Publish ====================
const togglePublish = async (quiz) => {
  try {
    if (quiz.is_published) {
      await teacherPanelService.unpublishQuiz(quiz.id)
    } else {
      await teacherPanelService.publishQuiz(quiz.id)
    }
    showAlert('success', quiz.is_published ? 'Quiz unpublished' : 'Quiz published')
    loadQuizzes()
  } catch (error) {
    console.error('Error toggling publish status:', error)
    showAlert('error', 'Failed to update quiz status')
  }
}

onMounted(loadQuizzes)
</script>
