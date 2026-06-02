<template>
  <StudentPageTemplate
    title="Semester History"
    subtitle="View your academic progress, GPA, and subject results across all semesters"
    icon="bi bi-clock-history"
    :breadcrumbs="breadcrumbs"
  >
    <!-- Top Summary (Cumulative CGPA) -->
    <div class="journey-card p-4 mb-4 shadow-sm">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center">
        <div class="mb-3 mb-md-0">
          <h4 class="fw-bold mb-1 text-dark">Academic Journey</h4>
          <p class="text-muted mb-0">Cumulative performance across <span class="fw-bold">{{ totalSemesters }}</span> recorded semesters.</p>
        </div>
        <div class="text-md-end text-center bg-white p-3 rounded-4 shadow-sm border" style="min-width: 150px;">
          <div class="small text-muted text-uppercase fw-bold mb-2" style="letter-spacing: 1px;">Cumulative CGPA</div>
          <div class="cgpa-display">{{ cgpa }}</div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5 my-5">
      <div class="spinner-border text-success" role="status" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted fw-semibold">Loading your academic history...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="semesters.length === 0" class="text-center py-5 my-5 bg-white rounded-4 shadow-sm border">
      <div class="display-1 text-muted mb-3"><i class="bi bi-inbox"></i></div>
      <h4 class="fw-bold text-dark">No Semester Records Found</h4>
      <p class="text-muted">You are not enrolled in any subjects yet.</p>
    </div>

    <div v-else>
      <div class="row g-4 mb-4">
        <div class="col-12 col-md-6 col-lg-4" v-for="(sem, index) in semesters" :key="sem.semester_id">
          <div 
            class="card h-100 border-0 rounded-4 quiz-style-card cursor-pointer transition-all" 
            @click="openSemesterModal(index)"
          >
            <div class="card-body p-4 d-flex flex-column">
              <!-- Header Row: Icon & Status -->
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="bg-white rounded-3 d-flex align-items-center justify-content-center shadow-sm" style="width: 48px; height: 48px;">
                  <i class="bi bi-journal-bookmark text-dark fs-4"></i>
                </div>
                <span class="badge rounded-pill px-3 py-2 fw-semibold shadow-sm" 
                      :class="sem.is_current ? 'bg-student text-white' : 'bg-success text-white'"
                      style="font-size: 0.75rem;">
                  {{ sem.is_current ? 'Current' : 'Completed' }}
                </span>
              </div>
              
              <!-- Title & Subtitle -->
              <h5 class="fw-bold mb-1 card-title-green">{{ sem.semester_name }}</h5>
              <div class="small mb-3 card-subtitle-green">
                <i class="bi bi-mortarboard opacity-75 me-1"></i> {{ sem.session_name }}
              </div>

              <div class="mt-auto">
                <!-- Divider -->
                <div class="border-top border-dark border-opacity-10 my-3"></div>
                
                <!-- Stats Row -->
                <div class="d-flex justify-content-between align-items-center mb-4 small text-muted fw-medium">
                  <span title="Total Subjects"><i class="bi bi-list-ul me-1"></i> {{ sem.total_subjects }} Subj</span>
                  <span title="Passed Subjects"><i class="bi bi-check-circle me-1"></i> {{ sem.passed_count }} Pass</span>
                  <span title="Failed/Pending"><i class="bi bi-exclamation-circle me-1"></i> {{ sem.failed_count + sem.pending_count }} Wait/Fail</span>
                </div>
                
                <!-- GPA Score Display -->
                <div class="d-flex justify-content-between align-items-center bg-white bg-opacity-50 rounded-3 p-3 mb-3 border border-white">
                  <span class="text-muted small fw-semibold">Semester GPA:</span>
                  <span class="fw-bold card-title-green fs-5">{{ (sem.gpa || 0).toFixed(2) }}</span>
                </div>
                
                <!-- Action Button -->
                <div class="d-flex gap-2 w-100">
                  <button class="btn btn-outline-success flex-grow-1 rounded-3 fw-bold bg-white hover-btn-green py-2 border-success border-opacity-50">
                    <i class="bi bi-eye me-1"></i> View Details
                  </button>
                  <a 
                    v-if="sem.result_pdf"
                    :href="getPdfUrl(sem.result_pdf)"
                    target="_blank"
                    class="btn btn-success rounded-3 fw-bold py-2 px-3 shadow-sm"
                    @click.stop
                    title="Download Official Transcript PDF"
                  >
                    <i class="bi bi-file-earmark-pdf-fill"></i>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Modal Popup -->
    <Teleport to="body">
      <div class="modal fade" id="semesterDetailsModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-xl modal-dialog-scrollable">
          <div class="modal-content border-0 rounded-4 shadow-lg">
            
            <div class="modal-header border-bottom-0 pb-0 px-4 pt-4 align-items-start" v-if="selectedSemester">
              <div>
                <div class="d-flex align-items-center gap-2 mb-2">
                  <h4 class="fw-bold mb-0 text-dark">{{ selectedSemester.semester_name }}</h4>
                  <span v-if="selectedSemester.is_current" class="badge bg-student text-white px-2 py-1 rounded-pill">Current</span>
                  <span v-if="selectedSemester.status === 'completed'" class="badge bg-success text-white px-2 py-1 rounded-pill">Completed</span>
                </div>
                <div class="text-muted small">
                  <i class="bi bi-mortarboard me-1 text-success"></i> <span class="fw-semibold">{{ selectedSemester.session_name }}</span>
                  <span class="mx-2 text-muted opacity-50">•</span>
                  <i class="bi bi-book me-1 text-success"></i> <span class="fw-semibold">{{ selectedSemester.total_subjects }}</span> Enrolled Subjects
                </div>
              </div>
              <button type="button" class="btn-close shadow-none" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>

            <div class="modal-body px-4 pb-4 pt-3" v-if="selectedSemester">
              
              <!-- Summary Stats -->
              <div class="d-flex flex-wrap gap-2 align-items-center bg-light p-3 rounded-4 mb-4 border">
                <div class="stat-box bg-white text-success rounded-3 px-3 py-2 text-center shadow-sm" title="Passed Subjects">
                  <div class="fw-bold fs-5 lh-1">{{ selectedSemester.passed_count }}</div>
                  <div class="text-uppercase fw-bold mt-1" style="font-size: 0.6rem; letter-spacing: 0.5px;">Pass</div>
                </div>
                <div class="stat-box bg-white text-danger rounded-3 px-3 py-2 text-center shadow-sm" title="Failed Subjects">
                  <div class="fw-bold fs-5 lh-1">{{ selectedSemester.failed_count }}</div>
                  <div class="text-uppercase fw-bold mt-1" style="font-size: 0.6rem; letter-spacing: 0.5px;">Fail</div>
                </div>
                <div class="stat-box bg-white text-warning rounded-3 px-3 py-2 text-center shadow-sm" title="Pending Subjects">
                  <div class="fw-bold fs-5 lh-1">{{ selectedSemester.pending_count }}</div>
                  <div class="text-uppercase fw-bold mt-1" style="font-size: 0.6rem; letter-spacing: 0.5px;">Wait</div>
                </div>
                <div class="stat-box bg-student text-white rounded-3 px-3 py-2 text-center shadow-sm ms-auto" title="Semester GPA">
                  <div class="fw-bold fs-5 lh-1">{{ selectedSemester.gpa.toFixed(2) }}</div>
                  <div class="text-uppercase fw-bold text-white-50 mt-1" style="font-size: 0.6rem; letter-spacing: 0.5px;">GPA</div>
                </div>
                <a 
                  v-if="selectedSemester.result_pdf"
                  :href="getPdfUrl(selectedSemester.result_pdf)"
                  target="_blank"
                  class="btn btn-success rounded-3 d-flex align-items-center gap-2 px-3 py-2 shadow-sm border border-success border-opacity-50"
                  title="Download Official Transcript PDF"
                >
                  <i class="bi bi-file-earmark-pdf-fill"></i>
                  <span class="fw-bold small text-white">Official Transcript</span>
                </a>
              </div>

              <div class="d-flex align-items-center mb-3">
                <h6 class="fw-bold text-muted mb-0 text-uppercase" style="letter-spacing: 1px; font-size: 0.85rem;">Subject Results History</h6>
                <div class="flex-grow-1 border-top ms-3 opacity-25"></div>
              </div>
              
              <div class="row g-3">
                <div class="col-md-6 col-lg-4" v-for="subj in selectedSemester.subjects" :key="subj.subject_id">
                  <div class="card h-100 border shadow-sm rounded-4 overflow-hidden">
                    <div class="p-1" :class="{'bg-success': subj.result === 'pass', 'bg-danger': subj.result === 'fail', 'bg-warning': subj.result === 'pending'}"></div>
                    <div class="card-body p-3">
                      <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                          <div class="badge bg-light text-dark border mb-2">{{ subj.code }}</div>
                          <h6 class="fw-bold mb-0 text-dark lh-sm" :title="subj.name">{{ subj.name }}</h6>
                        </div>
                        <div class="rounded-circle d-flex align-items-center justify-content-center text-white flex-shrink-0 shadow-sm" style="width: 32px; height: 32px;" :class="{'bg-success': subj.result === 'pass', 'bg-danger': subj.result === 'fail', 'bg-warning': subj.result === 'pending'}">
                          <i class="bi fs-5" :class="{'bi-check': subj.result === 'pass', 'bi-x': subj.result === 'fail', 'bi-hourglass-split': subj.result === 'pending'}"></i>
                        </div>
                      </div>
                      
                      <div class="row g-2 mt-2 bg-light rounded-3 p-2 text-center border">
                        <div class="col-4 border-end">
                          <div class="small text-muted mb-1" style="font-size: 0.65rem; text-transform: uppercase;">Percent</div>
                          <div class="fw-bold text-dark">{{ subj.result === 'pending' && subj.percentage === 0 ? '--' : subj.percentage + '%' }}</div>
                        </div>
                        <div class="col-4 border-end">
                          <div class="small text-muted mb-1" style="font-size: 0.65rem; text-transform: uppercase;">Grade</div>
                          <div class="fw-bold fs-5 lh-1" :class="getGradeColor(subj.letter_grade)">{{ subj.letter_grade || '--' }}</div>
                        </div>
                        <div class="col-4">
                          <div class="small text-muted mb-1" style="font-size: 0.65rem; text-transform: uppercase;">Credits</div>
                          <div class="fw-bold text-dark">{{ subj.credit_hours }}</div>
                        </div>
                      </div>

                      <div v-if="subj.remarks" class="mt-3 p-2 bg-light rounded-3 small text-muted border-start border-3 border-secondary">
                        <i class="bi bi-chat-text me-1"></i> {{ subj.remarks }}
                      </div>

                      <!-- Grading Components (Assignments / Quizzes) -->
                      <div v-if="subj.components && subj.components.length > 0" class="mt-3 pt-3 border-top border-light">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                          <span class="small fw-bold text-muted text-uppercase" style="font-size: 0.7rem; letter-spacing: 0.5px;">Assessments Breakdown</span>
                          <span class="badge bg-secondary bg-opacity-10 text-secondary rounded-pill" style="font-size: 0.65rem;">{{ subj.components.length }}</span>
                        </div>
                        
                        <div class="d-flex flex-column gap-2" style="max-height: 140px; overflow-y: auto;">
                          <div v-for="(comp, idx) in subj.components" :key="idx" class="d-flex justify-content-between align-items-center p-2 rounded-3 bg-white border border-light shadow-sm transition-hover" style="font-size: 0.8rem;">
                            <div class="d-flex align-items-center gap-2 overflow-hidden">
                              <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width: 28px; height: 28px; background-color: rgba(25, 135, 84, 0.1) !important; color: #198754 !important;">
                                <i class="bi" :class="comp.type === 'assignment' ? 'bi-file-earmark-text' : (comp.type === 'quiz' ? 'bi-ui-radios' : 'bi-journal-check')" style="font-size: 0.85rem;"></i>
                              </div>
                              <span class="text-truncate fw-medium text-dark" :title="comp.title">{{ comp.title }}</span>
                            </div>
                            <div class="flex-shrink-0 text-end ms-2">
                              <span class="fw-bold" :class="comp.percentage >= 50 ? 'text-success' : (comp.percentage > 0 ? 'text-danger' : 'text-muted')">
                                {{ comp.marks_obtained }}
                              </span>
                              <span class="text-muted small"> / {{ comp.max_marks }}</span>
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
        </div>
      </div>
    </Teleport>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { Modal } from 'bootstrap'
import { StudentPageTemplate } from '@/components/shared/panels'
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { apiGet } from '@/services/shared/core/apiWrapper'
import { getFileUrl } from '@/utils/constants/config'

const getPdfUrl = (url) => getFileUrl(url)

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Grades', href: STUDENT_ROUTES.MY_GRADES.path },
  { name: 'Semester History' }
]

const { studentId } = useStudentBase()

const loading = ref(true)
const cgpa = ref('0.00')
const totalSemesters = ref(0)
const semesters = ref([])
const selectedSemesterIndex = ref(0)

const selectedSemester = computed(() => {
  if (!semesters.value || semesters.value.length === 0) return null
  return semesters.value[selectedSemesterIndex.value]
})

let detailsModalInstance = null

const openSemesterModal = (index) => {
  selectedSemesterIndex.value = index
  if (!detailsModalInstance) {
    const el = document.getElementById('semesterDetailsModal')
    if (el) detailsModalInstance = new Modal(el)
  }
  if (detailsModalInstance) {
    detailsModalInstance.show()
  }
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const res = await apiGet(`/students/${studentId}/semester-history/`)
    cgpa.value = (res.cgpa || 0).toFixed(2)
    totalSemesters.value = res.total_semesters || 0
    semesters.value = res.semesters || []
    
    // Auto-select index 0 on load just to have data ready
    if (semesters.value.length > 0) {
      selectedSemesterIndex.value = 0
    }
    
    nextTick(() => {
      const el = document.getElementById('semesterDetailsModal')
      if (el) detailsModalInstance = new Modal(el)
    })
  } catch (err) {
    console.error('Failed to fetch semester history:', err)
  } finally {
    loading.value = false
  }
}

const getGradeColor = (grade) => {
  if (!grade) return 'text-muted'
  if (grade.startsWith('A')) return 'text-success'
  if (grade.startsWith('B')) return 'text-primary'
  if (grade.startsWith('C')) return 'text-warning'
  if (grade === 'F') return 'text-danger'
  return 'text-dark'
}

onMounted(() => {
  if (studentId) {
    fetchHistory()
  } else {
    // Fallback in case ID is delayed or needs to be pulled from profile
    console.warn('Student ID not found in localStorage')
    loading.value = false
  }
})
</script>
