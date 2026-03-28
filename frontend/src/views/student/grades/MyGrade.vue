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
                        <div class="progress-bar" :class="getProgressBarClass(getPercentage(grade))"
                          :style="{ width: getPercentage(grade) + '%' }"></div>
                      </div>
                      <span class="small">{{ getPercentage(grade) }}%</span>
                    </div>
                  </td>
                  <td>
                    <span class="badge"
                      :class="getGradeBadgeClass(grade.grade_value || calculateLetterGrade(getPercentage(grade)))">
                      {{ grade.grade_value || calculateLetterGrade(getPercentage(grade)) }}
                    </span>
                  </td>
                  <td><small>{{ formatDate(grade.graded_at || grade.created_at) }}</small></td>
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
import { studentService, studentPanelService } from '@/services/shared'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, StatCard, LoadingSpinner, EmptyState, Pagination, SearchFilter, SelectInput } from '@/components/shared/common'
import { useEntityList, usePagination } from '@/composables/shared'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { formatDate } from '@/utils/formatters'
import { getProgressBarClass, getGradeBadgeClass, calculateLetterGrade } from '@/utils/badgeHelpers'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const { studentId, studentName, studentEnrollment, loadProfile } = useStudentBase()
const enrolledSubjects = ref([])

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

const averageScore = computed(() => {
  if (grades.value.length === 0) return 0
  const total = grades.value.reduce((sum, g) => sum + getPercentage(g), 0)
  return Math.round(total / grades.value.length)
})

const statsCards = computed(() => [
  { title: 'Overall GPA', value: studentPanelService.calculateGPA(grades.value), icon: 'bi bi-trophy-fill', type: 'student' },
  { title: 'Total Subjects', value: enrolledSubjects.value.length, icon: 'bi bi-book-fill', type: 'department' },
  { title: 'Average Score', value: `${averageScore.value}%`, icon: 'bi bi-star-fill', type: 'teacher' }
])

const getPercentage = (g) => Math.round(((g.marks_obtained || g.marks || 0) / (g.total_marks || g.max_marks || 100)) * 100)

const resetFilters = () => {
  filters.value = { search: '', subject: '' }
}

onMounted(async () => {
  if (!studentId) return

  loadProfile()

  // Load grades via useEntityList
  await loadData(() => studentService.getGrades(studentId))

  // Load additional subject data
  try {
    const subjectsRes = await studentService.getEnrolledSubjects(studentId)
    enrolledSubjects.value = Array.isArray(subjectsRes) ? subjectsRes : (subjectsRes.results || [])
  } catch (err) {
    console.error('Error loading subjects:', err)
  }
})
</script>
