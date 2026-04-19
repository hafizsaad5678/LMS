<template>
  <StudentPageTemplate :title="quizTitle" icon="bi bi-puzzle" :breadcrumbs="breadcrumbs" :show-content-card="false" :show-actions="showReviewMode">
    <template #actions>
      <button v-if="showReviewMode" type="button" class="btn btn-student" @click="goBackToQuizList">
        <i class="bi bi-arrow-left me-2"></i>Back to Quizzes
      </button>
    </template>

    <LoadingSpinner v-if="loading" text="Loading quiz..." theme="student" />

    <div v-else>
      <AlertMessage
        v-if="alert.show"
        :type="alert.type"
        :message="alert.message"
        :title="alert.title"
        :auto-close="true"
        @close="alert.show = false"
      />

      <AlertMessage
        v-if="saveError"
        type="warning"
        title="Auto-save warning"
        :message="saveError"
        :auto-close="false"
      />

      <div v-if="showReviewMode" class="quiz-review-wrap">
        <div class="card border-0 shadow-sm rounded-4 mb-4">
          <div class="card-body d-flex flex-wrap justify-content-between align-items-center gap-2">
            <div>
              <h5 class="fw-bold mb-1">Quiz Review</h5>
              <small class="text-muted">Attempt status: {{ reviewData?.status || attemptState?.status }}</small>
            </div>
            <div class="text-end ms-auto">
              <div class="fw-bold text-student">Score: {{ reviewData?.score }} / {{ reviewData?.total_marks }}</div>
              <small class="text-muted">{{ percentageText }}</small>
            </div>
          </div>
        </div>

        <div v-for="(question, idx) in reviewQuestions" :key="question.id" class="card border-0 shadow-sm rounded-4 mb-3">
          <div class="card-body p-4">
            <div class="quiz-review-question-head mb-3">
              <div>
                <h6 class="mb-1 fw-bold">Question {{ idx + 1 }}</h6>
                <small class="text-muted">{{ getQuestionTypeLabel(question.question_type) }}</small>
              </div>
              <div class="quiz-review-mark-box">
                <div class="quiz-review-mark-value">{{ formatMarks(question.obtained_marks) }} / {{ formatMarks(question.marks) }}</div>
                <small class="text-muted">Marks</small>
              </div>
            </div>

            <div class="mb-3 quiz-question-text" v-html="renderRichText(question.question_text)"></div>

            <div class="quiz-answer-panels mb-3">
              <div class="quiz-answer-panel">
                <div class="small text-muted mb-1">Your answer</div>
                <div>{{ getUserAnswerText(question) }}</div>
              </div>
              <div class="quiz-answer-panel">
                <div class="small text-muted mb-1">Correct answer</div>
                <div>{{ getCorrectAnswerText(question) }}</div>
              </div>
            </div>

            <div v-if="question.question_type === 'mcq'" class="d-flex flex-column gap-2">
              <div
                v-for="opt in question.options"
                :key="opt.id"
                class="review-option"
                :class="getReviewOptionClass(question, opt.id)"
              >
                {{ opt.option_text }}
              </div>
            </div>

            <div class="quiz-explanation-box mt-3">
              <div class="small text-muted mb-1">Explanation</div>
              <div>{{ question.explanation || 'No explanation provided.' }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-else>
        <div class="card border-0 shadow-sm rounded-4 mb-4 overflow-hidden quiz-header-sticky">
          <div class="card-body p-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
              <div>
                <h4 class="fw-bold mb-1">{{ quizTitle }}</h4>
                <p class="text-muted mb-0">{{ subjectName }} | {{ questions.length }} Questions | {{ totalMarks }} Marks</p>
              </div>
              <div class="d-flex align-items-center gap-2">
                <span :class="['quiz-timer-pill', timerVariantClass]">
                  <i class="bi bi-clock me-2"></i>{{ formattedTime }}
                </span>
                <span class="badge bg-student-light text-student">Flagged: {{ flaggedCount }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-lg-8">
            <div v-if="activeQuestion" class="card border-0 shadow-sm rounded-4">
              <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <span class="badge bg-student">Question {{ currentIndex + 1 }} of {{ questions.length }}</span>
                  <span class="badge bg-light text-dark">{{ activeQuestion.marks }} marks</span>
                </div>

                <div class="mb-4 quiz-question-text" v-html="renderRichText(activeQuestion.question_text)"></div>

                <div v-if="activeQuestion.question_type === 'mcq'" class="d-flex flex-column gap-2">
                  <button
                    v-for="option in activeQuestion.options"
                    :key="option.id"
                    type="button"
                    class="btn text-start quiz-answer-btn"
                    :class="{ 'is-selected': activeState.selected_option === option.id }"
                    @click="selectOption(option.id)"
                  >
                    {{ option.option_text }}
                  </button>
                </div>

                <div v-else>
                  <textarea
                    class="form-control"
                    rows="4"
                    :value="activeState.answer_text || ''"
                    placeholder="Type your answer"
                    @input="updateTextAnswer($event.target.value)"
                  ></textarea>
                </div>
              </div>

              <div class="card-footer bg-transparent d-flex flex-wrap justify-content-between gap-2">
                <button type="button" class="btn btn-outline-warning" @click="toggleFlag">
                  <i :class="activeState.is_flagged ? 'bi bi-flag-fill me-2' : 'bi bi-flag me-2'"></i>
                  {{ activeState.is_flagged ? 'Unflag' : 'Flag Question' }}
                </button>

                <div class="d-flex gap-2">
                  <button type="button" class="btn btn-outline-secondary" :disabled="currentIndex === 0" @click="prevQuestion">Previous</button>
                  <button type="button" class="btn btn-outline-student" :disabled="currentIndex === questions.length - 1" @click="nextQuestion">Next</button>
                  <BaseButton variant="student-primary" :loading="submitting" @click="openSubmitSummary">Submit</BaseButton>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-4">
            <QuizQuestionPalette
              :questions="questions"
              :current-index="currentIndex"
              :states="answersMap"
              :flagged-count="flaggedCount"
              @jump="jumpToQuestion"
            />

            <div class="card border-0 shadow-sm mt-3">
              <div class="card-body">
                <div class="d-flex justify-content-between small mb-2"><span>Answered</span><strong>{{ answeredCount }}</strong></div>
                <div class="d-flex justify-content-between small mb-2"><span>Not Answered</span><strong>{{ Math.max(questions.length - answeredCount, 0) }}</strong></div>
                <div class="d-flex justify-content-between small"><span>Flagged</span><strong>{{ flaggedCount }}</strong></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <QuizSubmitSummaryModal
      v-model="showSubmitSummaryModal"
      :summary="submitSummary"
      :submitting="submitting"
      @confirm="submitQuiz"
    />

    <ConfirmDialog
      v-model="showLeaveConfirmDialog"
      theme="student"
      type="warning"
      title="Leave Quiz?"
      message="Quiz is in progress. Leave page? Your answers are saved but timer will continue."
      confirm-text="Leave"
      cancel-text="Stay"
      @confirm="handleConfirmLeave"
      @cancel="handleCancelLeave"
    />
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAlert } from '@/composables/shared'
import { useQuizAttempt } from '@/composables/student/useQuizAttempt'
import { useQuizReview } from '@/composables/student/useQuizReview'
import { useQuizSessionGuards } from '@/composables/student/useQuizSessionGuards'
import studentPanelService from '@/services/student/studentPanelService'
import { StudentPageTemplate } from '@/components/shared/panels'
import { LoadingSpinner, BaseButton, AlertMessage, QuizQuestionPalette, QuizSubmitSummaryModal, ConfirmDialog } from '@/components/shared/common'
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { sanitizeRichHtml } from '@/utils/security'

const route = useRoute()
const router = useRouter()
const quizId = route.params.id
const loading = ref(true)
const currentIndex = ref(0)
const showSubmitSummaryModal = ref(false)
const showLeaveConfirmDialog = ref(false)
const submitSummary = ref({ total_questions: 0, answered: 0, not_answered: 0, flagged: 0 })
const reviewData = ref(null)
let leaveConfirmResolver = null

const { alert, showError } = useAlert()
const {
  QUIZ_STATUSES,
  attemptId,
  attemptState,
  answersMap,
  saveError,
  submitting,
  flaggedCount,
  answeredCount,
  setAttemptState,
  getQuestionState,
  patchQuestionState,
  scheduleAutosave,
  flushAllSaves,
  submitAttempt
} = useQuizAttempt()
const {
  formatMarks,
  getQuestionTypeLabel,
  getUserAnswerText,
  getCorrectAnswerText,
  getReviewOptionClass
} = useQuizReview()

const submitQuiz = async () => {
  showSubmitSummaryModal.value = false
  try {
    const submitted = await submitAttempt()
    if (!submitted) return

    stopTimer()
    reviewData.value = await studentPanelService.getQuizReview(attemptId.value)
  } catch (error) {
    showError('Submission failed due to network issue. Please try again.', 'Submit Failed')
  }
}

const breadcrumbs = [{ name: 'Quizzes', href: STUDENT_ROUTES.QUIZ_LIST.path }, { name: 'Take Quiz' }]

const quizTitle = computed(() => attemptState.value?.quiz?.title || 'Take Quiz')
const subjectName = computed(() => attemptState.value?.quiz?.subject_name || 'Subject')
const questions = computed(() => attemptState.value?.quiz?.questions || [])
const totalMarks = computed(() => attemptState.value?.quiz?.total_marks || 0)
const activeQuestion = computed(() => questions.value[currentIndex.value] || null)
const activeState = computed(() => {
  if (!activeQuestion.value) return { selected_option: null, answer_text: '', is_flagged: false, status: QUIZ_STATUSES.NOT_VISITED }
  return getQuestionState(activeQuestion.value.id)
})
const showReviewMode = computed(() => Boolean(reviewData.value) || attemptState.value?.status === 'evaluated')
const reviewQuestions = computed(() => reviewData.value?.questions || [])
const percentageText = computed(() => {
  if (!reviewData.value?.total_marks) return 'Percentage: 0%'
  const pct = (Number(reviewData.value.score || 0) / Number(reviewData.value.total_marks || 1)) * 100
  return `Percentage: ${pct.toFixed(0)}%`
})

const renderRichText = (content) => sanitizeRichHtml(content || '')

const requestLeaveConfirmation = () => {
  showLeaveConfirmDialog.value = true
  return new Promise((resolve) => {
    leaveConfirmResolver = resolve
  })
}

const resolveLeaveDecision = (decision) => {
  showLeaveConfirmDialog.value = false
  if (leaveConfirmResolver) {
    leaveConfirmResolver(decision)
    leaveConfirmResolver = null
  }
}

const handleConfirmLeave = () => {
  resolveLeaveDecision(true)
}

const handleCancelLeave = () => {
  resolveLeaveDecision(false)
}

const {
  timeRemaining,
  formattedTime,
  timerVariantClass,
  setTimeRemaining,
  startTimer,
  stopTimer
} = useQuizSessionGuards({
  showReviewMode,
  submitting,
  flushAllSaves,
  showError,
  onAutoSubmit: submitQuiz,
  requestLeaveConfirmation
})

const setVisitedIfNeeded = () => {
  if (!activeQuestion.value) return

  const current = getQuestionState(activeQuestion.value.id)
  if (current.status === QUIZ_STATUSES.NOT_VISITED) {
    patchQuestionState(activeQuestion.value.id, { status: QUIZ_STATUSES.VISITED })
    scheduleAutosave(activeQuestion.value.id)
  }
}

const loadQuiz = async () => {
  try {
    let state = await studentPanelService.startQuiz(quizId)

    // Defensive sync: if start returns an in-progress attempt with no time left,
    // refresh authoritative state from server before starting timer.
    if (state?.id && state?.status === 'in_progress' && Number(state?.time_remaining_seconds || 0) <= 0) {
      state = await studentPanelService.getQuizAttemptState(state.id)
    }

    setAttemptState(state)
    setTimeRemaining(state.time_remaining_seconds)

    if (state.status === 'evaluated') {
      reviewData.value = await studentPanelService.getQuizReview(state.id)
      return
    }

    setVisitedIfNeeded()
    startTimer()
  } catch (error) {
    showError('Unable to load quiz attempt. Please try again.', 'Quiz Error')
    router.push(STUDENT_ROUTES.QUIZ_LIST.path)
  } finally {
    loading.value = false
  }
}

const goBackToQuizList = () => {
  router.push(STUDENT_ROUTES.QUIZ_LIST.path)
}

const selectOption = (optionId) => {
  if (!activeQuestion.value) return

  patchQuestionState(activeQuestion.value.id, {
    selected_option: optionId,
    status: QUIZ_STATUSES.ANSWERED
  })
  scheduleAutosave(activeQuestion.value.id)
}

const updateTextAnswer = (value) => {
  if (!activeQuestion.value) return

  patchQuestionState(activeQuestion.value.id, {
    answer_text: value,
    status: value.trim() ? QUIZ_STATUSES.ANSWERED : QUIZ_STATUSES.VISITED
  })
  scheduleAutosave(activeQuestion.value.id, 1200)
}

const toggleFlag = () => {
  if (!activeQuestion.value) return

  patchQuestionState(activeQuestion.value.id, { is_flagged: !activeState.value.is_flagged })
  scheduleAutosave(activeQuestion.value.id)
}

const jumpToQuestion = (index) => {
  currentIndex.value = index
  setVisitedIfNeeded()
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value += 1
    setVisitedIfNeeded()
  }
}

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
    setVisitedIfNeeded()
  }
}

const openSubmitSummary = async () => {
  try {
    await flushAllSaves()
    submitSummary.value = await studentPanelService.getQuizAttemptSummary(attemptId.value)
    showSubmitSummaryModal.value = true
  } catch (error) {
    showError('Unable to load submission summary.', 'Summary Error')
  }
}

onMounted(async () => {
  await loadQuiz()
})
</script>
