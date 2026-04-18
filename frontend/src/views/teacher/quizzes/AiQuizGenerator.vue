<template>
    <TeacherPageTemplate title="AI Quiz Generation"
        subtitle="Harnessing artificial intelligence to curate world-class assessments in seconds." icon="bi bi-stars"
        :breadcrumbs="breadcrumbs">
        <!-- Premium Alert -->
        <AlertMessage v-if="alert.show" v-bind="alert" @close="alert.show = false"
            class="animate__animated animate__slideInDown" />

        <!-- Progress Journey -->
        <div class="mb-5 py-4">
            <div class="quiz-stepper w-100">
                <div v-for="s in [1, 2]" :key="s" class="quiz-step"
                    :class="{ 'active': step === s, 'completed': step > s }">
                    <div class="quiz-step-icon">
                        <i v-if="step > s" class="bi bi-check-lg"></i>
                        <span v-else>{{ s }}</span>
                    </div>
                    <span class="quiz-step-title">{{ s === 1 ? 'Design' : 'Review' }}</span>
                </div>
            </div>
        </div>

        <!-- Step 1: Design Phase -->
        <div v-if="step === 1" class="row justify-content-center animate__animated animate__fadeIn">
            <div class="col-lg-8 col-xl-7">
                <div class="quiz-card shadow-lg border-0">
                    <div class="mb-4 text-center">
                        <div class="avatar-circle-teacher bg-teacher-light text-teacher mx-auto mb-3"
                            style="width: 60px; height: 60px;">
                            <i class="bi bi-bezier2 fs-3"></i>
                        </div>
                        <h4 class="fw-extrabold m-0">Define Scope</h4>
                        <p class="text-muted small">Specify the parameters for your AI-generated assessment.</p>
                    </div>

                    <div class="d-flex flex-column gap-3 px-2">
                        <!-- Topic Input -->
                        <div>
                            <label class="form-label small fw-bold text-muted ls-1">TOPIC OF INTEREST</label>
                            <input v-model="form.topic" type="text" class="form-control quiz-input"
                                placeholder="e.g. Quantum Mechanics or 18th Century Art">
                        </div>

                        <!-- Basic Fields Row -->
                        <div class="row g-3">
                            <div class="col-md-12">
                                <label class="form-label small fw-bold text-muted ls-1">SUBJECT</label>
                                <select v-model="form.subject_id" class="form-select quiz-input border-0 bg-light">
                                    <option value="" disabled>Select Subject</option>
                                    <option v-for="s in subjects" :key="s.subject_id" :value="s.subject_id">{{
                                        s.subject_name }}
                                    </option>
                                </select>
                            </div>
                        </div>

                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-muted ls-1">QUESTIONS</label>
                                <input v-model.number="form.num_questions" type="number"
                                    class="form-control quiz-input border-0 bg-light" placeholder="Count">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-muted ls-1">DIFFICULTY</label>
                                <select v-model="form.difficulty" class="form-select quiz-input border-0 bg-light">
                                    <option value="Easy">Easy</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Hard">Hard</option>
                                </select>
                            </div>
                        </div>

                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-muted ls-1">TYPE</label>
                                <select v-model="form.question_type" class="form-select quiz-input border-0 bg-light">
                                    <option value="MCQ">Multiple Choice</option>
                                    <option value="Short Answer">Short Answer</option>
                                    <option value="Long Answer">Long Answer</option>
                                    <option value="Mixed">Mixed Format</option>
                                </select>
                            </div>
                            <div class="col-md-6 d-flex align-items-center">
                                <div class="form-check form-switch mt-4">
                                    <input class="form-check-input" type="checkbox" v-model="form.include_explanation"
                                        id="expSwitch">
                                    <label class="form-check-label small fw-bold" for="expSwitch">Include
                                        Explanations</label>
                                </div>
                            </div>
                        </div>

                        <!-- Mixed Format Inputs -->
                        <div v-if="form.question_type === 'Mixed'"
                            class="p-4 bg-white rounded-4 border shadow-sm animate__animated animate__fadeIn">
                            <div class="d-flex justify-content-between align-items-center mb-4">
                                <label class="form-label small fw-bold text-muted ls-1 mb-0">MIXED COMPOSITION</label>
                                <span class="badge bg-teacher-light text-teacher rounded-pill px-3 py-1 fw-extrabold"
                                    :class="{ 'bg-danger-subtle text-danger': mixedTotal !== form.num_questions }">
                                   TOTAL: {{ mixedTotal }}
                                   <template v-if="mixedTotal !== form.num_questions"> / {{ form.num_questions }}</template>
                                </span>
                            </div>

                            <div class="row g-3">
                                <div class="col-4">
                                    <div class="composition-card p-3 rounded-4 border bg-light text-center transition-all hover-translate-y">
                                        <i class="bi bi-list-check d-block mb-2 text-primary fs-5"></i>
                                        <label class="x-small fw-bold text-muted text-uppercase mb-2 d-block">MCQ</label>
                                        <input v-model.number="form.mixed_counts.mcq" type="number" min="0"
                                            class="form-control form-control-sm border-0 bg-white text-center fw-bold rounded-3 shadow-none no-arrows">
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="composition-card p-3 rounded-4 border bg-light text-center transition-all hover-translate-y">
                                        <i class="bi bi-chat-left-text d-block mb-2 text-success fs-5"></i>
                                        <label class="x-small fw-bold text-muted text-uppercase mb-2 d-block">Short</label>
                                        <input v-model.number="form.mixed_counts.short" type="number" min="0"
                                            class="form-control form-control-sm border-0 bg-white text-center fw-bold rounded-3 shadow-none no-arrows">
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="composition-card p-3 rounded-4 border bg-light text-center transition-all hover-translate-y">
                                        <i class="bi bi-file-earmark-text d-block mb-2 text-warning fs-5"></i>
                                        <label class="x-small fw-bold text-muted text-uppercase mb-2 d-block">Long</label>
                                        <input v-model.number="form.mixed_counts.long" type="number" min="0"
                                            class="form-control form-control-sm border-0 bg-white text-center fw-bold rounded-3 shadow-none no-arrows">
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div v-if="form.question_type === 'Mixed' && mixedTotal !== form.num_questions"
                            class="alert alert-warning border-0 rounded-4 py-2 px-3 mb-0 small fw-bold d-flex align-items-center gap-2 animate__animated animate__shakeX">
                            <i class="bi bi-exclamation-triangle-fill"></i>
                            Mixed composition total ({{ mixedTotal }}) must equal the question count ({{ form.num_questions }}).
                        </div>


                        <button @click="handleGenerateManual" :disabled="loading || (form.question_type === 'Mixed' && mixedTotal !== form.num_questions)"
                            class="btn btn-teacher-primary btn-lg mt-3 py-3 rounded-pill fw-bold shadow-lg transition-all hover-translate-y">
                            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                            {{ loading ? 'Generating Quiz...' : 'Generate Quiz Here' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Step 2: Synthesis Review & Assignment -->
        <div v-if="step === 2" class="row g-4 animate__animated animate__fadeIn px-xl-5">
            <div class="col-12 mb-2">
                <button @click="step = 1" class="btn btn-outline-secondary rounded-pill px-4 py-2 fw-bold shadow-sm">
                    <i class="bi bi-arrow-left me-2"></i>Back to Design
                </button>
            </div>
            <div class="col-lg-8">
                <div class="mb-4 d-flex align-items-center justify-content-between">
                    <div>
                        <h4 class="fw-extrabold m-0">Quiz Blueprint</h4>
                        <p class="text-muted small m-0">Review and refine the generated items.</p>
                    </div>
                    <div class="d-flex gap-2 align-items-center">
                        <button @click="copyToClipboard"
                            class="btn btn-outline-secondary rounded-4 btn-sm fw-bold px-3 py-2 d-flex flex-column align-items-center lh-1 border"
                            style="min-width: 65px;">
                            <i class="bi bi-clipboard mb-2 fs-6"></i>
                            <span style="font-size: 0.75rem;">Copy</span>
                        </button>
                        <button @click="downloadPDF"
                            class="btn btn-outline-secondary rounded-4 btn-sm fw-bold px-3 py-2 d-flex flex-column align-items-center lh-1 border"
                            style="min-width: 65px;">
                            <i class="bi bi-file-pdf mb-2 fs-6"></i>
                            <span style="font-size: 0.75rem;">PDF</span>
                        </button>
                        <button @click="downloadJSON"
                            class="btn btn-outline-secondary rounded-4 btn-sm fw-bold px-3 py-2 d-flex flex-column align-items-center lh-1 border"
                            style="min-width: 65px;">
                            <i class="bi bi-code-slash mb-2 fs-6"></i>
                            <span style="font-size: 0.75rem;">JSON</span>
                        </button>
                        <button @click="downloadTXT"
                            class="btn btn-outline-secondary rounded-4 btn-sm fw-bold px-3 py-2 d-flex flex-column align-items-center lh-1 border"
                            style="min-width: 65px;">
                            <i class="bi bi-file-text mb-2 fs-6"></i>
                            <span style="font-size: 0.75rem;">TXT</span>
                        </button>
                        <button @click="addQuestion"
                            class="btn btn-link text-dark text-decoration-none fw-bold p-0 ms-2 d-flex flex-column align-items-center lh-sm bg-transparent border-0"
                            style="font-size: 0.85rem;">
                            <span>+ Manual</span>
                            <span>Slot</span>
                        </button>
                    </div>
                </div>

                <div v-if="quiz && (!quiz.questions || quiz.questions.length === 0)"
                    class="alert alert-info border-0 shadow-sm rounded-4 mb-4">
                    <div class="d-flex align-items-center gap-3">
                        <i class="bi bi-info-circle-fill fs-4 text-info"></i>
                        <div style="max-width: 100%; overflow: hidden;">
                            <div class="fw-bold">Debug Information</div>
                            <div class="small opacity-75 text-truncate">Keys: {{ Object.keys(quiz) }}</div>
                            <div class="x-small mt-1 opacity-50" style="font-size: 10px;">{{
                                JSON.stringify(quiz).substring(0, 100) }}...</div>
                        </div>
                    </div>
                </div>

                <div v-if="!quiz?.questions || quiz.questions.length === 0"
                    class="text-center py-5 bg-light rounded-4 border-dashed">
                    <i class="bi bi-inbox fs-1 text-muted d-block mb-3"></i>
                    <p class="text-muted fw-bold">No questions synthesized yet.</p>
                    <button @click="addQuestion" class="btn btn-sm btn-teacher-primary rounded-pill">Add Question
                        Manually</button>
                </div>

                <div v-for="(q, i) in quiz?.questions" :key="i"
                    class="question-item shadow-sm p-4 mb-4 border-0 animate__animated animate__fadeInUp"
                    :style="{ animationDelay: (i * 0.1) + 's' }">
                    <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-light">
                        <div class="d-flex align-items-center gap-3">
                            <div class="avatar-circle sm bg-primary text-white fw-bold shadow-sm">{{ i + 1 }}</div>
                            <select
                                v-model="q.question_type"
                                @change="onQuestionTypeChange(q)"
                                class="form-select form-select-sm rounded-pill fw-bold border bg-light"
                                style="width: 180px;"
                            >
                                <option value="MCQ">Multiple Choice</option>
                                <option value="Short Answer">Short Answer</option>
                                <option value="Long Answer">Long Answer</option>
                            </select>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <div class="d-flex align-items-center bg-light px-2 rounded-3">
                                <span class="small fw-bold text-muted me-2">PTS</span>
                                <input type="number" v-model.number="q.marks"
                                    class="form-control text-center fw-bold border-0 bg-transparent p-1"
                                    style="width: 50px;">
                            </div>
                            <button @click="regenerateQuestion(i)" class="btn btn-link text-info p-0 fs-5"
                                title="Regenerate this question"><i class="bi bi-arrow-clockwise"></i></button>
                            <button @click="removeQuestion(i)" class="btn btn-link text-danger p-0 fs-5"
                                title="Remove question"><i class="bi bi-trash"></i></button>
                        </div>
                    </div>

                    <div class="mb-4">
                        <textarea v-model="q.question_text" class="form-control quiz-input fw-bold fs-5" rows="2"
                            placeholder="Describe the question..."></textarea>
                    </div>

                    <div v-if="isMcqType(q.question_type)" class="row g-3">
                        <div v-for="(o, oi) in q.options" :key="oi" class="col-md-6">
                            <div class="quiz-option-row d-flex align-items-center gap-2 border-0 shadow-sm"
                                :class="{ 'is-correct': o.is_correct }">
                                <input type="radio" :name="'q' + i" :checked="o.is_correct" @change="setCorrect(i, oi)"
                                    class="form-check-input mt-0 custom-check">
                                <input v-model="o.text"
                                    class="form-control form-control-sm border-0 bg-transparent py-0 fw-medium"
                                    placeholder="Option source...">
                            </div>
                        </div>
                    </div>

                    <div v-else class="mt-3">
                        <label class="form-label small fw-bold text-muted">Expected Answer</label>
                        <textarea
                            v-model="q.correct_answer_text"
                            class="form-control quiz-input"
                            rows="2"
                            placeholder="Enter expected answer..."
                        ></textarea>
                    </div>

                    <div v-if="q.explanation" class="mt-4 p-4 rounded-4"
                        style="background: rgba(var(--teacher-primary-rgb), 0.05); border: 1px dashed rgba(var(--teacher-primary-rgb), 0.2);">
                        <span class="fw-bold text-teacher d-block mb-2 small text-uppercase ls-1">
                            <i class="bi bi-lightbulb-fill me-2 fs-6"></i> AI Explanation
                        </span>
                        <textarea v-model="q.explanation"
                            class="form-control border-0 bg-transparent p-0 text-dark fw-medium fs-6"
                            rows="2"></textarea>
                    </div>
                </div>
            </div>

            <!-- Deployment Sidebar -->
            <div class="col-lg-4">
                <div class="sticky-top" style="top: 100px;">
                    <div class="quiz-card quiz-glass-panel border-0 shadow-xl p-4">
                        <h5 class="fw-extrabold mb-4 pb-2 border-bottom">Assignment Matrix</h5>

                        <div class="mb-4">
                            <label class="form-label small fw-bold text-muted text-uppercase mb-2">Internal
                                Designation</label>
                            <input v-model="quiz.title" class="form-control ai-input border-0 shadow-sm p-3">
                        </div>

                        <div class="mb-4">
                            <label class="form-label small fw-bold text-muted text-uppercase mb-2">Assign Mode</label>
                            <select v-model="form.assign_mode" class="form-select ai-input border-0 shadow-sm bg-light">
                                <option value="subject">Subject Wise</option>
                                <option value="students">Selected Students</option>
                            </select>
                        </div>

                        <div v-if="form.assign_mode === 'subject'" class="mb-4 animate__animated animate__fadeIn">
                            <label class="form-label small fw-bold text-muted text-uppercase mb-2">Confirm Your
                                Subject</label>
                            <select v-model="form.subject_id" class="form-select ai-input border-0 shadow-sm bg-light">
                                <option v-for="s in subjects" :key="s.subject_id" :value="s.subject_id">{{
                                    s.subject_name }}</option>
                            </select>
                        </div>

                        <div v-if="form.assign_mode === 'students'" class="mb-4 animate__animated animate__fadeIn">
                            <label class="form-label small fw-bold text-muted text-uppercase mb-2">Select
                                Students</label>
                            <div class="student-select-box border rounded-4 p-2 bg-light shadow-sm overflow-auto"
                                style="max-height: 150px;">
                                <div v-for="s in filteredStudents" :key="s.id" class="form-check small mb-1">
                                    <input class="form-check-input" type="checkbox" :value="s.id"
                                        v-model="form.selectedStudents" :id="'st' + s.id">
                                    <label class="form-check-label" :for="'st' + s.id">{{ s.full_name }}</label>
                                </div>
                                <div v-if="!filteredStudents || filteredStudents.length === 0"
                                    class="text-muted small p-2 text-center">
                                    No students available.
                                </div>
                            </div>
                        </div>

                        <div class="mb-4">
                            <label class="form-label small fw-bold text-muted text-uppercase mb-2">Deadline</label>
                            <VueDatePicker v-model="form.deadline" :format="'yyyy-MM-dd HH:mm'" :dark="false" :text-input="false"
                                placeholder="Select Submission Deadline" class="quiz-datepicker" />
                        </div>

                        <div
                            class="bg-primary bg-opacity-10 p-4 rounded-4 mb-4 border border-teacher border-opacity-10">
                            <div class="d-flex justify-content-between mb-3">
                                <div class="text-muted small fw-bold">TOTAL ITEMS</div>
                                <div class="fs-5 fw-extrabold text-teacher">{{ quiz?.questions?.length || 0 }}</div>
                            </div>
                            <div
                                class="d-flex justify-content-between m-0 pt-3 border-top border-teacher border-opacity-20">
                                <div class="text-muted small fw-bold">CREDIT QUOTA</div>
                                <div class="fs-3 fw-extrabold text-teacher">{{ totalMarks }}</div>
                            </div>
                        </div>

                        <div class="d-grid gap-3">
                            <button @click="handleSave" :disabled="saving"
                                class="btn btn-teacher-primary w-100 py-3 rounded-4 fw-extrabold shadow-lg transition-all hover-scale-105">
                                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                                {{ saving ? 'Deploying...' : 'Save & Assign Quiz' }}
                            </button>
                        </div>
                    </div>

                    <div class="mt-4 p-4 rounded-4 bg-dark text-white shadow-lg animate__animated animate__fadeInUp">
                        <div class="d-flex align-items-center gap-2 mb-2">
                            <i class="bi bi-lightning-charge-fill text-warning"></i>
                            <span class="small fw-bold">PRO TIP</span>
                        </div>
                        <p class="small text-white-50 m-0">Questions with explanations lead to 40% higher student
                            comprehension. Consider adding them to manual slots.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- System Intelligence Overlay -->
        <div v-if="loading"
            class="position-fixed top-0 start-0 w-100 h-100 bg-white bg-opacity-90 d-flex align-items-center justify-content-center"
            style="z-index: 9999; backdrop-filter: blur(8px);">
            <div class="text-center">
                <div class="spinner-grow text-teacher mb-4" style="width: 3rem; height: 3rem;"
                    role="status text-teacher"></div>
                <h4 class="fw-extrabold m-0">{{ loadingText }}</h4>
                <p class="text-muted mt-2">Harnessing neural nodes for content creation...</p>
            </div>
        </div>
    </TeacherPageTemplate>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { jsPDF } from 'jspdf'
import { AlertMessage, LoadingSpinner } from '@/components/shared/common'
import aiService from '@/services/teacher/aiService'
import teacherService from '@/services/teacher/teacherPanelService'
import departmentService from '@/services/shared/users/departmentService'
import studentService from '@/services/shared/users/studentService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import '@/assets/css/ai-generator.css'

const router = useRouter()
const step = ref(1)
const loading = ref(false)
const loadingText = ref('Initializing Neural Link...')
const saving = ref(false)
const subjects = ref([])
const departments = ref([])
const filteredStudents = ref([])
const suggestions = ref([])
const selectedIdx = ref(null)
const quiz = ref(null)
const showAdvanced = ref(false)
const alert = reactive({ show: false, type: 'success', message: '', title: '' })

const stepNames = ['Discovery', 'Architecture', 'Deployment']
const breadcrumbs = [
    { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
    { name: 'Quizzes', href: TEACHER_ROUTES.QUIZ_LIST.path },
    { name: 'AI Generator' }
]

// ─── Session persistence helpers ────────────────────────────────────────────
const STORAGE_KEY = 'ai_quiz_generator_state_v2'

const defaultForm = () => ({
    topic: '',
    subject_id: '',
    include_explanation: true,
    num_questions: 10,
    question_type: 'MCQ',
    difficulty: 'Medium',
    assign_mode: 'subject',
    selectedStudents: [],
    deadline: null,
    mixed_counts: { mcq: 5, short: 3, long: 2 }
})

const saveState = () => {
    try {
        const snapshot = {
            step: step.value,
            quiz: quiz.value,
            suggestions: suggestions.value,
            selectedIdx: selectedIdx.value,
            form: { ...form }
        }
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot))
    } catch { /* quota exceeded — ignore */ }
}

const restoreState = () => {
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY)
        if (!raw) return false
        const saved = JSON.parse(raw)
        if (saved.step) step.value = saved.step
        if (saved.quiz) {
            quiz.value = normalizeQuizPayload(
                saved.quiz,
                saved.form?.question_type || form.question_type,
                (saved.form?.question_type || '').toString() === 'Mixed' ? saved.form?.mixed_counts : null
            )
        }
        if (saved.suggestions) suggestions.value = saved.suggestions
        if (saved.selectedIdx != null) selectedIdx.value = saved.selectedIdx
        if (saved.form) Object.assign(form, { ...defaultForm(), ...saved.form })
        return true
    } catch { return false }
}

const clearState = () => {
    sessionStorage.removeItem(STORAGE_KEY)
}
// ─────────────────────────────────────────────────────────────────────────────

const form = reactive(defaultForm())
const isRestoring = ref(false)

// Reset suggestions and selection when input parameters change
watch([() => form.topic, () => form.subject_id, () => form.difficulty, () => form.num_questions, () => form.question_type, () => form.mixed_counts.mcq, () => form.mixed_counts.short, () => form.mixed_counts.long], () => {
    if (isRestoring.value) return
    suggestions.value = []
    selectedIdx.value = null
    quiz.value = null
    if (step.value > 1) step.value = 1
})

// Auto-save state whenever important data changes
watch([step, quiz, suggestions, selectedIdx, () => ({ ...form })], saveState, { deep: true })

onMounted(async () => {
    // Restore previous session state (quiz, form, step) if available
    isRestoring.value = true
    const restored = restoreState()

    try {
        const [subRes, deptRes] = await Promise.all([
            teacherService.getMyClasses(),
            departmentService.getAllDepartments()
        ])

        subjects.value = subRes.results || subRes || []
        // Only auto-select first subject when there is no restored selection
        if (!restored || !form.subject_id) {
            if (subjects.value.length) form.subject_id = subjects.value[0].subject_id
        }

        departments.value = deptRes.results || deptRes || []
        if (!restored || !form.department_id) {
            if (departments.value.length) form.department_id = departments.value[0].id
        }

        const studRes = await studentService.getAllStudents()
        filteredStudents.value = studRes.results || studRes || []
    } catch (error) {
        console.error("Failed to load initial data", error)
    } finally {
        // Allow watchers to function normally after restore settles
        nextTick(() => { isRestoring.value = false })
    }
})

const handleInit = async () => {
    if (!form.topic) return showAlert('warning', 'A topic is required for discovery.')
    if (!form.subject_id) return showAlert('warning', 'Please select a subject.')
    
    loading.value = true
    loadingText.value = 'Analyzing Curriculum Map...'

    try {
        const selectedSubject = subjects.value.find(s => s.subject_id == form.subject_id)

        const res = await aiService.initQuiz({
            topic: form.topic,
            subject: selectedSubject?.subject_name || 'General',
            department: selectedSubject?.department_name || 'Academic',
            num_questions: form.num_questions,
            question_type: form.question_type,
            difficulty: form.difficulty
        })
        if (res.success) {
            suggestions.value = res.data
            step.value = 2
        } else {
            showAlert('error', res.message)
        }
    } catch (error) {
        showAlert('error', 'Failed to initialize AI quiz. Please retry.')
    } finally {
        loading.value = false
    }
}

const handleGenerateManual = async () => {
    if (!form.topic) return showAlert('warning', 'A topic is required.')
    if (!form.subject_id) return showAlert('warning', 'Please select a subject.')

    loading.value = true
    loadingText.value = 'Synthesizing Educational Content...'

    try {
        const selectedSubject = subjects.value.find(sub => sub.subject_id == form.subject_id)

        // Construct a detailed type description for Mixed format
        let finalType = form.question_type
        let finalCount = form.num_questions

        if (form.question_type === 'Mixed') {
            finalCount = form.mixed_counts.mcq + form.mixed_counts.short + form.mixed_counts.long
            finalType = `Mixed format containing strictly: ${form.mixed_counts.mcq} Multiple Choice questions, ${form.mixed_counts.short} Short Answer questions, and ${form.mixed_counts.long} Long Answer/Essay questions.`
        }

        const res = await aiService.generateQuiz({
            topic: form.topic,
            subject: selectedSubject?.subject_name || 'General',
            department: selectedSubject?.department_name || 'Academic',
            difficulty: form.difficulty,
            question_type: finalType,
            num_questions: finalCount,
            total_marks: finalCount,
            temperature: 0.7,
            include_explanation: form.include_explanation
        })

        if (res.success) {
            quiz.value = normalizeQuizPayload(res.data, finalType, form.question_type === 'Mixed' ? form.mixed_counts : null)
            step.value = 2
        } else {
            showAlert('error', res.message)
        }
    } catch (error) {
        showAlert('error', 'Quiz generation failed. Please retry.')
    } finally {
        loading.value = false
    }
}

const handleGenerate = async (s) => {
    loading.value = true
    loadingText.value = 'Synthesizing Educational Content...'

    try {
        const selectedSubject = subjects.value.find(sub => sub.subject_id == form.subject_id)

        const res = await aiService.generateQuiz({
            topic: form.topic,
            subject: selectedSubject?.subject_name || 'General',
            department: selectedSubject?.department_name || 'Academic',
            difficulty: s.difficulty || form.difficulty,
            question_type: s.types ? s.types[0] : form.question_type,
            num_questions: s.total_questions || form.num_questions,
            total_marks: s.marks || form.num_questions,
            temperature: 0.7,
            include_explanation: form.include_explanation
        })

        if (res.success) {
            quiz.value = normalizeQuizPayload(res.data, s.types ? s.types[0] : form.question_type, null)
            step.value = 3
        } else {
            showAlert('error', res.message)
        }
    } catch (error) {
        showAlert('error', 'Quiz generation failed. Please retry.')
    } finally {
        loading.value = false
    }
}

const handleSave = async () => {
    saving.value = true
    const payload = {
        subject_id: form.subject_id,
        title: quiz.value.title,
        quiz_data: quiz.value,
        assign_mode: form.assign_mode === 'subject' ? 'all' : form.assign_mode,
        deadline: form.deadline ? new Date(form.deadline).toISOString() : null,
        target_ids: form.assign_mode === 'students' ? form.selectedStudents : []
    }
    const res = await aiService.saveQuiz(payload)
    if (res.success) {
        clearState()
        showAlert('success', 'Synchronization Complete!', 'Quiz Published')
        setTimeout(() => router.push(TEACHER_ROUTES.QUIZ_LIST.path), 1500)
    } else showAlert('error', res.message)
    saving.value = false
}

const showAlert = (type, message, title = '') => { Object.assign(alert, { show: true, type, message, title }) }
const totalMarks = computed(() => quiz.value?.questions?.reduce((a, b) => a + (Number(b.marks) || 0), 0) || 0)
const mixedTotal = computed(() => (Number(form.mixed_counts.mcq) || 0) + (Number(form.mixed_counts.short) || 0) + (Number(form.mixed_counts.long) || 0))
const isMcqType = (questionType) => (questionType || '').toString().trim().toLowerCase() === 'mcq'
const createEmptyMcqOptions = () => Array(4).fill().map((_, idx) => ({ text: '', is_correct: idx === 0 }))
const normalizeTypeLabel = (value) => {
    const text = (value || '').toString().trim().toLowerCase()
    if (text.includes('mcq') || text.includes('multiple')) return 'MCQ'
    if (text.includes('long') || text.includes('essay')) return 'Long Answer'
    if (text.includes('short')) return 'Short Answer'
    return ''
}
const isGenericOptionText = (text) => {
    const normalized = (text || '').toString().trim().toLowerCase()
    return (
        !normalized
        || normalized === '...'
        || /^option\s+[a-d]$/.test(normalized)
    )
}
const readOptionText = (option) => {
    if (typeof option === 'string' || typeof option === 'number') {
        return String(option).trim()
    }
    if (!option || typeof option !== 'object') return ''
    return (
        option.text
        ?? option.option_text
        ?? option.option
        ?? option.value
        ?? option.label
        ?? ''
    ).toString().trim()
}
const readQuestionOptions = (question) => {
    if (!question || typeof question !== 'object') return []

    if (Array.isArray(question.options)) return question.options
    if (Array.isArray(question.choices)) return question.choices

    const objectCandidates = [question.options, question.choices]
    for (const candidate of objectCandidates) {
        if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)) continue
        const keys = Object.keys(candidate)
        if (!keys.length) continue
        return keys.map((k) => ({ text: candidate[k], is_correct: false }))
    }

    return []
}
const normalizeQuestionShape = (question, questionNumber = 1) => {
    if (!question || typeof question !== 'object') return
    const qText = (question.question_text || '').toString().trim()
    if (!qText || qText === '...') {
        question.question_text = `Question ${questionNumber}`
    }
    if (isMcqType(question.question_type)) {
        question.question_type = 'MCQ'
        question.options = readQuestionOptions(question)
        if (question.options.length === 0) {
            question.options = createEmptyMcqOptions()
        }

        if (question.options.length < 4) {
            const missing = 4 - question.options.length
            for (let i = 0; i < missing; i += 1) {
                question.options.push({ text: '', is_correct: false })
            }
        }

        const explicitCorrectAnswer = (
            question.correct_answer_text
            || question.correct_answer
            || ''
        ).toString().trim().toLowerCase()

        question.options = question.options.slice(0, 4).map((option) => {
            const optionText = readOptionText(option)
            const normalizedText = optionText.toLowerCase()
            const isCorrectFromPayload = typeof option === 'object' && option !== null
                ? !!(option.is_correct ?? option.isCorrect)
                : false
            return {
                text: isGenericOptionText(optionText) ? '' : optionText,
                is_correct: isCorrectFromPayload || (!!explicitCorrectAnswer && explicitCorrectAnswer === normalizedText)
            }
        })

        if (!question.options.some((option) => option.is_correct)) {
            question.options[0].is_correct = true
        }
    } else {
        question.options = []
        if ((question.question_type || '').toString().toLowerCase().includes('long')) {
            question.question_type = 'Long Answer'
        } else {
            question.question_type = 'Short Answer'
        }

        const answerText = (question.correct_answer_text || '').toString().trim()
        if (!answerText || answerText === '...') {
            question.correct_answer_text = 'Write a concise, correct answer.'
        }
    }
}
const normalizeQuizPayload = (payload, requestedType, mixedCounts) => {
    const quizPayload = payload && typeof payload === 'object' ? payload : { questions: [] }
    if (!Array.isArray(quizPayload.questions)) quizPayload.questions = []

    const requested = normalizeTypeLabel(requestedType)
    const isMixed = (requestedType || '').toString().toLowerCase().includes('mixed')

    if (!isMixed && requested) {
        quizPayload.questions.forEach((q, idx) => {
            if (!q || typeof q !== 'object') return
            q.question_type = requested
            normalizeQuestionShape(q, idx + 1)
        })
        return quizPayload
    }

    // Mixed fallback: fill missing/invalid types using requested composition.
    if (isMixed && mixedCounts) {
        const targets = {
            MCQ: Number(mixedCounts.mcq || 0),
            'Short Answer': Number(mixedCounts.short || 0),
            'Long Answer': Number(mixedCounts.long || 0)
        }
        const assigned = { MCQ: 0, 'Short Answer': 0, 'Long Answer': 0 }

        quizPayload.questions.forEach((q) => {
            if (!q || typeof q !== 'object') return
            const normalized = normalizeTypeLabel(q.question_type)
            if (normalized && assigned[normalized] < targets[normalized]) {
                q.question_type = normalized
                assigned[normalized] += 1
            } else {
                q.question_type = ''
            }
        })

        const remaining = []
        ;['MCQ', 'Short Answer', 'Long Answer'].forEach((t) => {
            const needed = Math.max(targets[t] - assigned[t], 0)
            for (let i = 0; i < needed; i += 1) remaining.push(t)
        })

        let remIdx = 0
        quizPayload.questions.forEach((q, qIdx) => {
            if (!q || typeof q !== 'object') return
            if (!q.question_type) {
                q.question_type = remaining[remIdx] || 'Short Answer'
                remIdx += 1
            }
            normalizeQuestionShape(q, qIdx + 1)
        })
        return quizPayload
    }

    quizPayload.questions.forEach((q, idx) => {
        if (!q || typeof q !== 'object') return
        q.question_type = normalizeTypeLabel(q.question_type) || 'MCQ'
        normalizeQuestionShape(q, idx + 1)
    })
    return quizPayload
}
const onQuestionTypeChange = (question) => {
    if (!question) return

    if (isMcqType(question.question_type)) {
        question.question_type = 'MCQ'
        if (!Array.isArray(question.options) || question.options.length === 0) {
            question.options = createEmptyMcqOptions()
        }
    } else {
        if ((question.question_type || '').toString().trim().toLowerCase().includes('long')) {
            question.question_type = 'Long Answer'
        } else {
            question.question_type = 'Short Answer'
        }
        question.options = []
    }
}
const setCorrect = (qi, oi) => {
    if (quiz.value?.questions?.[qi]) {
        quiz.value.questions[qi].options.forEach((o, idx) => o.is_correct = idx === oi)
    }
}
const removeQuestion = (i) => {
    if (quiz.value?.questions) {
        quiz.value.questions.splice(i, 1)
    }
}
const addQuestion = () => {
    if (!quiz.value) quiz.value = { questions: [] }
    if (!quiz.value.questions) quiz.value.questions = []
    quiz.value.questions.push({
        question_text: '', question_type: 'MCQ', marks: 1,
        options: createEmptyMcqOptions()
    })
}

const regenerateQuestion = async (i) => {
    if (!quiz.value?.questions?.[i]) return
    loading.value = true
    loadingText.value = 'Recomputing Question Matrix...'
    const q = quiz.value.questions[i]
    try {
        const payload = {
            topic: form.topic,
            subject: subjects.value.find(s => s.subject_id == form.subject_id)?.subject_name || 'General',
            question_type: q.question_type || 'MCQ',
            difficulty: form.difficulty || 'Medium',
            marks: q.marks || 1,
            temperature: form.temperature || 0.7
        }
        const res = await aiService.regenerateQuizQuestion(payload)
        if (res.success && res.data) {
            // Vue reactivity update
            const normalized = normalizeQuizPayload({ questions: [res.data] }, q.question_type || form.question_type, null)
            quiz.value.questions.splice(i, 1, normalized.questions[0])
            showAlert('success', 'Question successfully regenerated.')
        } else {
            showAlert('error', res.message || 'Failed to regenerate question.')
        }
    } catch (e) {
        showAlert('error', 'Network error while regenerating.')
    } finally {
        loading.value = false
    }
}

const copyToClipboard = () => {
    try {
        let text = quiz.value.questions.map((q, idx) => {
            let optionsText = q.options ? q.options.map(o => `- ${o.text} ${o.is_correct ? '(Correct)' : ''}`).join('\n') : ''
            return `${idx + 1}. ${q.question_text}\n${optionsText}`
        }).join('\n\n')
        navigator.clipboard.writeText(text)
        showAlert('success', 'Quiz copied to clipboard!')
    } catch (err) {
        showAlert('error', 'Failed to copy quiz.')
    }
}

const downloadJSON = () => {
    try {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(quiz.value, null, 2));
        const link = document.createElement('a');
        link.href = dataStr;
        link.download = `${quiz.value.title || 'quiz'}.json`;
        link.click();
        showAlert('success', 'Quiz downloaded as JSON');
    } catch (err) {
        showAlert('error', 'Failed to download JSON.');
    }
}

const downloadTXT = () => {
    try {
        let text = `QUIZ: ${quiz.value.title || 'Untitled Quiz'}\n`;
        text += `Subject: ${subjects.value.find(s => s.subject_id == form.subject_id)?.subject_name || 'General'}\n`;
        text += `==========================================\n\n`;

        quiz.value.questions.forEach((q, i) => {
            text += `Q${i + 1}: ${q.question_text} (${q.marks} pts)\n`;
            if (isMcqType(q.question_type) && q.options) {
                q.options.forEach((o, oi) => {
                    text += `   ${String.fromCharCode(65 + oi)}) ${o.text}${o.is_correct ? ' [CORRECT]' : ''}\n`;
                });
            }
            if (q.explanation) text += `\nExplanation: ${q.explanation}\n`;
            text += `\n`;
        });

        const blob = new Blob([text], { type: 'text/plain' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `${quiz.value.title || 'quiz'}.txt`;
        link.click();
        showAlert('success', 'Quiz downloaded as Plain Text');
    } catch (err) {
        showAlert('error', 'Failed to download TXT.');
    }
}

const downloadPDF = () => {
    if (!quiz.value || !quiz.value.questions) {
        showAlert('warning', 'No quiz questions to export.');
        return;
    }

    try {
        const doc = new jsPDF();
        let y = 20;
        const pageHeight = doc.internal.pageSize.height;
        const marginLeft = 15;
        const marginY = 10;
        const maxLineWidth = 180;

        const checkPageBreak = (neededSpace) => {
            if (y + neededSpace > pageHeight - marginY) {
                doc.addPage();
                y = 20;
            }
        };

        // Title
        doc.setFontSize(18);
        doc.setFont('helvetica', 'bold');
        const title = doc.splitTextToSize(quiz.value.title || 'Generated Quiz', maxLineWidth);
        doc.text(title, marginLeft, y);
        y += (title.length * 8) + 4;
        
        // Metadata
        doc.setFontSize(12);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(100, 100, 100);
        doc.text(`Subject: ${quiz.value.subject || 'General'}  |  Grade: ${quiz.value.grade_level || 'N/A'}`, marginLeft, y);
        doc.setTextColor(0, 0, 0);
        y += 15;
        
        doc.setFontSize(11);
        
        quiz.value.questions.forEach((q, i) => {
            // Question Text
            doc.setFont('helvetica', 'bold');
            const qStr = `Q${i + 1} (${q.marks} pts): ${q.question_text || ''}`;
            const qTexts = doc.splitTextToSize(qStr, maxLineWidth);
            
            checkPageBreak(qTexts.length * 6 + 10);
            doc.text(qTexts, marginLeft, y);
            y += qTexts.length * 6;

            doc.setFont('helvetica', 'normal');
            
            // Options
            if (isMcqType(q.question_type) && q.options) {
                q.options.forEach((o, oi) => {
                    const line = `    ${String.fromCharCode(65 + oi)}) ${o.text || ''}`;
                    const lineTexts = doc.splitTextToSize(line, maxLineWidth);
                    checkPageBreak(lineTexts.length * 5 + 2);
                    
                    if (o.is_correct) {
                        doc.setTextColor(0, 128, 0); // Green for correct option
                        doc.text(`    ${String.fromCharCode(65 + oi)}) ${o.text || ''} [CORRECT]`, marginLeft, y);
                        doc.setTextColor(0, 0, 0);
                    } else {
                        doc.text(lineTexts, marginLeft, y);
                    }
                    y += lineTexts.length * 5 + 2;
                });
            } else if (q.correct_answer_text) {
                const aTexts = doc.splitTextToSize(`Expected Answer: ${q.correct_answer_text}`, maxLineWidth - 10);
                checkPageBreak(aTexts.length * 5 + 4);
                
                doc.setTextColor(0, 100, 200); // Blue for short/long answers
                doc.text(aTexts, marginLeft + 5, y);
                doc.setTextColor(0, 0, 0);
                y += aTexts.length * 5 + 4;
            }

            // Explanation
            if (q.explanation) {
                doc.setFontSize(10);
                doc.setTextColor(100, 100, 100);
                const expTexts = doc.splitTextToSize(`Explanation: ${q.explanation}`, maxLineWidth - 10);
                
                checkPageBreak(expTexts.length * 5 + 4);
                doc.text(expTexts, marginLeft + 5, y);
                doc.setTextColor(0, 0, 0);
                doc.setFontSize(11);
                y += expTexts.length * 5 + 4;
            }
            
            y += 8; // Spacing between questions
        });

        doc.save(`${quiz.value.title || 'Quiz_Blueprint'}.pdf`);
        showAlert('success', 'Quiz exported as PDF successfully.');
    } catch (err) {
        console.error('PDF Export Error:', err);
        showAlert('error', 'Failed to generate PDF.');
    }
}

const difficultyClass = (diff) => ({
    'bg-success-light text-success': diff === 'Easy',
    'bg-warning-light text-warning': diff === 'Medium',
    'bg-danger-light text-danger': diff === 'Hard'
})
</script>
