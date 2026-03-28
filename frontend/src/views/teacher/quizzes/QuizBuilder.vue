<template>
  <TeacherPageTemplate :title="isEditing ? 'Edit Quiz' : 'Quiz Builder'"
    :subtitle="isEditing ? 'Update quiz content and settings' : 'Create an interactive MCQ or short answer quiz'"
    icon="bi bi-puzzle" :breadcrumbs="breadcrumbs">
    <!-- Alert Message -->
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true"
      @close="alert.show = false" />

    <!-- Confirm Dialog -->
    <ConfirmDialog v-model="confirmDialog.show" :title="confirmDialog.title" :message="confirmDialog.message"
      :confirm-text="confirmDialog.confirmText" :type="confirmDialog.type" @confirm="onConfirm"
      @cancel="confirmDialog.show = false" />

    <LoadingSpinner v-if="loading" text="Loading quiz builder..." theme="teacher" />

    <div v-else class="row g-4">
      <!-- Main Content: Questions -->
      <div class="col-lg-8">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h4 class="fw-bold text-dark m-0">Questions ({{ questions.length }})</h4>
          <div class="d-flex gap-2">
            <button class="btn btn-teacher-light btn-sm rounded-3 px-3" @click="addQuestion('mcq')">
              <i class="bi bi-list-check me-2"></i>Add MCQ
            </button>
            <button class="btn btn-teacher-light btn-sm rounded-3 px-3" @click="addQuestion('short_answer')">
              <i class="bi bi-chat-left-text me-2"></i>Add Answer
            </button>
          </div>
        </div>

        <div v-if="questions.length === 0"
          class="text-center py-5 quiz-card bg-white shadow-sm border border-dashed hover-translate-y">
          <i class="bi bi-journals display-1 text-muted opacity-25"></i>
          <h5 class="mt-3 text-teacher fw-bold">No questions added yet</h5>
          <p class="text-muted small">Start by adding an MCQ or Short Answer question</p>
          <button class="btn btn-teacher rounded-pill px-4 fw-bold shadow-sm" @click="addQuestion('mcq')">
            Create First Question
          </button>
        </div>

        <div v-else class="d-flex flex-column gap-4">
          <div v-for="(q, qIndex) in questions" :key="q.tempId"
            class="quiz-card question-item shadow-sm border-0 bg-white hover-translate-y">
            <div class="card-body p-4">
              <!-- Question Header -->
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="d-flex align-items-center gap-3">
                  <div class="question-number">{{ qIndex + 1 }}</div>
                  <span :class="['type-badge', q.type === 'mcq' ? 'type-mcq' : 'type-answer']">
                    {{ q.type === 'mcq' ? 'Multiple Choice' : 'Short Answer' }}
                  </span>
                </div>
                <div class="d-flex gap-1">
                  <button class="btn btn-link text-danger p-1 ms-2" title="Remove"
                    @click="handleRemoveQuestion(qIndex)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>

              <!-- Question Text Editor -->
              <div class="mb-4">
                <label class="form-label fw-bold small text-muted">QUESTION TEXT</label>
                <RichTextEditor v-model="q.text" placeholder="Enter your question here..." min-height="100px" />
              </div>

              <!-- Options for MCQ -->
              <div v-if="q.type === 'mcq'" class="mb-4">
                <label class="form-label fw-bold small text-muted">OPTIONS & CORRECT ANSWER</label>
                <div class="d-flex flex-column gap-2">
                  <div v-for="(opt, oIndex) in q.options" :key="oIndex"
                    class="quiz-option-row d-flex align-items-center gap-3 border shadow-sm"
                    :class="{ 'is-correct': opt.isCorrect }">
                    <input type="radio" :name="'correct-' + q.tempId"
                      class="option-radio form-check-input quiz-check mt-0" :checked="opt.isCorrect"
                      @change="setCorrectOption(qIndex, oIndex)">
                    <input v-model="opt.text" type="text" class="form-control border-0 bg-transparent py-2 fw-medium"
                      placeholder="Enter option detail here...">
                    <button v-if="q.options.length > 2" class="btn btn-link text-danger p-0 fs-5"
                      @click="removeOption(qIndex, oIndex)">
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>
                <button class="btn btn-teacher-light fw-bold rounded-pill px-4 mt-3 hover-lift shadow-sm"
                  @click="addOption(qIndex)">
                  <i class="bi bi-plus me-1"></i> Add Option
                </button>
              </div>

              <!-- Correct Answer for Short Answer -->
              <div v-if="q.type === 'short_answer'" class="mb-4">
                <label class="form-label fw-bold small text-teacher ls-1 text-uppercase">CORRECT ANSWER KEY</label>
                <input v-model="q.correctAnswer" type="text" class="form-control quiz-input bg-light border-0 fw-bold"
                  placeholder="The exact answer expected (not case sensitive)...">
              </div>

              <!-- Marks & Explanation -->
              <div class="row g-3">
                <div class="col-md-3">
                  <label class="form-label fw-bold small text-muted">MARKS</label>
                  <input v-model.number="q.marks" type="number" class="form-control rounded-3" min="1">
                </div>
                <div class="col-md-9">
                  <label class="form-label fw-bold small text-muted">EXPLANATION (OPTIONAL)</label>
                  <input v-model="q.explanation" type="text" class="form-control rounded-3"
                    placeholder="Explain why the answer is correct...">
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar: Quiz Settings -->
      <div class="col-lg-4">
        <div class="quiz-preview-container position-sticky" style="top: 100px;">
          <div class="quiz-card quiz-glass-panel shadow-sm border-0 mb-4 overflow-hidden">
            <div class="bg-teacher p-4 text-white">
              <h5 class="fw-extrabold m-0"><i class="bi bi-gear-fill me-2"></i>Quiz Settings</h5>
            </div>
            <div class="card-body p-4 bg-white">
              <div class="mb-3">
                <label class="form-label fw-bold small text-muted">QUIZ TITLE</label>
                <input v-model="quizData.title" type="text" class="form-control rounded-3 p-3 bg-light border-0"
                  placeholder="e.g. Midterm Quiz - Unit 1">
              </div>

              <div class="mb-3">
                <SelectInput v-model="quizData.subject" :options="subjects" label="SUBJECT" placeholder="Select Subject"
                  label-class="fw-bold small text-muted" :no-margin="true" />
              </div>

              <div class="row g-3 mb-4">
                <div class="col-6">
                  <label class="form-label fw-bold small text-teacher text-uppercase ls-1">TIME LIMIT</label>
                  <div class="input-group">
                    <input v-model.number="quizData.timeLimit" type="number"
                      class="form-control quiz-input rounded-start-3 bg-light border-0 fw-bold">
                    <span class="input-group-text bg-light border-0 small fw-bold">MIN</span>
                  </div>
                </div>
                <div class="col-6">
                  <label class="form-label fw-bold small text-teacher text-uppercase ls-1">TOTAL MARKS</label>
                  <div
                    class="form-control quiz-input bg-light border-0 text-center fw-extrabold text-teacher d-flex align-items-center justify-content-center">
                    {{ totalQuizMarks }}
                  </div>
                </div>
              </div>

              <hr class="my-4 opacity-10">

              <div class="d-grid gap-2">
                <button class="btn btn-teacher py-3 rounded-3 fw-bold shadow-sm" :disabled="saving"
                  @click="saveQuiz(true)">
                  <i class="bi bi-cloud-check me-2"></i> {{ isEditing ? 'Update & Publish' : 'Save & Publish' }}
                </button>
                <button class="btn btn-teacher-light py-3 rounded-3 fw-bold" :disabled="saving"
                  @click="saveQuiz(false)">
                  <i class="bi bi-save me-2"></i> Save as Draft
                </button>
                <button class="btn btn-light py-3 rounded-3 text-muted" @click="router.back()">
                  Cancel
                </button>
              </div>
            </div>
          </div>

          <!-- Tips Card -->
          <div class="card bg-teacher-light border-0 rounded-4">
            <div class="card-body p-4">
              <h6 class="fw-bold text-teacher mb-3">
                <i class="bi bi-lightbulb me-2"></i>Quick Tips
              </h6>
              <ul class="small text-muted mb-0 ps-3">
                <li class="mb-2"><b>Auto-Grading:</b> MCQs are automatically graded upon submission.</li>
                <li class="mb-2"><b>Rich Text:</b> Use the text editor to add math formulas, bold text, or lists.</li>
                <li><b>Accessibility:</b> Keep answer keys short and simple for short answer questions.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { RichTextEditor, LoadingSpinner, SelectInput, AlertMessage, ConfirmDialog } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { useAlert } from '@/composables/shared'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import '@/assets/css/ai-generator.css'

const router = useRouter()
const route = useRoute()
const { alert, showAlert } = useAlert()

const isEditing = computed(() => !!route.params.id)
const saving = ref(false)
const loading = ref(true)
const subjects = ref([])
const confirmDialog = ref({ show: false, title: '', message: '', confirmText: 'Confirm', type: 'warning', action: null })
const quizData = ref({ title: '', subject: '', timeLimit: 30 })
const questions = ref([])
const deletedQuestionIds = ref([])

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Quizzes', href: TEACHER_ROUTES.QUIZ_LIST.path },
  { name: 'Builder' }
]

const totalQuizMarks = computed(() => questions.value.reduce((sum, q) => sum + (Number(q.marks) || 0), 0))

const addQuestion = (type) => {
  questions.value.push({
    tempId: Date.now() + Math.random(), type, text: '', marks: 1, explanation: '', correctAnswer: '',
    options: type === 'mcq' ? [{ text: '', isCorrect: true }, { text: '', isCorrect: false }, { text: '', isCorrect: false }, { text: '', isCorrect: false }] : []
  })
}

const handleRemoveQuestion = (index) => {
  confirmDialog.value = {
    show: true,
    title: 'Remove Question',
    message: 'Are you sure you want to remove this question?',
    confirmText: 'Remove',
    type: 'danger',
    action: () => {
      const q = questions.value[index]
      if (q.id) deletedQuestionIds.value.push(q.id)
      questions.value.splice(index, 1)
      confirmDialog.value.show = false
    }
  }
}

const onConfirm = () => { if (confirmDialog.value.action) confirmDialog.value.action() }
const addOption = (qIndex) => { questions.value[qIndex].options.push({ text: '', isCorrect: false }) }
const removeOption = (qIndex, oIndex) => { questions.value[qIndex].options.splice(oIndex, 1); if (!questions.value[qIndex].options.some(o => o.isCorrect)) questions.value[qIndex].options[0].isCorrect = true }
const setCorrectOption = (qIndex, oIndex) => { questions.value[qIndex].options.forEach((opt, idx) => { opt.isCorrect = idx === oIndex }) }

const saveQuiz = async (publish = false) => {
  if (!quizData.value.title || !quizData.value.subject) { showAlert('warning', 'Please fill in the quiz title and select a subject.'); return }
  if (questions.value.length === 0) { showAlert('warning', 'Please add at least one question.'); return }

  saving.value = true
  try {
    const payload = { title: quizData.value.title, subject: quizData.value.subject, time_limit_minutes: quizData.value.timeLimit, total_marks: totalQuizMarks.value, is_published: publish }
    let quizId = route.params.id
    if (isEditing.value) await teacherPanelService.updateQuiz(quizId, payload)
    else { const newQuiz = await teacherPanelService.createQuiz(payload); quizId = newQuiz.id }

    // Save current questions
    for (const [index, q] of questions.value.entries()) {
      const qPayload = { quiz: quizId, question_text: q.text, question_type: q.type, marks: q.marks, correct_answer_text: q.correctAnswer || '', explanation: q.explanation, order: index, options: q.type === 'mcq' ? q.options.map(o => ({ option_text: o.text, is_correct: o.isCorrect })) : [] }
      if (q.id) await teacherPanelService.updateQuizQuestion(q.id, qPayload)
      else await teacherPanelService.addQuizQuestion(qPayload)
    }

    // Process deletions
    if (deletedQuestionIds.value.length > 0) {
      await Promise.all(deletedQuestionIds.value.map(id => teacherPanelService.deleteQuizQuestion(id)))
      deletedQuestionIds.value = []
    }
    showAlert('success', `Quiz ${isEditing.value ? 'updated' : 'created'} successfully!`)
    setTimeout(() => router.push({ name: 'TeacherQuizList' }), 1500)
  } catch (error) { showAlert('error', 'Failed to save quiz. Please ensure all fields are correct.') }
  finally { saving.value = false }
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await teacherPanelService.getMyClasses()
    subjects.value = (response.results || response || []).map(c => ({ value: c.subject_id || c.id, label: `${c.subject_name} (${c.subject_code})` }))
    if (isEditing.value) {
      const data = await teacherPanelService.getQuizDetails(route.params.id)
      quizData.value = { title: data.title, subject: data.subject, timeLimit: data.time_limit_minutes }
      questions.value = (data.questions || []).map(q => ({ id: q.id, tempId: Math.random(), type: q.question_type, text: q.question_text, marks: q.marks, explanation: q.explanation, options: (q.options || []).map(o => ({ text: o.option_text, isCorrect: o.is_correct })), correctAnswer: q.correct_answer_text || '' }))
    }
  } catch (error) { /* silent */ }
  finally { loading.value = false }
})
</script>
