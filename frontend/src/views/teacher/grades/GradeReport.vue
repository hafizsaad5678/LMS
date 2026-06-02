<template>
  <TeacherPageTemplate
    title="Grade Report"
    subtitle="Comprehensive grade analysis and performance reports"
    icon="bi bi-clipboard-data"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <AlertMessage v-if="alert.show" v-bind="alert" :auto-close="true" @close="clearAlert" />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 mb-4">
        <div v-for="stat in statsCards" :key="stat.title" class="col-md-3">
          <StatCard v-bind="stat" />
        </div>
      </div>
    </template>

    <LoadingSpinner v-if="loading" text="Loading grade report..." theme="teacher" />

    <div v-else>
      <!-- Filters -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label fw-bold text-dark small">Select Class/Subject</label>
              <select v-model="selectedClass" class="form-select rounded-4 bg-light border-0 p-3">
                <option value="">All Classes</option>
                <option v-for="cls in classes" :key="cls.id" :value="cls.subject_id">
                  {{ cls.subject_name }} ({{ cls.subject_code }})
                </option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-bold text-dark small">Period</label>
              <select v-model="selectedPeriod" class="form-select rounded-4 bg-light border-0 p-3">
                <option v-for="opt in GRADE_PERIOD_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <GradeDistributionChart :distribution="gradeDistribution" />
        </div>
        <div class="col-lg-4">
          <TopPerformersList :performers="topPerformers" />
        </div>
      </div>

      <!-- Detailed Grades Table -->
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <h5 class="card-title fw-bold text-dark mb-4">
            <i class="bi bi-table me-2 text-teacher"></i>Detailed Grades
          </h5>
          <div v-if="detailedGrades.length > 0" class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Student</th>
                  <th class="text-center">Assignments (10)</th>
                  <th class="text-center">Quizzes (10)</th>
                  <th class="text-center">Mid Paper (20)</th>
                  <th class="text-center">Final (60)</th>
                  <th class="text-center">Overall (100)</th>
                  <th class="text-center">Grade</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in detailedGrades" :key="student.id">
                  <td>
                    <div class="fw-bold text-dark">{{ student.name || 'Unknown Student' }}</div>
                    <small v-if="student.roll_no" class="text-muted">{{ student.roll_no }}</small>
                  </td>
                  <td class="text-center">
                    <span class="fw-semibold text-dark">{{ student.assignment_scaled !== null && student.assignment_scaled !== undefined ? student.assignment_scaled : 0 }} / 10</span>
                    <small class="text-muted text-xs ms-1">({{ student.assignments !== null && student.assignments !== undefined ? student.assignments + '%' : '0%' }})</small>
                  </td>
                  <td class="text-center">
                    <span class="fw-semibold text-dark">{{ student.quiz_scaled !== null && student.quiz_scaled !== undefined ? student.quiz_scaled : 0 }} / 10</span>
                    <small class="text-muted text-xs ms-1">({{ student.quizzes !== null && student.quizzes !== undefined ? student.quizzes + '%' : '0%' }})</small>
                  </td>
                  <td 
                    class="text-center position-relative midterm-cell" 
                    style="cursor: pointer; min-width: 140px; transition: background-color 0.2s;" 
                    @click="openEditMidModal(student)"
                    title="Click to enter/edit Mid Paper marks"
                  >
                    <div class="d-flex align-items-center justify-content-center gap-1 py-1 rounded">
                      <span class="fw-semibold text-dark">
                        {{ student.mid_paper_marks !== null && student.mid_paper_marks !== undefined ? student.mid_paper_marks + ' / 20' : '0 / 20' }}
                      </span>
                      <small v-if="student.mid_paper_marks !== null && student.mid_paper_marks !== undefined" class="text-muted text-xs ms-1">
                        ({{ Math.round((student.mid_paper_marks / 20) * 100) }}%)
                      </small>
                      <small v-else class="text-muted text-xs ms-1">
                        (0%)
                      </small>
                      <i class="bi bi-pencil-fill text-primary ms-2 edit-pencil-icon" style="font-size: 0.75rem; opacity: 0; transition: opacity 0.2s;"></i>
                    </div>
                  </td>
                  <td class="text-center">
                    <span class="fw-semibold text-dark">{{ student.sessional_marks !== null && student.sessional_marks !== undefined ? student.sessional_marks : 0 }} / 60</span>
                    <small class="text-muted text-xs ms-1">({{ student.final !== null && student.final !== undefined ? student.final + '%' : '0%' }})</small>
                  </td>
                  <td class="text-center fw-bold text-dark">
                    <span>{{ student.overall !== null && student.overall !== undefined ? student.overall : 0 }} / 100</span>
                    <small class="text-muted text-xs ms-1">({{ student.overall !== null && student.overall !== undefined ? student.overall + '%' : '0%' }})</small>
                  </td>
                  <td class="text-center">
                    <button 
                      class="badge px-3 border-0 font-monospace"
                      :class="student.is_pending ? 'bg-warning-subtle text-warning-emphasis' : getGradeBadge(student.grade)"
                      style="cursor: pointer; font-size: 0.85rem; transition: transform 0.2s;"
                      onmouseover="this.style.transform='scale(1.15)';"
                      onmouseout="this.style.transform='scale(1)';"
                      @click="openGradeExplanationModal(student)"
                      title="Click to view grade explanation"
                    >
                      {{ student.is_pending ? 'Pending' : student.grade }}
                    </button>
                    <div v-if="student.is_pending" class="extra-small text-muted mt-1 fw-semibold">Marks not entered yet</div>
                    <div v-else-if="student.overall < 40" class="extra-small text-danger mt-1 fw-semibold">Below 40%</div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-5">
            <i class="bi bi-table display-4 text-muted"></i>
            <p class="text-muted mt-3">No grade data available</p>
          </div>
        </div>
      </div>
    </div>
    
    <GradeBreakdownModal
      v-model="showGradeModal"
      v-if="showGradeModal && gradeModalStudent"
      :student-id="gradeModalStudent.id"
      :subject-id="gradeModalStudent.subject_id || selectedClass"
      :student-name="gradeModalStudent.name"
      :student-enrollment="gradeModalStudent.roll_no"
      :mid-marks="gradeModalStudent.mid_marks"
      :mid-paper-marks="gradeModalStudent.mid_paper_marks"
      :sessional-marks="gradeModalStudent.sessional_marks"
      :total-marks="gradeModalStudent.overall"
      :letter-grade="gradeModalStudent.grade"
      :gpa="gradeModalStudent.gpa"
    />

    <!-- Sleek Pop-up Modal for Entering Mid Paper Marks -->
    <BaseModal v-model="showEditMidModal" title="Mid Paper Marks" :show-footer="false">
      <div class="p-2 pb-3">
        <div class="bg-light p-3 rounded-4 mb-4 border-start border-4 border-primary d-flex justify-content-between align-items-center">
          <div>
            <h6 class="fw-bold text-dark mb-1">{{ editingStudent?.name }}</h6>
            <p class="text-muted small mb-0 text-uppercase font-monospace">ROLL NO: {{ editingStudent?.roll_no || '—' }}</p>
          </div>
        </div>
        
        <div class="input-group input-group-lg mx-auto shadow-sm" style="max-width: 180px; border-radius: 12px; overflow: hidden;">
          <input 
            type="number" 
            v-model="editMidMarksVal" 
            class="form-control text-center fw-bold border-0 bg-light"
            min="0" 
            max="20" 
            step="0.5"
            placeholder="0"
            v-focus
            @keydown.enter="submitEditMidMarks"
            @keydown.esc="showEditMidModal = false"
            style="font-size: 1.5rem;"
          />
          <span class="input-group-text border-0 bg-light-subtle fw-bold text-secondary" style="font-size: 1.2rem;">/ 20</span>
        </div>
        <div class="text-center extra-small text-muted mt-3 mb-4 fw-semibold">Enter paper marks between 0 and 20</div>
        
        <div class="d-flex justify-content-center gap-3">
          <button type="button" class="btn btn-light px-4 rounded-pill fw-bold text-secondary border" @click="showEditMidModal = false">Cancel</button>
          <button type="button" class="btn btn-primary px-4 rounded-pill fw-bold shadow-sm" style="background-color: var(--teacher-primary);" @click="submitEditMidMarks">Save</button>
        </div>
      </div>
    </BaseModal>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { StatCard, AlertMessage, LoadingSpinner, BaseModal } from '@/components/shared/common'
import GradeDistributionChart from '@/components/teacher/grades/GradeDistributionChart.vue'
import TopPerformersList from '@/components/teacher/grades/TopPerformersList.vue'
import GradeBreakdownModal from '@/components/teacher/grades/GradeBreakdownModal.vue'
import { useGradeManagement } from '@/composables/teacher/useGradeManagement'
import { useAlert } from '@/composables/shared'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { GRADE_PERIOD_OPTIONS } from '@/utils/constants/options'

const router = useRouter()
const { calculateGrade, getGradeBadge } = useGradeManagement()
const { alert, showAlert, clearAlert } = useAlert()

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Grades', href: TEACHER_ROUTES.GRADE_MANAGEMENT.path },
  { name: 'Grade Report' }
]

const actions = [
  { label: 'Export Report', icon: 'bi bi-download', variant: 'btn-teacher-outline', onClick: exportReport },
  { label: 'Manage Grades', icon: 'bi bi-gear', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.GRADE_MANAGEMENT.name }) }
]

const selectedClass = ref('')
const selectedPeriod = ref('current')
const classes = ref([])
const loading = ref(false)
const gradeDistribution = ref([])
const topPerformers = ref([])
const detailedGrades = ref([])

const showGradeModal = ref(false)
const gradeModalStudent = ref(null)

const openGradeExplanationModal = (student) => {
  gradeModalStudent.value = student
  showGradeModal.value = true
}

// Custom focus directive for inline editing
const vFocus = {
  mounted: (el) => el.focus()
}

const showEditMidModal = ref(false)
const editingStudent = ref(null)
const editMidMarksVal = ref('')

const openEditMidModal = (student) => {
  editingStudent.value = student
  editMidMarksVal.value = student.mid_paper_marks !== null && student.mid_paper_marks !== undefined ? student.mid_paper_marks.toString() : '0'
  showEditMidModal.value = true
}

const submitEditMidMarks = async () => {
  const student = editingStudent.value
  if (!student) return
  
  const parsedVal = editMidMarksVal.value === '' ? 0 : parseFloat(editMidMarksVal.value)
  
  if (isNaN(parsedVal) || parsedVal < 0 || parsedVal > 20) {
    showAlert('danger', 'Mid Paper marks must be between 0 and 20')
    return
  }

  try {
    loading.value = true
    showEditMidModal.value = false
    
    if (!student.result_id) {
      await teacherPanelService.initializeSubjectResults(selectedClass.value || student.subject_id)
      await loadGradeReport()
      const updatedStudent = detailedGrades.value.find(s => s.id === student.id)
      if (updatedStudent && updatedStudent.result_id) {
        student.result_id = updatedStudent.result_id
      } else {
        throw new Error('Could not initialize SubjectResult for student')
      }
    }

    await teacherPanelService.updateSubjectResult(student.result_id, {
      mid_paper_marks: parsedVal
    })

    showAlert('success', `Mid Paper marks updated successfully for ${student.name}`)
    await loadGradeReport()
  } catch (error) {
    console.error('Error saving midterm marks:', error)
    showAlert('danger', 'Failed to save midterm marks')
  } finally {
    loading.value = false
    editingStudent.value = null
    editMidMarksVal.value = ''
  }
}

const statsCards = computed(() => [
  { title: 'Class Average', value: averageGrade.value, icon: 'bi bi-award', type: 'student' },
  { title: 'Total Students', value: detailedGrades.value.length, icon: 'bi bi-people', type: 'teacher' },
  { title: 'Pending', value: detailedGrades.value.filter(s => s.is_pending).length, icon: 'bi bi-hourglass-split', type: 'finance' },
  { title: 'Below 50%', value: detailedGrades.value.filter(s => !s.is_pending && s.overall < 50).length, icon: 'bi bi-exclamation-triangle', type: 'finance' }
])

const averageGrade = computed(() => {
  const gradedOnly = detailedGrades.value.filter(s => !s.is_pending)
  if (gradedOnly.length === 0) return '0%'
  return Math.round(gradedOnly.reduce((sum, s) => sum + s.overall, 0) / gradedOnly.length) + '%'
})

function exportReport() {
  if (detailedGrades.value.length === 0) return showAlert('warning', 'No grade data to export')
  const headers = ['Student', 'Roll No', 'Assignments', 'Quizzes', 'Midterm', 'Final', 'Overall', 'Grade']
  const rows = detailedGrades.value.map(s => [s.name, s.roll_no, `${s.assignments}%`, `${s.quizzes}%`, `${s.midterm}%`, `${s.final}%`, `${s.overall}%`, s.grade])
  const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `grade-report-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

async function loadClasses() {
  try {
    const response = await teacherPanelService.getMyClasses()
    classes.value = response.results || response || []
  } catch (error) {
    console.error('Error loading classes:', error)
  }
}

async function loadGradeReport() {
  loading.value = true
  try {
    const params = { subject: selectedClass.value || undefined, period: selectedPeriod.value === 'current' ? undefined : selectedPeriod.value }
    
    // Fetch both assessment component marks and final subject results
    const [marksRes, resultsRes] = await Promise.all([
      teacherPanelService.getAllMarks(params),
      teacherPanelService.getSubjectResults(params)
    ])
    
    const marks = marksRes.results || marksRes || []
    const results = resultsRes.results || resultsRes || []
    
    if (marks.length === 0 && results.length === 0) {
      detailedGrades.value = []
      gradeDistribution.value = []
      topPerformers.value = []
      return
    }
    
    const studentMap = new Map()
    
    // 1. Initialize from Subject Results (Ground Truth for Midterm, Final/Sessional, Overall, Grade)
    results.forEach(res => {
      const studentId = res.student
      const midPaperVal = res.mid_paper_marks !== null && res.mid_paper_marks !== undefined ? parseFloat(res.mid_paper_marks) : null
      const midVal = res.mid_marks !== null && res.mid_marks !== undefined ? parseFloat(res.mid_marks) : null
      const sessVal = res.sessional_marks !== null && res.sessional_marks !== undefined ? parseFloat(res.sessional_marks) : null
      const totalVal = res.total_marks !== null && res.total_marks !== undefined ? parseFloat(res.total_marks) : null
      const isPending = res.result === 'pending' || res.total_marks === null
      
      studentMap.set(studentId, {
        id: studentId,
        subject_id: res.subject,
        name: res.student_name || 'Unknown Student',
        roll_no: res.student_enrollment || null,
        assignments: null,
        quizzes: null,
        midterm: midPaperVal !== null ? Math.round((midPaperVal / 20) * 100) : null,
        final: sessVal !== null ? Math.round((sessVal / 60) * 100) : null,
        mid_paper_marks: midPaperVal,
        mid_marks: midVal,
        sessional_marks: sessVal,
        overall: totalVal !== null ? Math.round(totalVal) : 0,
        grade: res.letter_grade || 'Pending',
        gpa: res.gpa !== null && res.gpa !== undefined ? parseFloat(res.gpa) : null,
        is_pending: isPending,
        assignment_obt: 0, assignment_max: 0,
        quiz_obt: 0, quiz_max: 0,
        result_id: res.id
      })
    })
    
    // 2. Accumulate granular assignment/quiz marks
    marks.forEach(mark => {
      const studentId = mark.student || mark.student_id
      if (!studentMap.has(studentId)) {
        studentMap.set(studentId, {
          id: studentId,
          subject_id: mark.subject || selectedClass.value || '',
          name: mark.student_name || 'Unknown Student',
          roll_no: mark.student_roll_no || mark.roll_no || mark.student_enrollment || null,
          assignments: null,
          quizzes: null,
          midterm: null,
          final: null,
          overall: 0,
          grade: 'Pending',
          is_pending: true,
          assignment_obt: 0, assignment_max: 0,
          quiz_obt: 0, quiz_max: 0,
          result_id: null
        })
      }
      
      const student = studentMap.get(studentId)
      const componentType = mark.component_type || 'assignment'
      const rawMaxMarks = mark.max_marks ?? mark.total_marks
      const maxMarks = Number(rawMaxMarks)
      const hasValidMax = Number.isFinite(maxMarks) && maxMarks > 0
      const rawMarks = mark.marks_obtained
      const hasMarks = rawMarks !== null && rawMarks !== undefined
      
      if (hasMarks && hasValidMax) {
        const obt = parseFloat(rawMarks)
        if (componentType === 'assignment') {
          student.assignment_obt += obt
          student.assignment_max += maxMarks
        } else if (componentType === 'quiz') {
          student.quiz_obt += obt
          student.quiz_max += maxMarks
        }
      }
    })
    
    // 3. Compute final percentages
    detailedGrades.value = Array.from(studentMap.values()).map(student => {
      const assignments = student.assignment_max > 0 ? Math.round((student.assignment_obt / student.assignment_max) * 100) : null
      const quizzes = student.quiz_max > 0 ? Math.round((student.quiz_obt / student.quiz_max) * 100) : null
      const assignment_scaled = assignments !== null ? ((assignments / 100) * 10).toFixed(2) : null
      const quiz_scaled = quizzes !== null ? ((quizzes / 100) * 10).toFixed(2) : null
      
      return {
        id: student.id,
        subject_id: student.subject_id,
        name: student.name,
        roll_no: student.roll_no,
        assignments,
        assignment_scaled,
        quizzes,
        quiz_scaled,
        midterm: student.midterm,
        final: student.final,
        mid_paper_marks: student.mid_paper_marks,
        mid_marks: student.mid_marks,
        sessional_marks: student.sessional_marks,
        overall: student.overall,
        grade: student.is_pending ? 'Pending' : student.grade,
        gpa: student.gpa,
        is_pending: student.is_pending,
        result_id: student.result_id
      }
    })
    
    calculateDistribution()
    calculateTopPerformers()
  } catch (error) {
    console.error('Error loading grade report:', error)
    detailedGrades.value = []
    gradeDistribution.value = []
    topPerformers.value = []
  } finally {
    loading.value = false
  }
}

function calculateDistribution() {
  const distribution = { 'A+': 0, 'A': 0, 'A-': 0, 'B+': 0, 'B': 0, 'B-': 0, 'C+': 0, 'C': 0, 'C-': 0, 'D': 0, 'F': 0, 'Pending': 0 }
  detailedGrades.value.forEach(s => { if (distribution[s.grade] !== undefined) distribution[s.grade]++ })
  const total = detailedGrades.value.length || 1
  gradeDistribution.value = Object.entries(distribution).filter(([_, count]) => count > 0).map(([grade, count]) => ({ grade, count, percentage: Math.round((count / total) * 100) }))
}

function calculateTopPerformers() {
  topPerformers.value = [...detailedGrades.value].sort((a, b) => b.overall - a.overall).slice(0, 5).map(s => ({ id: s.id, name: s.name, roll_no: s.roll_no, average: s.overall, grade: s.grade }))
}

watch(selectedClass, loadGradeReport)
watch(selectedPeriod, loadGradeReport)

onMounted(() => {
  loadClasses()
  loadGradeReport()
})
</script>
