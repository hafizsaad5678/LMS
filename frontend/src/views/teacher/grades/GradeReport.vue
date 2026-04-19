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
                  <th class="text-center">Assignments</th>
                  <th class="text-center">Quizzes</th>
                  <th class="text-center">Midterm</th>
                  <th class="text-center">Final</th>
                  <th class="text-center">Overall</th>
                  <th class="text-center">Grade</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in detailedGrades" :key="student.id">
                  <td>
                    <div class="fw-bold text-dark">{{ student.name || 'Unknown Student' }}</div>
                    <small v-if="student.roll_no" class="text-muted">{{ student.roll_no }}</small>
                  </td>
                  <td class="text-center">{{ student.assignments }}%</td>
                  <td class="text-center">{{ student.quizzes }}%</td>
                  <td class="text-center">{{ student.midterm }}%</td>
                  <td class="text-center">{{ student.final }}%</td>
                  <td class="text-center fw-bold text-dark">{{ student.overall }}%</td>
                  <td class="text-center">
                    <span v-if="student.is_pending" class="badge px-3 bg-warning-subtle text-warning-emphasis">Pending</span>
                    <span v-else :class="['badge px-3', getGradeBadge(student.grade)]">{{ student.grade }}</span>
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
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { StatCard, AlertMessage, LoadingSpinner } from '@/components/shared/common'
import GradeDistributionChart from '@/components/teacher/grades/GradeDistributionChart.vue'
import TopPerformersList from '@/components/teacher/grades/TopPerformersList.vue'
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

const statsCards = computed(() => [
  { title: 'Class Average', value: averageGrade.value, icon: 'bi bi-award', type: 'student' },
  { title: 'Total Students', value: detailedGrades.value.length, icon: 'bi bi-people', type: 'teacher' },
  { title: 'Pending', value: detailedGrades.value.filter(s => s.is_pending).length, icon: 'bi bi-hourglass-split', type: 'finance' },
  { title: 'Excellent (A)', value: detailedGrades.value.filter(s => s.overall >= 85).length, icon: 'bi bi-star', type: 'department' },
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
    const response = await teacherPanelService.getAllMarks(params)
    const marks = response.results || response || []
    
    if (marks.length === 0) {
      detailedGrades.value = []
      gradeDistribution.value = []
      topPerformers.value = []
      return
    }
    
    const studentMap = new Map()
    marks.forEach(mark => {
      const studentId = mark.student || mark.student_id
      if (!studentMap.has(studentId)) {
        studentMap.set(studentId, {
          id: studentId,
          name: mark.student_name || 'Unknown Student',
          roll_no: mark.student_roll_no || mark.roll_no || mark.student_enrollment || null,
          assignments: 0, quizzes: 0, midterm: 0, final: 0,
          componentCount: { assignments: 0, quizzes: 0, midterm: 0, final: 0 },
          gradedCount: { assignments: 0, quizzes: 0, midterm: 0, final: 0 }
        })
      }
      const student = studentMap.get(studentId)
      const componentType = mark.component_type || 'assignment'
      const isGraded = mark.marks_obtained !== null && mark.marks_obtained !== undefined
      const percentage = typeof mark.percentage === 'number'
        ? mark.percentage
        : (isGraded && mark.max_marks)
          ? (parseFloat(mark.marks_obtained) / parseFloat(mark.max_marks)) * 100
          : 0
      const typeMap = { assignment: 'assignments', quiz: 'quizzes', midterm: 'midterm', final: 'final' }
      const key = typeMap[componentType] || 'assignments'
      if (isGraded) {
        student[key] += percentage
        student.componentCount[key]++
        student.gradedCount[key]++
      }
    })
    
    detailedGrades.value = Array.from(studentMap.values()).map(student => {
      const avg = (key) => student.componentCount[key] > 0 ? Math.round(student[key] / student.componentCount[key]) : 0
      const components = [avg('assignments'), avg('quizzes'), avg('midterm'), avg('final')].filter(v => v > 0)
      const gradedComponents = ['assignments', 'quizzes', 'midterm', 'final'].reduce((sum, key) => sum + (student.gradedCount[key] || 0), 0)
      const overall = components.length > 0 ? Math.round(components.reduce((sum, v) => sum + v, 0) / components.length) : 0
      const isPending = gradedComponents === 0
      return {
        id: student.id,
        name: student.name,
        roll_no: student.roll_no,
        assignments: avg('assignments'),
        quizzes: avg('quizzes'),
        midterm: avg('midterm'),
        final: avg('final'),
        overall,
        grade: isPending ? 'Pending' : calculateGrade(overall),
        is_pending: isPending
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
