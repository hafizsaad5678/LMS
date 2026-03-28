<template>
  <TeacherPageTemplate title="Attendance Report" subtitle="View and analyze student attendance patterns"
    icon="bi bi-graph-up" :breadcrumbs="breadcrumbs" :actions="actions">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true"
      :auto-close-duration="3000" @close="alert.show = false" />

    <template #stats>
      <div class="row g-3 mb-4">
        <div v-for="stat in statsCards" :key="stat.title" class="col-md-3 col-6">
          <StatCard v-bind="stat" />
        </div>
      </div>
    </template>

    <template #filters>
      <SearchFilter v-model="searchQuery" :show-status-filter="false" :show-labels="false"
        search-placeholder="Search students..." search-col-size="col-md-3" actions-col-size="col-md-3" theme="teacher"
        @refresh="loadAttendanceReport" @reset="resetFilters">
        <template #filters>
          <div class="col-md-3">
            <select v-model="filters.class" class="form-select">
              <option value="">All Classes</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                {{ cls.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <select v-model="filters.month" class="form-select">
              <option value="">All Time</option>
              <option value="2025-12">December 2025</option>
              <option value="2025-11">November 2025</option>
              <option value="2025-10">October 2025</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <LoadingSpinner v-if="loading" text="Loading attendance report..." theme="teacher" />

    <div v-else class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom">
        <div class="d-flex justify-content-between align-items-center">
          <h6 class="mb-0 fw-semibold">
            <i class="bi bi-table me-2 text-teacher"></i>Student Attendance Report
          </h6>
          <button @click="exportReport" class="btn btn-sm btn-teacher-outline">
            <i class="bi bi-download me-1"></i>Export
          </button>
        </div>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Student</th>
                <th>Roll No</th>
                <th class="text-center">Present</th>
                <th class="text-center">Late</th>
                <th class="text-center">Absent</th>
                <th class="text-center">Leave</th>
                <th class="text-center">Total</th>
                <th class="text-center">Attendance %</th>
                <th class="text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in filteredStudents" :key="student.id">
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar-circle avatar-circle-sm me-2">
                      {{ student.name.charAt(0) }}
                    </div>
                    <span class="fw-semibold">{{ student.name }}</span>
                  </div>
                </td>
                <td>{{ student.roll_no }}</td>
                <td class="text-center">
                  <span class="badge bg-success">{{ student.present }}</span>
                </td>
                <td class="text-center">
                  <span class="badge bg-warning text-dark">{{ student.late }}</span>
                </td>
                <td class="text-center">
                  <span class="badge bg-danger">{{ student.absent }}</span>
                </td>
                <td class="text-center">
                  <span class="badge bg-info">{{ student.leave }}</span>
                </td>
                <td class="text-center">
                  <span class="badge bg-secondary">{{ student.total }}</span>
                </td>
                <td class="text-center">
                  <div class="d-flex align-items-center justify-content-center">
                    <div class="progress me-2 progress-w-60 progress-h-8">
                      <div class="progress-bar" :class="getAttendanceColor(student.percentage)"
                        :style="{ width: `${student.percentage}%` }"></div>
                    </div>
                    <span class="fw-semibold">{{ student.percentage }}%</span>
                  </div>
                </td>
                <td class="text-center">
                  <span :class="['badge', getStatusBadge(student.percentage)]">
                    {{ getStatusLabel(student.percentage) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { smartSearch } from '@/utils'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { SearchFilter, AlertMessage, StatCard, LoadingSpinner } from '@/components/shared/common'
import { useAttendanceData } from '@/composables/teacher/useAttendanceData'
import { useAlert } from '@/composables/shared'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { getAttendanceColorClass, getAttendanceStatusLabel } from '@/utils/badgeHelpers'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const { alert, showAlert } = useAlert()
const { removeDuplicates, calculateStats } = useAttendanceData()

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Attendance', href: TEACHER_ROUTES.MARK_ATTENDANCE.path },
  { name: 'Reports' }
]

const actions = [
  { label: 'Mark Attendance', icon: 'bi bi-calendar-check', variant: 'btn-teacher-outline', onClick: () => router.push(TEACHER_ROUTES.MARK_ATTENDANCE.path) }
]

const loading = ref(false)
const searchQuery = ref('')
const filters = ref({ class: '', month: '' })
const classes = ref([])
const students = ref([])
const attendanceRecords = ref([])

const filteredStudents = computed(() => {
  // Note: Highly complex filtering involving nested arrays, mapping transformations, and secondary calculations.
  // useFilterLogic omitted to preserve core stat recalculations. smartSearch used cleanly.
  let result = students.value

  if (searchQuery.value) {
    result = result.filter(s => smartSearch(s, searchQuery.value, ['name', 'roll_no']))
  }

  if (filters.value.class) {
    result = result.filter(s => {
      const hasClass = s.class_ids && s.class_ids.includes(filters.value.class)
      return hasClass
    })
  }

  // Recalculate stats based on filters
  return result.map(student => {
    let filteredAttendance = student.attendance_records || []

    // Filter by selected class/subject for STATS calculation only
    if (filters.value.class) {
      const selectedClass = classes.value.find(c => c.id === filters.value.class)
      if (selectedClass && selectedClass.subject_id) {
        filteredAttendance = filteredAttendance.filter(a => a.subject === selectedClass.subject_id)
      }
    }

    // Filter by month
    if (filters.value.month) {
      filteredAttendance = filteredAttendance.filter(a => a.session_date && a.session_date.startsWith(filters.value.month))
    }

    // Recalculate stats with filtered data
    const stats = filteredAttendance.length > 0 ? calculateStats(filteredAttendance) : {
      presentCount: 0,
      lateCount: 0,
      absentCount: 0,
      excusedCount: 0,
      totalClasses: 0,
      percentage: 0
    }

    return {
      ...student,
      present: stats.presentCount - stats.lateCount,
      late: stats.lateCount,
      absent: stats.absentCount,
      leave: stats.excusedCount,
      total: stats.totalClasses,
      percentage: stats.percentage
    }
  })
})

const totalStudents = computed(() => filteredStudents.value.length)
const totalClasses = computed(() => {
  if (attendanceRecords.value.length === 0) return 0
  // Count unique session dates
  const uniqueDates = new Set(attendanceRecords.value.map(r => r.session_date))
  return uniqueDates.size
})
const overallAttendance = computed(() => {
  if (filteredStudents.value.length === 0) return 0
  const avg = filteredStudents.value.reduce((sum, s) => sum + s.percentage, 0) / filteredStudents.value.length
  return Math.round(avg)
})
const lowAttendanceCount = computed(() => filteredStudents.value.filter(s => s.percentage < 75).length)

const statsCards = computed(() => [
  {
    title: 'Overall Attendance',
    value: `${overallAttendance.value}%`,
    icon: 'bi bi-check-circle',
    bgColor: 'bg-success-light',
    iconColor: 'text-success'
  },
  {
    title: 'Total Students',
    value: totalStudents.value,
    icon: 'bi bi-people',
    bgColor: 'bg-admin-light',
    iconColor: 'text-teacher'
  },
  {
    title: 'Low Attendance',
    value: lowAttendanceCount.value,
    icon: 'bi bi-exclamation-triangle',
    bgColor: 'bg-danger-light',
    iconColor: 'text-danger'
  },
  {
    title: 'Classes Held',
    value: totalClasses.value,
    icon: 'bi bi-calendar-event',
    bgColor: 'bg-warning-light',
    iconColor: 'text-warning'
  }
])

const getAttendanceColor = (percentage) => getAttendanceColorClass(percentage)

const getStatusBadge = (percentage) => {
  if (percentage >= 85) return 'bg-success'
  if (percentage >= 75) return 'bg-warning text-dark'
  return 'bg-danger'
}

const getStatusLabel = (percentage) => getAttendanceStatusLabel(percentage)

const loadAttendanceReport = async () => {
  loading.value = true
  try {
    const classResponse = await teacherPanelService.getMyClasses()
    const classList = classResponse.results || classResponse || []
    classes.value = classList.map(cls => ({
      id: cls.id,
      subject_id: cls.subject_id,
      name: `${cls.subject_name} - ${cls.subject_code}`
    }))

    const allStudentsData = await teacherPanelService.getAllStudentsFromClasses()
    const studentMap = new Map()

    allStudentsData.forEach(student => {
      const classId = student.class?.id || student.class_id
      const subjectId = student.class?.subject_id || student.subject_id

      if (!studentMap.has(student.id)) {
        studentMap.set(student.id, {
          ...student,
          class_ids: [classId],
          subject_ids: [subjectId]
        })
      } else {
        const existing = studentMap.get(student.id)
        if (classId && !existing.class_ids.includes(classId)) {
          existing.class_ids.push(classId)
        }
        if (subjectId && !existing.subject_ids.includes(subjectId)) {
          existing.subject_ids.push(subjectId)
        }
      }
    })

    const allAttendance = await teacherPanelService.getAllAttendance()
    attendanceRecords.value = allAttendance

    const studentsWithStats = Array.from(studentMap.values()).map(student => {
      let studentAttendance = allAttendance.filter(a => a.student === student.id)
      studentAttendance = removeDuplicates(studentAttendance)

      // Calculate stats for ALL attendance (unfiltered)
      const stats = calculateStats(studentAttendance)
      const sortedByDate = [...studentAttendance].sort((a, b) => new Date(b.session_date) - new Date(a.session_date))

      return {
        id: student.id,
        name: student.name,
        roll_no: student.roll_no,
        class_ids: student.class_ids,
        subject_ids: student.subject_ids,
        attendance_records: studentAttendance, // Keep all records for filtering
        present: stats.presentCount - stats.lateCount,
        late: stats.lateCount,
        absent: stats.absentCount,
        leave: stats.excusedCount,
        total: stats.totalClasses,
        percentage: stats.percentage,
        lastAttended: sortedByDate.length > 0 ? sortedByDate[0].session_date : '-'
      }
    })

    students.value = studentsWithStats.sort((a, b) => a.name.localeCompare(b.name))
  } catch (error) {
    console.error('Error loading report:', error)
    students.value = []
    classes.value = []
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = { class: '', month: '' }
}

const exportReport = () => showAlert('info', 'Exporting attendance report to CSV...', 'Info')

onMounted(loadAttendanceReport)

</script>
