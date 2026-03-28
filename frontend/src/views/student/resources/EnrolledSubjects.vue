<template>
  <StudentPageTemplate title="My Subjects" subtitle="View all your enrolled subjects for this semester"
    icon="bi bi-book-half" :breadcrumbs="breadcrumbs">
    <!-- Loading State -->
    <LoadingSpinner v-if="loading" text="Loading subjects..." theme="student" />

    <!-- Error State -->
    <AlertMessage v-else-if="error" type="error" :message="error" title="Error" />

    <!-- Empty State -->
    <div v-else-if="subjects.length === 0" class="text-center py-5">
      <i class="bi bi-inbox display-1 text-muted"></i>
      <h3 class="mt-3">No Subjects Enrolled</h3>
      <p class="text-muted">You haven't enrolled in any subjects yet.</p>
    </div>

    <!-- Subjects Grid -->
    <div v-else class="row g-4">
      <div v-for="subject in subjects" :key="subject.id" class="col-12 col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-lift">
          <div class="card-body">
            <div class="d-flex align-items-start mb-3">
              <div class="flex-shrink-0">
                <div class="bg-gradient-emerald rounded p-3">
                  <i class="bi bi-book-fill text-student fs-4"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <h5 class="card-title mb-1">{{ subject.subject_name || subject.subject?.name }}</h5>
                <p class="text-muted small mb-0">{{ subject.subject_code || subject.subject?.code }}</p>
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="text-muted small">Credit Hours</span>
                <span class="badge badge-soft-success">{{ subject.subject?.credit_hours || subject.credit_hours || 3 }}
                  Credits</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="text-muted small">Semester</span>
                <span class="badge badge-soft-success">{{ subject.semester_name || 'Current' }}</span>
              </div>
              <div v-if="subject.enrollment_date" class="d-flex justify-content-between align-items-center">
                <span class="text-muted small">Enrolled</span>
                <span class="text-muted small">{{ formatDate(subject.enrollment_date) }}</span>
              </div>
            </div>

            <div class="d-grid gap-2">
              <button class="btn btn-student-outline btn-sm" @click="viewSubjectDetails(subject)">
                <i class="bi bi-eye me-1"></i>
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <Pagination v-if="totalPages > 1" :current-page="currentPage" :total-pages="totalPages"
      :display-pages="displayPages" theme="student" @change="changePage" />
  </StudentPageTemplate>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, LoadingSpinner, Pagination } from '@/components/shared/common'
import { studentService } from '@/services/shared'
import { useEntityList, usePagination } from '@/composables/shared'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const { studentId } = useStudentBase()

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'My Subjects' }
]

const {
  loading,
  error,
  filteredData,
  loadData
} = useEntityList({
  cacheKey: `student:${studentId}:subjects`
})

const { currentPage, totalItems, totalPages, displayPages, paginate, changePage } = usePagination({ pageSize: 9 })

// Update pagination when filtered data changes
watch(filteredData, (newData) => {
  totalItems.value = newData ? newData.length : 0
  currentPage.value = 1
}, { immediate: true })

const subjects = computed(() => {
  return paginate(filteredData.value || [])
})

const viewSubjectDetails = (subjectItem) => {
  const subId = subjectItem.subject?.id || subjectItem.subject_id || subjectItem.subject
  if (subId) router.push({ name: STUDENT_ROUTES.SUBJECT_PROFILE.name, params: { id: subId } })
}

const formatDate = (dateString) => formatDateUtil(dateString)

onMounted(() => {
  if (studentId) loadData(() => studentService.getEnrolledSubjects(studentId))
  else error.value = 'Student ID not found.'
})
</script>

<!-- Using Bootstrap classes only -->
