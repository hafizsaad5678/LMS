<template>
  <TeacherPageTemplate title="Student Attendance History" subtitle="View attendance records and statistics"
    icon="bi bi-calendar-check" :breadcrumbs="breadcrumbs" :actions="actions" :show-content-card="false">
    <template v-if="studentId && !loading" #stats>
      <StudentInfoCard :student-info="studentInfo" class="mb-4" />
      <div class="row g-3">
        <div v-for="stat in statsCards" :key="stat.title" class="col-md-3 col-6">
          <StatCard v-bind="stat" />
        </div>
      </div>
    </template>

    <template v-if="studentId && !loading" #filters>
      <div class="row g-3 align-items-end">
        <div class="col-md-4 col-12">
          <select v-model="filters.dateRange" class="form-select">
            <option value="all">All Time</option>
            <option value="thisMonth">This Month</option>
            <option value="lastMonth">Last Month</option>
            <option value="thisWeek">This Week</option>
            <option value="lastWeek">Last Week</option>
          </select>
        </div>
        <div class="col-md-4 col-12">
          <select v-model="filters.subject" class="form-select">
            <option value="">All Subjects</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }} ({{ subject.code }})
            </option>
          </select>
        </div>
        <div class="col-md-4 col-12 d-flex justify-content-end">
          <div class="d-flex gap-2">
            <button @click="loadAttendance" class="btn btn-teacher-outline" type="button">
              <i class="bi bi-arrow-clockwise me-2"></i>Refresh
            </button>
            <button @click="resetFilters" class="btn btn-outline-secondary" type="button">
              <i class="bi bi-x-circle me-2"></i>Reset
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- No student ID provided -->
    <EmptyState v-if="!studentId" icon="bi bi-calendar-check" title="Please Select a Student"
      subtitle="Choose a student to view their attendance history." button-text="Go to Student List"
      button-icon="bi bi-list-ul" button-variant="btn-teacher-primary"
      @action="router.push({ name: TEACHER_ROUTES.STUDENT_LIST.name })" />

    <LoadingSpinner v-else-if="loading" text="Loading attendance records..." theme="teacher" />

    <div v-else>
      <!-- Attendance Records -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-teacher-light border-0">
          <h5 class="mb-0 fw-bold text-teacher">
            <i class="bi bi-list-ul me-2"></i>Attendance Records
          </h5>
        </div>
        <div class="card-body p-0">
          <EmptyState v-if="filteredAttendance.length === 0" icon="bi bi-calendar-x"
            title="No Attendance Records Found" subtitle="No attendance records match your current filters." />
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
        title="Other Students" icon="bi bi-people" empty-message="No other students found" class="mt-4"
        header-class="bg-teacher-light" header-text-class="text-teacher fw-bold">
        <template #actions="{ student }">
          <button @click="viewStudentAttendance(student)" class="btn btn-sm flex-grow-1"
            :class="student.id.toString() === studentId ? 'btn-teacher-primary' : 'btn-teacher-outline'"
            :disabled="student.id.toString() === studentId">
            <i class="bi bi-calendar-check me-1"></i>
            {{ student.id.toString() === studentId ? 'Current Student' : 'View Attendance' }}
          </button>
          <button @click="viewStudentProfile(student)" class="btn btn-sm btn-teacher-outline">
            <i class="bi bi-person me-1"></i>Profile
          </button>
        </template>
      </StudentListCard>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { LoadingSpinner, StatCard, EmptyState } from '@/components/shared/common'
import { StudentInfoCard, StudentListCard } from '@/components/teacher/shared'
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
const { filters, filteredItems: filteredAttendance, resetFilters } = useFilterLogic(
  attendanceRecords,
  { dateField: 'session_date', subjectField: 'subject_id' }
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

const statsCards = computed(() => [
  { title: 'Total Classes', value: attendanceStats.value.totalClasses, icon: 'bi bi-calendar-check', bgColor: 'bg-teacher-light', iconColor: 'text-teacher' },
  { title: 'Present', value: attendanceStats.value.presentCount, icon: 'bi bi-check-circle', bgColor: 'bg-teacher-light', iconColor: 'text-success' },
  { title: 'Absent', value: attendanceStats.value.absentCount, icon: 'bi bi-x-circle', bgColor: 'bg-teacher-light', iconColor: 'text-danger' },
  { title: 'Attendance Rate', value: `${attendanceStats.value.percentage}%`, icon: 'bi bi-percent', bgColor: 'bg-teacher-light', iconColor: 'text-teacher' }
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
