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
      confirm-text="Save Changes" confirm-variant="btn-teacher">
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

    <template #stats>
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <StatCard title="Total Quizzes" :value="quizzes.length" icon="bi bi-journal-check" bg-color="bg-teacher-light"
            icon-color="text-teacher" />
        </div>
        <div class="col-md-4">
          <StatCard title="Active Quizzes" :value="activeQuizzesCount" icon="bi bi-play-circle"
            bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-md-4">
          <StatCard title="Submissions" :value="totalSubmissions" icon="bi bi-people" bg-color="bg-info-light"
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
              <div>
                <div class="fw-bold text-dark">{{ row.title }}</div>
                <div class="small text-muted">
                  <i class="bi bi-book me-1"></i>{{ row.subject_name || 'No Subject' }}
                </div>
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
const totalSubmissions = ref(0)

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

  saving.value = true
  try {
    await teacherPanelService.updateQuiz(editForm.value.id, {
      title: editForm.value.title,
      time_limit_minutes: editForm.value.time_limit_minutes,
      is_published: editForm.value.is_published
    })
    showAlert('success', 'Quiz updated successfully!')
    showEditModal.value = false
    loadQuizzes()
  } catch (error) {
    console.error('Error updating quiz:', error)
    showAlert('error', 'Failed to update quiz')
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
    await teacherPanelService.updateQuiz(quiz.id, {
      is_published: !quiz.is_published
    })
    showAlert('success', quiz.is_published ? 'Quiz unpublished' : 'Quiz published')
    loadQuizzes()
  } catch (error) {
    console.error('Error toggling publish status:', error)
    showAlert('error', 'Failed to update quiz status')
  }
}

onMounted(loadQuizzes)
</script>
