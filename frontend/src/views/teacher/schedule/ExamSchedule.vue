<template>
  <TeacherPageTemplate
    title="Exam Schedule"
    subtitle="View upcoming exams and assessment dates"
    icon="bi bi-calendar-event"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="alert.show = false"
    />

    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-teacher-light border-0">
            <h5 class="mb-0 fw-bold text-teacher">
              <i class="bi bi-calendar-range me-2"></i>Upcoming Exams
            </h5>
          </div>
          <div class="card-body p-0">
            <LoadingSpinner v-if="loading" text="Loading exams..." theme="teacher" />
            <div v-else-if="exams.length === 0" class="text-center py-5">
              <i class="bi bi-calendar-x display-1 text-muted opacity-50"></i>
              <h4 class="text-muted mt-3">No Exams Scheduled</h4>
              <p class="text-muted">No upcoming exams found.</p>
            </div>
            <div v-else class="exam-list">
              <div v-for="(exam, index) in exams" :key="exam.id" class="exam-card p-4" :class="{ 'border-bottom': index < exams.length - 1 }">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div class="flex-grow-1">
                    <h5 class="fw-bold mb-2">{{ exam.title || exam.exam_name || 'Exam' }}</h5>
                    <p class="text-muted mb-0">
                      <i class="bi bi-book me-1"></i>{{ exam.subject || exam.subject_name || 'N/A' }}
                    </p>
                  </div>
                  <div class="d-flex flex-column align-items-end gap-2">
                    <span :class="['badge', 'px-3', 'py-2', 'badge-sm', getExamTypeBadge(exam.type || exam.exam_type)]">
                      {{ exam.type || exam.exam_type || 'Exam' }}
                    </span>
                    <span v-if="exam.phase" class="badge bg-light text-dark border px-3 py-1">{{ exam.phase }}</span>
                  </div>
                </div>
                
                <div class="row g-3">
                  <div class="col-md-6 col-sm-6">
                    <div class="info-box p-3 bg-light rounded">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-calendar-event fs-4 text-teacher me-3"></i>
                        <div>
                          <small class="text-muted d-block mb-1">Date</small>
                          <strong>{{ formatExamDate(exam.date || exam.exam_date) }}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6 col-sm-6">
                    <div class="info-box p-3 bg-light rounded">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-clock fs-4 text-warning me-3"></i>
                        <div>
                          <small class="text-muted d-block mb-1">Time</small>
                          <strong>{{ exam.time || exam.exam_time || 'TBA' }} ({{ exam.duration || '2h 0m' }})</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6 col-sm-6">
                    <div class="info-box p-3 bg-light rounded">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-geo-alt fs-4 text-danger me-3"></i>
                        <div>
                          <small class="text-muted d-block mb-1">Venue</small>
                          <strong>{{ exam.venue || exam.room || 'TBA' }}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6 col-sm-6">
                    <div class="info-box p-3 bg-light rounded">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-people fs-4 text-success me-3"></i>
                        <div>
                          <small class="text-muted d-block mb-1">Students</small>
                          <strong>{{ exam.students || exam.student_count || 0 }} enrolled</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-info-light border-0">
            <h5 class="mb-0 fw-bold text-info">
              <i class="bi bi-bar-chart me-2"></i>Exam Statistics
            </h5>
          </div>
          <div class="card-body">
            <div class="d-flex flex-column gap-3">
              <div class="stat-card p-3 bg-light rounded">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <small class="text-muted d-block mb-1">Total Exams</small>
                    <h3 class="mb-0 fw-bold text-dark">{{ exams.length }}</h3>
                  </div>
                  <div class="stat-icon bg-teacher-light text-teacher rounded-circle">
                    <i class="bi bi-calendar-check"></i>
                  </div>
                </div>
              </div>
              <div class="stat-card p-3 bg-light rounded">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <small class="text-muted d-block mb-1">This Week</small>
                    <h3 class="mb-0 fw-bold text-dark">{{ thisWeekExams }}</h3>
                  </div>
                  <div class="stat-icon bg-success-light text-success rounded-circle">
                    <i class="bi bi-calendar-week"></i>
                  </div>
                </div>
              </div>
              <div class="stat-card p-3 bg-light rounded">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <small class="text-muted d-block mb-1">Next Week</small>
                    <h3 class="mb-0 fw-bold text-dark">{{ nextWeekExams }}</h3>
                  </div>
                  <div class="stat-icon bg-warning-light text-warning rounded-circle">
                    <i class="bi bi-calendar-range"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Exam Modal -->
    <ExamFormModal
      v-model="showCreateModal"
      :form="form"
      :subjects="subjects"
      :is-editing="false"
      :loading="submitting"
      @submit="handleSubmit"
    />
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { AlertMessage, LoadingSpinner } from '@/components/shared/common'
import { ExamFormModal } from '@/components/teacher/shared'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { formatDate } from '@/utils/formatters'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { useAlert, useAsyncState } from '@/composables/shared'

const router = useRouter()
const { alert, showAlert } = useAlert()

const breadcrumbs = [
  { name: 'Dashboard', href: { name: TEACHER_ROUTES.DASHBOARD.name } },
  { name: 'Class Schedule', href: { name: TEACHER_ROUTES.CLASS_SCHEDULE.name } },
  { name: 'Exam Schedule' }
]

const showCreateModal = ref(false)
const submitting = ref(false)

const actions = [
  { label: 'Schedule Exam', icon: 'bi bi-plus-circle', variant: 'btn-teacher-outline', onClick: () => { showCreateModal.value = true } },
  { label: 'Class Schedule', icon: 'bi bi-calendar3', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.CLASS_SCHEDULE.name }) }
]

const defaultForm = { subject: '', exam_type: 'midterm', phase: '', exam_date: '', exam_time: '', duration_minutes: 120, room: '', total_marks: 100, status: 'scheduled', instructions: '' }
const form = ref({ ...defaultForm })

const { data: examsData, loading, execute: fetchExams } = useAsyncState({ initialLoading: true })
const exams = computed(() => examsData.value?.results || [])

const loadExams = () => fetchExams(() => teacherPanelService.getExams())

const { data: subjectsData, execute: fetchSubjects } = useAsyncState({ initialLoading: true })
const subjects = computed(() => subjectsData.value?.results || [])

const loadSubjects = () => fetchSubjects(() => teacherPanelService.getMyClasses(), { showLoading: false })

const getExamsInRange = (startDays, endDays) => {
  const start = new Date(); start.setDate(start.getDate() + startDays)
  const end = new Date(); end.setDate(end.getDate() + endDays)
  return exams.value.filter(e => { const d = new Date(e.date); return d >= start && d <= end }).length
}

const thisWeekExams = computed(() => getExamsInRange(0, 7))
const nextWeekExams = computed(() => getExamsInRange(7, 14))

const getExamTypeBadge = (type) => ({ 'quiz': 'bg-info', 'midterm': 'bg-warning text-dark', 'final': 'bg-danger', 'practical': 'bg-primary', 'viva': 'bg-success' }[type?.toLowerCase()] || 'bg-secondary')

const formatExamDate = (dateString) => formatDate(dateString, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })

const handleSubmit = async (formData) => {
  submitting.value = true
  try {
    await teacherPanelService.createExam(formData)
    showAlert('success', 'Exam scheduled successfully!')
    showCreateModal.value = false
    form.value = { ...defaultForm }
    loadExams()
  } catch (error) {
    showAlert('error', 'Failed to schedule exam')
  } finally {
    submitting.value = false
  }
}

onMounted(() => { loadExams(); loadSubjects() })
</script>

