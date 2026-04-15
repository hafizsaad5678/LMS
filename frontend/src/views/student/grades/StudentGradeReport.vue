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
import { studentService } from '@/services/shared'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, StatCard, StudentSectionHeader } from '@/components/shared/common'
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { useStudentId } from '@/composables/shared/domain/useStudentId'

const { studentId } = useStudentId()
const loading = ref(true)
const studentName = ref('')
const studentEnrollment = ref('')
const report = ref({
  summary: { overall_gpa: '0.00', average_score: 0, total_subjects: 0, total_grades: 0 },
  distribution: { A: 0, B: 0, C: 0, F: 0, other: 0 },
  performance_summary: [],
  subject_performance: []
})

const { alert, showInfo } = useAlert()
const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Grades', href: STUDENT_ROUTES.MY_GRADES.path },
  { name: 'Grade Report' }
]

const statCards = computed(() => [
  { title: 'Overall GPA', value: report.value.summary.overall_gpa, icon: 'bi bi-trophy-fill', type: 'student' },
  { title: 'Average Score', value: `${Math.round(Number(report.value.summary.average_score || 0))}%`, icon: 'bi bi-percent', iconColor: 'text-success', bgColor: 'bg-success-light' },
  { title: 'Total Subjects', value: Number(report.value.summary.total_subjects || 0), icon: 'bi bi-book-fill', type: 'department' },
  { title: 'Total Grades', value: Number(report.value.summary.total_grades || 0), icon: 'bi bi-graph-up', type: 'teacher' }
])

const distributions = computed(() => {
  const dist = report.value.distribution || { A: 0, B: 0, C: 0, F: 0, other: 0 }
  return [
    { label: 'A', value: Number(dist.A || 0), bgClass: 'bg-student-light', textClass: 'text-student' },
    { label: 'B', value: Number(dist.B || 0), bgClass: 'bg-student-light', textClass: 'text-student' },
    { label: 'C', value: Number(dist.C || 0), bgClass: 'bg-warning-light', textClass: 'text-warning' },
    { label: 'F', value: Number(dist.F || 0), bgClass: 'bg-danger-light', textClass: 'text-danger' },
    { label: 'Other', value: Number(dist.other || 0), bgClass: 'bg-light', textClass: 'text-secondary' }
  ]
})

const performanceBars = computed(() => Array.isArray(report.value.performance_summary) ? report.value.performance_summary : [])

const subjectPerformance = computed(() => Array.isArray(report.value.subject_performance) ? report.value.subject_performance : [])

const getPerformanceClass = (p) => p >= 80 ? 'bg-success' : p >= 60 ? 'bg-warning' : 'bg-danger'

const loadData = async () => {
  if (!studentId.value) return
  loading.value = true
  try {
    const [profile, gradeReport] = await Promise.all([
      studentService.getStudent(studentId.value),
      studentService.getGradeReport(studentId.value)
    ])
    studentName.value = profile.full_name
    studentEnrollment.value = profile.enrollment_number
    report.value = {
      summary: gradeReport?.summary || report.value.summary,
      distribution: gradeReport?.distribution || report.value.distribution,
      performance_summary: Array.isArray(gradeReport?.performance_summary) ? gradeReport.performance_summary : [],
      subject_performance: Array.isArray(gradeReport?.subject_performance) ? gradeReport.subject_performance : []
    }
  } catch (err) { console.error(err) } finally { loading.value = false }
}

const exportPDF = () => showInfo('PDF export coming soon!')
const printReport = () => window.print()
onMounted(loadData)
</script>
