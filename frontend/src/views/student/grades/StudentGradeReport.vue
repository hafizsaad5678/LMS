<template>
  <StudentPageTemplate :title="studentName ? `Grade Report: ${studentName}` : 'Grade Report'"
    :subtitle="studentEnrollment ? `Enrollment: ${studentEnrollment} - Comprehensive analysis of your academic performance` : 'Comprehensive analysis of your academic performance'"
    icon="bi bi-graph-up-arrow" :breadcrumbs="breadcrumbs">
    <!-- Alert Message -->
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true"
      :auto-close-duration="3000" @close="alert.show = false" />

    <!-- Overall Statistics -->
    <div class="row g-4 mb-4">
      <div v-for="stat in statCards" :key="stat.title" class="col-md-3">
        <StatCard v-bind="stat" :loading="loading" />
      </div>
    </div>

    <!-- Grade Distribution & Performance Summary -->
    <div class="row g-4 mb-4">
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <StudentSectionHeader title="Grade Distribution" />
          <div class="card-body">
            <div class="row text-center">
              <div v-for="dist in distributions" :key="dist.label" class="col-6 col-md-4 mb-3">
                <div :class="dist.bgClass" class="p-3 rounded">
                  <h4 :class="dist.textClass" class="mb-1">{{ dist.value }}</h4>
                  <small class="text-muted">{{ dist.label }} Grade</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <StudentSectionHeader title="Performance Summary" />
          <div class="card-body">
            <div v-for="perf in performanceBars" :key="perf.label" class="mb-4">
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">{{ perf.label }} ({{ perf.range }})</span>
                <span :class="`badge badge-soft-${perf.color}`">{{ perf.value }}</span>
              </div>
              <div class="progress progress-h-8">
                <div :class="[`progress-bar bg-${perf.color}`, perf.opacity]" :style="{ width: perf.percent + '%' }">
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Subject-wise Performance -->
    <div class="card border-0 shadow-sm">
      <StudentSectionHeader title="Subject-wise Performance" />
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Subject</th>
                <th>Total Assessments</th>
                <th>Average Score</th>
                <th>Best Score</th>
                <th>Worst Score</th>
                <th>Performance</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="subject in subjectPerformance" :key="subject.name">
                <td>
                  <strong>{{ subject.name }}</strong><br>
                  <small class="text-muted">{{ subject.code }}</small>
                </td>
                <td>{{ subject.count }}</td>
                <td><span class="badge badge-soft-success">{{ subject.average }}%</span></td>
                <td><span class="badge badge-soft-info">{{ subject.best }}%</span></td>
                <td><span class="badge badge-soft-warning">{{ subject.worst }}%</span></td>
                <td>
                  <div class="progress h-20px w-100px">
                    <div class="progress-bar" :class="getPerformanceClass(subject.average)"
                      :style="{ width: subject.average + '%' }">
                      <small class="text-white fw-bold">{{ subject.average }}%</small>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Export Button -->
    <div class="mt-4 d-flex gap-2">
      <button class="btn btn-success" @click="exportPDF">
        <i class="bi bi-file-pdf me-2"></i>
        Export as PDF
      </button>
      <button class="btn btn-outline-success" @click="printReport">
        <i class="bi bi-printer me-2"></i>
        Print Report
      </button>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { studentService, studentPanelService } from '@/services/shared'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, StatCard, StudentSectionHeader } from '@/components/shared/common'
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { useStudentId } from '@/composables/shared/domain/useStudentId'

const { studentId } = useStudentId()
const loading = ref(true)
const grades = ref([])
const enrolledSubjects = ref([])
const studentName = ref('')
const studentEnrollment = ref('')

const { alert, showInfo } = useAlert()
const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Grades', href: STUDENT_ROUTES.MY_GRADES.path },
  { name: 'Grade Report' }
]

// GPA & Score Logic (Shared via studentPanelService where possible)
const overallGPA = computed(() => studentPanelService.calculateGPA(grades.value))
const averageScore = computed(() => {
  if (grades.value.length === 0) return 0
  const total = grades.value.reduce((sum, g) => sum + getPercentage(g), 0)
  return Math.round(total / grades.value.length)
})

const statCards = computed(() => [
  { title: 'Overall GPA', value: overallGPA.value, icon: 'bi bi-trophy-fill', type: 'student' },
  { title: 'Average Score', value: `${averageScore.value}%`, icon: 'bi bi-percent', iconColor: 'text-success', bgColor: 'bg-success-light' },
  { title: 'Total Subjects', value: enrolledSubjects.value.length, icon: 'bi bi-book-fill', type: 'department' },
  { title: 'Total Grades', value: grades.value.length, icon: 'bi bi-graph-up', type: 'teacher' }
])

const distributions = computed(() => {
  const dist = { A: 0, B: 0, C: 0, F: 0, other: 0 }
  grades.value.forEach(g => {
    const l = g.grade_value || calculateLetterGrade(getPercentage(g))
    if (l.includes('A')) dist.A++
    else if (l.includes('B')) dist.B++
    else if (l.includes('C')) dist.C++
    else if (l === 'F') dist.F++
    else dist.other++
  })
  return [
    { label: 'A', value: dist.A, bgClass: 'bg-student-light', textClass: 'text-student' },
    { label: 'B', value: dist.B, bgClass: 'bg-student-light', textClass: 'text-student' },
    { label: 'C', value: dist.C, bgClass: 'bg-warning-light', textClass: 'text-warning' },
    { label: 'F', value: dist.F, bgClass: 'bg-danger-light', textClass: 'text-danger' },
    { label: 'Other', value: dist.other, bgClass: 'bg-light', textClass: 'text-secondary' }
  ]
})

const performanceBars = computed(() => {
  const s = { excellent: 0, good: 0, average: 0, belowAverage: 0 }
  grades.value.forEach(g => {
    const p = getPercentage(g)
    if (p >= 90) s.excellent++
    else if (p >= 80) s.good++
    else if (p >= 60) s.average++
    else s.belowAverage++
  })
  const total = grades.value.length || 1
  return [
    { label: 'Excellent', range: '90-100%', value: s.excellent, percent: (s.excellent / total) * 100, color: 'success' },
    { label: 'Good', range: '80-89%', value: s.good, percent: (s.good / total) * 100, color: 'success', opacity: 'bg-opacity-75' },
    { label: 'Average', range: '60-79%', value: s.average, percent: (s.average / total) * 100, color: 'warning' },
    { label: 'Below Average', range: '<60%', value: s.belowAverage, percent: (s.belowAverage / total) * 100, color: 'danger' }
  ]
})

const subjectPerformance = computed(() => {
  const subjects = {}
  grades.value.forEach(g => {
    const name = g.subject_name || g.assignment?.subject?.name || 'Unknown'
    const code = g.subject_code || g.assignment?.subject?.code || 'N/A'
    if (!subjects[name]) subjects[name] = { name, code, scores: [], count: 0 }
    subjects[name].scores.push(getPercentage(g))
    subjects[name].count++
  })
  return Object.values(subjects).map(s => ({
    ...s,
    average: Math.round(s.scores.reduce((a, b) => a + b, 0) / s.scores.length),
    best: Math.max(...s.scores),
    worst: Math.min(...s.scores)
  }))
})

const getPercentage = (g) => Math.round(((g.marks_obtained || g.marks || 0) / (g.total_marks || g.max_marks || 100)) * 100)
const calculateLetterGrade = (p) => {
  if (p >= 90) return 'A+'; if (p >= 80) return 'A'; if (p >= 70) return 'B'; if (p >= 60) return 'C'; return 'F'
}
const getPerformanceClass = (p) => p >= 80 ? 'bg-success' : p >= 60 ? 'bg-warning' : 'bg-danger'

const loadData = async () => {
  if (!studentId.value) return
  loading.value = true
  try {
    const [profile, gradesRes, subjectsRes] = await Promise.all([
      studentService.getStudent(studentId.value),
      studentService.getGrades(studentId.value),
      studentService.getEnrolledSubjects(studentId.value)
    ])
    studentName.value = profile.full_name
    studentEnrollment.value = profile.enrollment_number
    grades.value = Array.isArray(gradesRes) ? gradesRes : (gradesRes.results || [])
    enrolledSubjects.value = Array.isArray(subjectsRes) ? subjectsRes : (subjectsRes.results || [])
  } catch (err) { console.error(err) } finally { loading.value = false }
}

const exportPDF = () => showInfo('PDF export coming soon!')
const printReport = () => window.print()
onMounted(loadData)
</script>
