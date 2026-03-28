<template>
  <StudentPageTemplate :title="studentName ? `Exam Schedule: ${studentName}` : 'Exam Schedule'"
    :subtitle="studentEnrollment ? `Enrollment: ${studentEnrollment} - View your upcoming exams and important dates` : 'View your upcoming exams and important dates'"
    icon="bi bi-journal-check" :breadcrumbs="breadcrumbs">

    <!-- Summary Cards -->
    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <StatCard title="Total Exams" :value="filteredData.length" icon="bi bi-calendar-event-fill"
          bg-color="bg-student-light" icon-color="text-student" />
      </div>
      <div class="col-md-3">
        <StatCard title="Upcoming" :value="upcomingCount" icon="bi bi-hourglass-split" bg-color="bg-warning-light"
          icon-color="text-warning" />
      </div>
      <div class="col-md-3">
        <StatCard title="Completed" :value="completedCount" icon="bi bi-check-circle-fill" bg-color="bg-success-light"
          icon-color="text-success" />
      </div>
      <div class="col-md-3">
        <StatCard title="Subjects" :value="uniqueSubjects" icon="bi bi-book-fill" bg-color="bg-info-light"
          icon-color="text-info" />
      </div>
    </div>

    <!-- Filters -->
    <div class="px-2 pt-1 pb-2">
      <SearchFilter v-model="searchQuery" :show-card="false" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search by subject, exam type..."
        search-col-size="col-md-5 col-12" actions-col-size="col-md-3 col-12" theme="student" @refresh="initData(true)"
        @reset="resetFilters">
        <template #filters>
          <div class="col-md-4 col-12">
            <SelectInput v-model="filterStatus" :options="EXAM_STATUS_OPTIONS" placeholder="All Exams" :no-margin="true"
              @change="filterExams" />
          </div>
        </template>
      </SearchFilter>
    </div>

    <!-- Active Filters Display -->
    <div v-if="filterStatus" class="mt-2 pt-3 border-top">
      <div class="d-flex flex-wrap gap-2 align-items-center">
        <small class="text-muted fw-semibold">Active Filters:</small>
        <span class="badge bg-info-light text-info px-3 py-2">
          <i class="bi bi-flag me-1"></i>
          {{ filterStatus === 'upcoming' ? 'Upcoming' : 'Completed' }}
          <i class="bi bi-x ms-2 cursor-pointer" @click="filterStatus = ''; filterExams()"></i>
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" text="Loading exams..." theme="student" class="py-5" />

    <!-- Error State -->
    <AlertMessage v-if="error" type="error" :message="error" title="Error" />

    <!-- Empty State -->
    <div v-else-if="paginatedExams.length === 0" class="text-center py-5">
      <i class="bi bi-calendar-x display-1 text-muted"></i>
      <h3 class="mt-3">No Exams Found</h3>
      <p class="text-muted">{{ searchQuery || filterStatus ? 'Try adjusting your filters' : 'No exams scheduled' }}</p>
    </div>

    <!-- Exams List -->
    <div v-else class="row g-4 pt-2">
      <div v-for="exam in paginatedExams" :key="exam.id" class="col-md-6 col-xl-4">
        <div class="exam-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden hover-lift">
          <StudentStatusCardHeader
            :header-class="getStatusColor(exam) === 'success' ? 'bg-success-light' : 'bg-student-light'"
            icon-class="bi bi-calendar-event fs-4"
            :badge-class="`badge-soft-${getStatusColor(exam)} px-3 py-2`"
            :badge-text="getStatusText(exam)"
            title-class="text-dark text-truncate-2"
            subtitle-class="text-muted"
          >
            <template #title>{{ exam.subject_name || exam.subject?.name }}</template>
            <template #subtitle>
              <div class="d-flex align-items-center gap-2 mt-2">
                <span class="badge bg-white text-muted border small fw-normal rounded-pill">
                  <i class="bi bi-pencil-square me-1 text-student"></i>{{ exam.exam_type || 'General Exam' }}
                </span>
                <span v-if="exam.total_marks" class="badge bg-white text-muted border small fw-normal rounded-pill">
                  <i class="bi bi-award me-1 text-info"></i>{{ exam.total_marks }} Marks
                </span>
              </div>
            </template>
          </StudentStatusCardHeader>

          <!-- Card Body -->
          <div class="card-body p-4 d-flex flex-column">
             <!-- Time and Duration Row -->
             <div class="row g-2 mb-4">
                <div class="col-6">
                   <div class="d-flex align-items-center gap-2">
                      <div class="icon-box-xs bg-light rounded-circle p-2">
                         <i class="bi bi-clock text-student"></i>
                      </div>
                      <div>
                         <small class="text-muted d-block text-xxs-65">START TIME</small>
                         <span class="small fw-bold">{{ formatTime(exam.start_time) }}</span>
                      </div>
                   </div>
                </div>
                <div class="col-6">
                   <div class="d-flex align-items-center gap-2">
                      <div class="icon-box-xs bg-light rounded-circle p-2">
                         <i class="bi bi-hourglass-split text-info"></i>
                      </div>
                      <div>
                         <small class="text-muted d-block text-xxs-65">DURATION</small>
                         <span class="small fw-bold">{{ exam.duration || 'TBA' }} Min</span>
                      </div>
                   </div>
                </div>
             </div>

             <!-- Location Info -->
             <div class="location-box p-3 border rounded-3 bg-light mb-4 d-flex align-items-center">
                <i class="bi bi-geo-alt-fill text-danger fs-5 me-3"></i>
                <div>
                   <small class="text-muted d-block text-uppercase letter-spacing-1 text-xxs-65">Hall / Room</small>
                   <span class="small fw-bold text-dark">{{ exam.location || exam.room_number || 'To Be Announced' }}</span>
                </div>
             </div>

             <!-- Action Buttons -->
             <div class="mt-auto pt-2">
                <button class="btn btn-student w-100 rounded-3 py-2 fw-bold small" @click="toggleExpand(exam.id)">
                   {{ expandedIds.includes(exam.id) ? 'Hide Instructions' : 'View Instructions' }}
                   <i class="bi ms-1" :class="expandedIds.includes(exam.id) ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                </button>
             </div>

             <!-- Expanded Instructions (Inline) -->
             <div v-if="expandedIds.includes(exam.id)" class="mt-3 animate__animated animate__fadeIn">
                <div class="p-3 bg-warning-light rounded-3 border border-warning-subtle">
                   <h6 class="text-warning small fw-bold mb-2"><i class="bi bi-info-circle me-1"></i>Candidate Info</h6>
                   <div v-if="exam.instructions" class="small text-muted" v-html="exam.instructions"></div>
                   <p v-else class="small text-muted mb-0 fst-italic">No specific instructions provided.</p>
                   
                   <div class="mt-2 pt-2 border-top border-warning-subtle d-flex justify-content-between small">
                      <span class="text-muted">Invigilator:</span>
                      <span class="fw-bold">{{ exam.invigilator_name || 'TBA' }}</span>
                   </div>
                </div>
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
import { generateBreadcrumbs } from '@/utils/navigation'
import { ref, computed, watch, onMounted } from 'vue'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, StatCard, SelectInput, SearchFilter, LoadingSpinner, Pagination, StudentStatusCardHeader } from '@/components/shared/common'
import { studentService } from '@/services/shared'
import studentPanelService from '@/services/student/studentPanelService'
import { formatDate as formatDateUtil, formatTime as formatTimeUtil } from '@/utils/formatters'
import { useEntityList, usePagination } from '@/composables/shared'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { useStudentId } from '@/composables/shared/domain/useStudentId'
import { EXAM_STATUS_OPTIONS } from '@/utils/constants/options'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const { studentName, studentEnrollment, loadProfile } = useStudentBase()
const { studentId } = useStudentId()
const CACHE_KEY = computed(() => `student:${studentId.value}:exams`)

const {
  loading,
  error,
  filteredData,
  loadData,
  applyFilters,
  filters,
  resetFilters: resetFiltersFn
} = useEntityList({
  cacheKey: CACHE_KEY,
  searchFields: ['subject_name', 'exam_type'],
  defaultFilters: { status: '' },
  customFilter: (items, { status }) => {
    let res = items
    const now = new Date()
    if (status === 'upcoming') {
      res = res.filter(e => new Date(e.exam_date) >= now)
    } else if (status === 'completed') {
      res = res.filter(e => new Date(e.exam_date) < now)
    }
    return res.sort((a, b) => new Date(a.exam_date) - new Date(b.exam_date))
  }
})

const { currentPage, totalItems, totalPages, displayPages, paginate, changePage } = usePagination({ pageSize: 10 })

// Update pagination when filtered data changes
watch(filteredData, (newData) => {
  totalItems.value = newData ? newData.length : 0
  currentPage.value = 1
}, { immediate: true })

const paginatedExams = computed(() => {
  return paginate(filteredData.value || [])
})

const expandedIds = ref([])

const resetFilters = () => {
  resetFiltersFn()
  // Any other custom reset logic
  filterStatus.value = ''
}

const toggleExpand = (id) => {
  if (expandedIds.value.includes(id)) {
    expandedIds.value = expandedIds.value.filter(i => i !== id)
  } else {
    expandedIds.value.push(id)
  }
}

// Sync local v-models with composable filters
const searchQuery = computed({
  get: () => filters.value.search,
  set: (val) => filters.value.search = val
})
const filterStatus = computed({
  get: () => filters.value.status,
  set: (val) => filters.value.status = val
})

const upcomingCount = computed(() => {
  const now = new Date()
  return (filteredData.value || []).filter(e => new Date(e.exam_date) >= now).length
})

const completedCount = computed(() => {
  const now = new Date()
  return (filteredData.value || []).filter(e => new Date(e.exam_date) < now).length
})

const uniqueSubjects = computed(() => {
  const subjects = new Set((filteredData.value || []).map(e => e.subject_name || e.subject?.name))
  return subjects.size
})

// Wrapper for load to include stats logic
const initData = async (shouldRefresh = false) => {
  if (!studentId.value) return
  loadProfile()
  // Passing !shouldRefresh as the useCache parameter to loadData
  await loadData(() => studentPanelService.getExamSchedule(studentId.value), !shouldRefresh)
}

const getStatusText = (exam) => {
  const now = new Date()
  if (new Date(exam.exam_date) < now) return 'Completed'
  return 'Upcoming'
}

const getStatusColor = (exam) => {
  const now = new Date()
  if (new Date(exam.exam_date) < now) return 'success'
  return 'warning'
}

// Use shared formatDate utility
const formatDate = (dateString) => {
  if (!dateString) return 'TBA'
  return formatDateUtil(dateString, {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Use shared formatTime utility
const formatTime = (timeString) => formatTimeUtil(timeString) || 'TBA'


// Breadcrumbs and Routes
const breadcrumbs = generateBreadcrumbs('student', 'Exam Schedule')

const filterExams = () => { applyFilters() }

onMounted(() => {
  initData()
})
</script>

<!-- Styles moved to assets/css/custom.css -->
