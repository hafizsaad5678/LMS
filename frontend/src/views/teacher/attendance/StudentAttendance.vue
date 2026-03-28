<template>
  <TeacherPageTemplate title="Student Attendance History" subtitle="View attendance records and statistics"
    icon="bi bi-calendar-check" :breadcrumbs="breadcrumbs" :actions="actions" :show-content-card="false">
    <!-- No student ID provided -->
    <div v-if="!studentId" class="text-center py-5">
      <i class="bi bi-calendar-check display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Student</h4>
      <p class="text-muted">Choose a student to view their attendance history.</p>
      <button @click="router.push({ name: TEACHER_ROUTES.STUDENT_LIST.name })" class="btn btn-teacher-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Student List
      </button>
    </div>

    <LoadingSpinner v-else-if="loading" text="Loading attendance records..." theme="teacher" />

    <div v-else>
      <!-- Student Info Header -->
      <StudentInfoCard :student-info="studentInfo" class="mb-4" />

      <!-- Attendance Statistics -->
      <StatsRow :stats="statsData" />

      <!-- Filters -->
      <SearchFilter v-model="searchQuery" :show-card="true" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search records..." search-col-size="col-md-3"
        actions-col-size="col-md-3" theme="teacher" @refresh="loadAttendance" @reset="resetFilters">
        <template #filters>
          <div class="col-md-2">
            <select v-model="filters.dateRange" class="form-select">
              <option value="all">All Time</option>
              <option value="thisMonth">This Month</option>
              <option value="lastMonth">Last Month</option>
              <option value="thisWeek">This Week</option>
              <option value="lastWeek">Last Week</option>
            </select>
          </div>
          <div class="col-md-2">
            <SelectInput v-model="filters.status" :options="ATTENDANCE_STATUS_OPTIONS" placeholder="All Status" />
          </div>
          <div class="col-md-2">
            <select v-model="filters.subject" class="form-select">
              <option value="">All Subjects</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }} ({{ subject.code }})
              </option>
            </select>
          </div>
        </template>
      </SearchFilter>

      <!-- Attendance Records -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-gradient-blue border-0">
          <h5 class="mb-0">
            <i class="bi bi-list-ul me-2"></i>Attendance Records
          </h5>
        </div>
        <div class="card-body p-0">
          <div v-if="filteredAttendance.length === 0" class="text-center py-5">
            <i class="bi bi-calendar-x display-1 text-muted"></i>
            <h5 class="text-muted mt-3">No Attendance Records Found</h5>
            <p class="text-muted">No attendance records match your current filters.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Date</th>
                  <th>Subject</th>
                  <th>Status</th>
                  <th>Marked By</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in filteredAttendance" :key="record.id">
                  <td>
                    <strong>{{ formatDate(record.session_date) }}</strong>
                  </td>
                  <td>
                    <div>
                      <strong>{{ record.subject_name }}</strong>
                      <br>
                      <small class="text-muted">{{ record.subject_code }}</small>
                    </div>
                  </td>
                  <td>
                    <span :class="getStatusBadgeClass(record.status)">
                      <i :class="getStatusIcon(record.status)" class="me-1"></i>
                      {{ getStatusText(record.status) }}
                    </span>
                  </td>
                  <td>
                    <div>
                      <strong>{{ record.marked_by_name || 'System' }}</strong>
                      <br>
                      <small class="text-muted">Teacher</small>
                    </div>
                  </td>
                  <td>
                    <small class="text-muted">{{ formatTime(record.marked_at) }}</small>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Other Students Section -->
      <StudentListCard :students="otherStudents" :loading="loadingOtherStudents" :current-student-id="studentId"
        title="Other Students" icon="bi bi-people" empty-message="No other students found" class="mt-4">
        <template #actions="{ student }">
          <button @click="viewStudentAttendance(student)" class="btn btn-sm flex-grow-1"
            :class="student.id.toString() === studentId ? 'btn-teacher-primary' : 'btn-teacher-outline'"
            :disabled="student.id.toString() === studentId">
            <i class="bi bi-calendar-check me-1"></i>
            {{ student.id.toString() === studentId ? 'Current Student' : 'View Attendance' }}
          </button>
          <button @click="viewStudentProfile(student)" class="btn btn-sm btn-outline-secondary">
            <i class="bi bi-person me-1"></i>Profile
          </button>
        </template>
      </StudentListCard>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { SearchFilter, SelectInput, LoadingSpinner } from '@/components/shared/common'
import { StudentInfoCard, StudentListCard, StatsRow } from '@/components/teacher/shared'
import { useStudentData } from '@/composables/teacher/useStudentData'
import { useAttendanceData } from '@/composables/teacher/useAttendanceData'
import { useFilterLogic } from '@/composables/teacher/useFilterLogic'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { getAttendanceBadgeClass, getAttendanceIcon } from '@/utils/badgeHelpers'
import { ATTENDANCE_STATUS_OPTIONS, getOptionLabel } from '@/utils/constants/options'

const router = useRouter()
const route = useRoute()
const { studentInfo, loadStudentInfo, loadAllStudents, getEnrolledSubjects } = useStudentData()
const { attendanceRecords, loading, calculateStats, loadStudentAttendance } = useAttendanceData()
const { searchQuery, filters, filteredItems: filteredAttendance, resetFilters } = useFilterLogic(
  attendanceRecords,
  { searchFields: ['subject_name', 'subject_code'], dateField: 'session_date', statusField: 'status', subjectField: 'subject_id' }
)

const studentId = computed(() => route.params.id || route.query.student)
const loadingOtherStudents = ref(false)
const subjects = ref([])
const otherStudents = ref([])

const breadcrumbs = computed(() => [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Students', href: TEACHER_ROUTES.STUDENT_LIST.path },
  { name: studentInfo.value.name || 'Student Profile', href: `${TEACHER_ROUTES.STUDENT_PROFILE.path}/${studentId.value}` },
  { name: 'Attendance History' }
])

const actions = computed(() => [
  {
    label: 'Back to Profile',
    icon: 'bi bi-arrow-left',
    variant: 'btn-teacher-outline',
    onClick: () => router.push({ name: TEACHER_ROUTES.STUDENT_PROFILE.name, params: { id: studentId.value } })
  },
  {
    label: 'Mark Attendance',
    icon: 'bi bi-plus-circle',
    variant: 'btn-teacher-outline',
    onClick: () => router.push({ name: TEACHER_ROUTES.MARK_ATTENDANCE.name, query: { student: studentId.value } })
  }
])

const attendanceStats = computed(() => calculateStats(attendanceRecords.value))

const statsData = computed(() => [
  { label: 'Total Classes', value: attendanceStats.value.totalClasses, icon: 'bi bi-calendar-check', bgClass: 'bg-gradient-blue', colClass: 'col-md-3 col-6' },
  { label: 'Present', value: attendanceStats.value.presentCount, icon: 'bi bi-check-circle', bgClass: 'bg-gradient-teal', colClass: 'col-md-3 col-6' },
  { label: 'Absent', value: attendanceStats.value.absentCount, icon: 'bi bi-x-circle', bgClass: 'bg-gradient-amber', colClass: 'col-md-3 col-6' },
  { label: 'Attendance Rate', value: `${attendanceStats.value.percentage}%`, icon: 'bi bi-percent', bgClass: 'bg-gradient-cyan', colClass: 'col-md-3 col-6' }
])

const loadAttendance = async () => {
  if (!studentId.value) return

  try {
    await loadStudentInfo(studentId.value)
    const enrolledSubjects = await getEnrolledSubjects(studentId.value)
    await loadStudentAttendance(studentId.value)

    const uniqueSubjectsMap = new Map()
    enrolledSubjects.forEach(sub => uniqueSubjectsMap.set(sub.id, sub))

    attendanceRecords.value.forEach(record => {
      const sId = record.subject_id
      if (sId && !uniqueSubjectsMap.has(sId)) {
        uniqueSubjectsMap.set(sId, {
          id: sId,
          name: record.subject_name,
          code: record.subject_code
        })
      }
    })

    subjects.value = Array.from(uniqueSubjectsMap.values())
    await loadOtherStudentsData()
  } catch (err) {
    console.error('Error loading attendance:', err)
  }
}

const loadOtherStudentsData = async () => {
  loadingOtherStudents.value = true
  try {
    otherStudents.value = await loadAllStudents()
  } finally {
    loadingOtherStudents.value = false
  }
}

const viewStudentAttendance = (student) => router.push({ name: TEACHER_ROUTES.STUDENT_ATTENDANCE.name, params: { id: student.id } })
const viewStudentProfile = (student) => router.push({ name: TEACHER_ROUTES.STUDENT_PROFILE.name, params: { id: student.id } })

const formatDate = (dateString) => formatDateUtil(dateString, { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' })
const formatTime = (dateTimeString) => dateTimeString ? new Date(dateTimeString).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : 'N/A'
const getStatusBadgeClass = (status) => `badge ${getAttendanceBadgeClass(status)}`
const getStatusIcon = (status) => getAttendanceIcon(status)
const getStatusText = (status) => getOptionLabel(ATTENDANCE_STATUS_OPTIONS, status)

watch(studentId, () => studentId.value && loadAttendance(), { immediate: true })
</script>
