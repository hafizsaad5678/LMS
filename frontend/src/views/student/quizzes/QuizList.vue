<template>
  <StudentPageTemplate title="Online Quizzes" subtitle="Take quizzes and test your knowledge" icon="bi bi-puzzle"
    :breadcrumbs="breadcrumbs">
    <!-- Alert Message -->
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :auto-close="true"
      @close="alert.show = false" />

    <template #stats>
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <StatCard title="Available Quizzes" :value="availableQuizzes.length" icon="bi bi-journal-check"
            bg-color="bg-student-light" icon-color="text-student" />
        </div>
        <div class="col-md-4">
          <StatCard title="Completed" :value="completedCount" icon="bi bi-check-circle" bg-color="bg-success-light"
            icon-color="text-success" />
        </div>
        <div class="col-md-4">
          <StatCard title="Pending" :value="pendingCount" icon="bi bi-clock" bg-color="bg-warning-light"
            icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <div class="px-2 pt-1 pb-2">
      <SearchFilter v-model="filters.search" :show-card="false" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search quizzes..." search-col-size="col-md-5"
        actions-col-size="col-md-3" theme="student" @refresh="loadQuizzes" @reset="resetFilters">
        <template #filters>
          <div class="col-md-4">
            <SelectInput v-model="filters.subject" :options="subjectOptions" placeholder="All Subjects"
              :no-margin="true" />
          </div>
        </template>
      </SearchFilter>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" text="Loading quizzes..." theme="student" />

    <!-- Quizzes Grid -->
    <div v-else class="row g-4">
      <!-- Empty State -->
      <div v-if="availableQuizzes.length === 0" class="col-12">
        <div class="text-center py-5">
          <i class="bi bi-puzzle display-1 text-muted opacity-25"></i>
          <h5 class="mt-3 text-muted">No quizzes available</h5>
          <p class="text-muted small">Check back later for new quizzes from your teachers</p>
        </div>
      </div>

      <!-- Quiz Cards -->
      <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="col-md-6 col-lg-4">
        <div class="quiz-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
          <StudentStatusCardHeader
            :header-class="getQuizStatusClass(quiz)"
            icon-class="bi bi-puzzle"
            :badge-class="getAttemptBadgeClass(quiz)"
            :badge-text="getAttemptStatus(quiz)"
            :title-class="quiz.last_attempt?.is_completed ? 'text-success' : quiz.last_attempt ? 'text-warning' : 'text-student'"
            :subtitle-class="quiz.last_attempt?.is_completed ? 'text-success-50' : quiz.last_attempt ? 'text-warning-50' : 'text-student-50'"
          >
            <template #title>{{ quiz.title }}</template>
            <template #subtitle>
              <i class="bi bi-book me-1"></i>{{ quiz.subject_name || 'General' }}
            </template>
          </StudentStatusCardHeader>

          <!-- Card Body -->
          <div class="card-body p-4">
            <div class="quiz-meta d-flex flex-wrap gap-3 mb-3">
              <div class="meta-item">
                <i class="bi bi-list-ol text-muted me-1"></i>
                <span class="small text-muted">{{ quiz.question_count || 0 }} Questions</span>
              </div>
              <div class="meta-item">
                <i class="bi bi-clock text-muted me-1"></i>
                <span class="small text-muted">{{ quiz.time_limit_minutes || 30 }} min</span>
              </div>
              <div class="meta-item">
                <i class="bi bi-award text-muted me-1"></i>
                <span class="small text-muted">{{ quiz.total_marks || 0 }} marks</span>
              </div>
            </div>

            <!-- Previous Attempt Info -->
            <div v-if="quiz.last_attempt && quiz.last_attempt.is_completed"
              class="attempt-info p-3 rounded-3 bg-light mb-3">
              <div class="d-flex justify-content-between">
                <span class="small text-muted">Your Score:</span>
                <span class="small fw-bold text-student">
                  {{ quiz.last_attempt.score }}/{{ quiz.total_marks }}
                </span>
              </div>
            </div>

            <!-- Action Button -->
            <button class="btn w-100 rounded-3 py-2" :class="getButtonClass(quiz)" @click="startQuiz(quiz)"
              :disabled="quiz.last_attempt && quiz.last_attempt.is_completed">
              <i :class="getButtonIcon(quiz)"></i>
              {{ getButtonText(quiz) }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { StudentPageTemplate } from '@/components/shared/panels'
import { StatCard, LoadingSpinner, AlertMessage, SearchFilter, SelectInput, StudentStatusCardHeader } from '@/components/shared/common'
import studentPanelService from '@/services/student/studentPanelService'
import { useEntityList, useAlert } from '@/composables/shared'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const { alert, showAlert } = useAlert()

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Quizzes' }
]

const {
  loading,
  data: availableQuizzes,
  filteredData: filteredQuizzes,
  filters,
  loadData,
  error
} = useEntityList({
  cacheKey: 'student:quizzes',
  searchFields: ['title', 'subject_name'],
  defaultFilters: { subject: '' },
  customFilter: (items, f) => {
    let res = items
    if (f.subject) {
      res = res.filter(q => q.subject_name === f.subject)
    }
    return res
  },
  processData: (data) => data || [] // Handle null/undefined data
})

const subjectOptions = computed(() => {
  const subs = [...new Set(availableQuizzes.value.map(q => q.subject_name).filter(Boolean))]
  return subs.sort().map(s => ({ value: s, label: s }))
})

const completedCount = computed(() =>
  availableQuizzes.value.filter(q => q.last_attempt?.is_completed).length
)

const pendingCount = computed(() =>
  availableQuizzes.value.filter(q => !q.last_attempt?.is_completed).length
)


const getQuizStatusClass = (quiz) => {
  if (quiz.last_attempt?.is_completed) return 'bg-success-light'
  if (quiz.last_attempt) return 'bg-warning-light'
  return 'bg-student-light'
}

const getAttemptBadgeClass = (quiz) => {
  if (quiz.last_attempt?.is_completed) return 'bg-success text-white'
  if (quiz.last_attempt) return 'bg-warning text-white'
  return 'bg-student text-white'
}

const getAttemptStatus = (quiz) => {
  if (quiz.last_attempt?.is_completed) return 'Completed'
  if (quiz.last_attempt) return 'In Progress'
  return 'Not Started'
}

const getButtonClass = (quiz) => {
  if (quiz.last_attempt?.is_completed) return 'btn-outline-success'
  if (quiz.last_attempt) return 'btn-warning text-white'
  return 'btn-student'
}

const getButtonIcon = (quiz) => {
  if (quiz.last_attempt?.is_completed) return 'bi bi-check-lg me-2'
  if (quiz.last_attempt) return 'bi bi-play-fill me-2'
  return 'bi bi-play-fill me-2'
}

const getButtonText = (quiz) => {
  if (quiz.last_attempt?.is_completed) return 'Completed'
  if (quiz.last_attempt) return 'Continue Quiz'
  return 'Start Quiz'
}

const loadQuizzes = () => loadData(studentPanelService.getAvailableQuizzes)
const resetFilters = () => filters.value = { search: '', subject: '' }
const startQuiz = (quiz) => router.push({ name: 'StudentTakeQuiz', params: { id: quiz.id } })

onMounted(loadQuizzes)
</script>


