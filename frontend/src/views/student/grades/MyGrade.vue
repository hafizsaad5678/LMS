<template>
  <StudentPageTemplate :title="studentName ? `Grades for ${studentName}` : 'My Grades'"
    :subtitle="studentEnrollment ? `Enrollment: ${studentEnrollment}` : 'View your academic performance and grades'"
    icon="bi bi-award" :breadcrumbs="breadcrumbs">
    <!-- Summary Cards -->
    <div class="row g-4 mb-4">
      <div v-for="stat in statsCards" :key="stat.title" class="col-md-4">
        <StatCard v-bind="stat" :loading="loading" />
      </div>
    </div>

    <!-- Filters Section -->
    <div class="px-2 pt-1 pb-2">
      <SearchFilter v-model="filters.search" :show-card="false" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search by subject or assignment..."
        search-col-size="col-md-5" actions-col-size="col-md-3" theme="student" @refresh="loadData" @reset="resetFilters">
        <template #filters>
          <div class="col-md-4">
            <SelectInput v-model="filters.subject" :options="subjectOptions" placeholder="All Subjects"
              :no-margin="true" />
          </div>
        </template>
      </SearchFilter>
    </div>
    <LoadingSpinner v-if="loading" text="Loading grades..." theme="student" class="py-5" />
    <AlertMessage v-else-if="error" type="error" :message="error" />
    <EmptyState v-else-if="grades.length === 0" title="No Grades Available" icon="bi bi-clipboard-data" />

    <div v-else>
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-bottom">
          <h5 class="mb-0">Grade Details</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Subject</th>
                  <th>Assignment/Exam</th>
                  <th>Marks</th>
                  <th>Percentage</th>
                  <th>Grade</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="grade in paginatedGrades" :key="grade.id">
                  <td>
                    <strong>{{ grade.subject_name || grade.assignment?.subject?.name }}</strong><br>
                    <small class="text-muted">{{ grade.subject_code || grade.assignment?.subject?.code }}</small>
                  </td>
                  <td>{{ grade.assignment_title || grade.assignment?.title || 'Assessment' }}</td>
                  <td><span class="badge badge-soft-success">{{ grade.marks_obtained || 0 }}/{{ grade.total_marks || 100
                  }}</span></td>
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="progress flex-grow-1 me-2 progress-h-8">
                        <div class="progress-bar" :class="getProgressBarClass(resolvePercentage(grade))"
                          :style="{ width: resolvePercentage(grade) + '%' }"></div>
                      </div>
                      <span class="small">{{ resolvePercentage(grade) }}%</span>
                    </div>
                  </td>
                  <td>
                    <span class="badge"
                      :class="getGradeBadgeClass(resolveGradeValue(grade))">
                      {{ resolveGradeValue(grade) }}
                    </span>
                  </td>
                  <td><small>{{ formatDate(grade.graded_at || grade.created_at) }}</small></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm mt-4">
        <div class="card-header bg-white border-bottom">
          <h5 class="mb-0">Pending Grade List</h5>
        </div>
        <div class="card-body p-0">
          <div v-if="loadingPending" class="p-4 text-muted small">Loading pending grades...</div>
          <div v-else-if="pendingGradeItems.length === 0" class="p-4 text-muted small">No pending grades right now.</div>
          <div v-else class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Subject</th>
                  <th>Pending Detail</th>
                  <th>Status</th>
                  <th>Updated At</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in pendingGradeItems" :key="item.id">
                  <td>
                    <strong>{{ item.subject_name || 'N/A' }}</strong><br>
                    <small class="text-muted">{{ item.subject_code || '-' }}</small>
                  </td>
                  <td>{{ item.title || 'Grades not posted yet' }}</td>
                  <td><span class="badge badge-soft-warning">Pending Grading</span></td>
                  <td><small>{{ formatDate(item.updated_at || item.created_at) }}</small></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <Pagination v-if="totalPages > 1" :current-page="currentPage" :total-pages="totalPages"
        :display-pages="displayPages" theme="student" @change="changePage" />
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { studentService } from '@/services/shared'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, StatCard, LoadingSpinner, EmptyState, Pagination, SearchFilter, SelectInput } from '@/components/shared/common'
import { useEntityList, usePagination } from '@/composables/shared'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { formatDate } from '@/utils/formatters'
import { getProgressBarClass, getGradeBadgeClass, calculateLetterGrade } from '@/utils/badgeHelpers'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const { studentId, studentName, studentEnrollment, loadProfile } = useStudentBase()
const gradeSummary = ref({
  overall_gpa: '0.00',
  average_score: 0,
  total_subjects: 0,
  total_grades: 0
})
const pendingGradeItems = ref([])
const loadingPending = ref(false)

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Grades', href: STUDENT_ROUTES.MY_GRADES.path },
  { name: 'My Grades' }
]

const {
  loading,
  error,
  data: grades,
  filteredData: filteredGrades,
  filters,
  loadData
} = useEntityList({
  cacheKey: `student:${studentId}:grades`,
  searchFields: ['subject_name', 'assignment_title', 'assignment.title', 'subject.name'],
  defaultFilters: { subject: '' },
  customFilter: (items, f) => {
    let res = items
    if (f.subject) {
      res = res.filter(g => (g.subject_name || g.assignment?.subject?.name) === f.subject)
    }
    return res
  }
})

const { currentPage, totalItems, totalPages, displayPages, paginate, changePage } = usePagination({ pageSize: 15 })

// Update pagination when filtered data changes
watch(filteredGrades, (newData) => {
  totalItems.value = newData ? newData.length : 0
  currentPage.value = 1
}, { immediate: true })

const paginatedGrades = computed(() => paginate(filteredGrades.value || []))

const subjectOptions = computed(() => {
  const subs = [...new Set(grades.value.map(g => g.subject_name || g.assignment?.subject?.name).filter(Boolean))]
  return subs.sort().map(s => ({ value: s, label: s }))
})

const statsCards = computed(() => [
  {
    title: 'Pending Grades',
    value: pendingGradeItems.value.length,
    icon: 'bi bi-hourglass-split',
    type: 'finance'
  },
  { title: 'Total Subjects', value: Number(gradeSummary.value.total_subjects || 0), icon: 'bi bi-book-fill', type: 'department' },
  { title: 'Average Score', value: `${Math.round(Number(gradeSummary.value.average_score || 0))}%`, icon: 'bi bi-star-fill', type: 'teacher' }
])

const resolvePercentage = (grade) => {
  const backendPercentage = Number(grade?.percentage)
  if (Number.isFinite(backendPercentage)) {
    return Math.round(backendPercentage)
  }

  const marks = Number(grade?.marks_obtained ?? grade?.marks ?? 0)
  const totalMarks = Number(grade?.total_marks ?? grade?.max_marks ?? 100)
  if (!Number.isFinite(totalMarks) || totalMarks <= 0) return 0

  return Math.round((marks / totalMarks) * 100)
}

const resolveGradeValue = (grade) => {
  if (grade?.grade_value) return grade.grade_value
  return calculateLetterGrade(resolvePercentage(grade))
}

const resetFilters = () => {
  filters.value = { search: '', subject: '' }
}

const loadGradeSummary = async () => {
  try {
    const report = await studentService.getGradeReport(studentId)
    const summary = report?.summary || {}
    gradeSummary.value = {
      overall_gpa: String(summary.overall_gpa ?? '0.00'),
      average_score: Number(summary.average_score ?? 0),
      total_subjects: Number(summary.total_subjects ?? 0),
      total_grades: Number(summary.total_grades ?? 0)
    }
  } catch (err) {
    console.error('Error loading grade summary:', err)
  }
}

const loadPendingGrades = async () => {
  if (!studentId) return

  try {
    loadingPending.value = true
    const [subjectsRes, gradesRes] = await Promise.all([
      studentService.getEnrolledSubjects(studentId),
      studentService.getGrades(studentId)
    ])

    const subjects = subjectsRes?.results || subjectsRes || []
    const gradedEntries = gradesRes?.results || gradesRes || []

    const gradedSubjectKeys = new Set(
      gradedEntries.map(g => `${g.subject_name || g.assignment?.subject?.name || ''}|${g.subject_code || g.assignment?.subject?.code || ''}`)
    )

    pendingGradeItems.value = subjects
      .filter(s => {
        const name = s.subject_name || s.subject?.name || ''
        const code = s.subject_code || s.subject?.code || ''
        
        // Only count as pending if teacher has actually created assignments or grade components
        const hasAssessments = (Number(s.total_components || 0) + Number(s.total_assignments || 0)) > 0
        
        return hasAssessments && !gradedSubjectKeys.has(`${name}|${code}`)
      })
      .map(s => ({
        id: s.id || `${s.subject_name || s.subject?.name}-${s.subject_code || s.subject?.code}`,
        title: 'No grade published yet for this subject',
        subject_name: s.subject_name || s.subject?.name,
        subject_code: s.subject_code || s.subject?.code,
        updated_at: s.updated_at || s.created_at,
        created_at: s.created_at
      }))
  } catch (err) {
    console.error('Error loading pending grades:', err)
    pendingGradeItems.value = []
  } finally {
    loadingPending.value = false
  }
}

onMounted(async () => {
  if (!studentId) return

  loadProfile()

  await Promise.all([
    loadData(() => studentService.getGrades(studentId)),
    loadGradeSummary(),
    loadPendingGrades()
  ])
})
</script>
