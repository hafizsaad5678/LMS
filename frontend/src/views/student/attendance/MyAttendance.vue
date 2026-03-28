<template>
  <StudentPageTemplate
    title="My Attendance"
    subtitle="Track your class attendance and participation"
    icon="bi bi-calendar-check"
    :breadcrumbs="breadcrumbs"
  >
    <!-- ── STAT CARDS (same as dashboard) ── -->
    <template #stats>
      <div class="row g-4">
        <div class="col-xl-3 col-md-6" v-for="card in statCards" :key="card.title">
          <StatCard v-bind="card" />
        </div>
      </div>
    </template>

    <template #filters>
      <div class="row g-3 align-items-end">
        <div class="col-md-5 col-12">
          <SelectInput
            v-model="filters.status"
            :options="ATTENDANCE_STATUS_OPTIONS"
            placeholder="All Status"
            :no-margin="true"
            @change="handleFilterChange"
          />
        </div>
        <div class="col-md-5 col-12">
          <SelectInput
            v-model="filters.subject"
            :options="subjectOptions"
            placeholder="All Subjects"
            :no-margin="true"
            @change="handleFilterChange"
          />
        </div>
        <div class="col-md-2 col-12">
          <button
            @click="resetFilters"
            class="btn btn-student w-100 rounded-3 py-2 fw-bold shadow-sm"
            type="button"
          >
            <i class="bi bi-x-circle me-1"></i>
            <span>Reset</span>
          </button>
        </div>
      </div>
    </template>

    <!-- ── LOADING / EMPTY ── -->
    <div v-if="loading" class="text-center py-5">
      <LoadingSpinner color="student" message="Loading attendance records..." />
    </div>

    <AlertMessage v-else-if="error" type="error" :message="error" title="Error" />

    <EmptyState
      v-else-if="filteredRecords.length === 0"
      title="No Attendance Records"
      :message="hasActiveFilters ? 'Try adjusting your filters' : 'No attendance records available yet'"
    />

    <!-- ── WEEK VIEW (single week with navigation) ── -->
    <div v-else>
      <div v-if="currentWeekGroup" class="mb-5">
        <div class="row g-3 align-items-start mb-3">
          <div class="col-md-4 col-12">
            <span class="week-pill px-3 py-1 bg-student-light text-student rounded-pill fw-bold small border d-inline-block">
              <i class="bi bi-calendar-week me-1"></i>{{ currentWeekGroup.weekLabel }}
            </span>
            <div class="text-muted smaller mt-2">
              <strong>{{ currentWeekGroup.records.length }}</strong> class{{ currentWeekGroup.records.length > 1 ? 'es' : '' }}
            </div>
          </div>

          <div class="col-md-4 col-12 text-center">
            <div class="month-pill px-4 py-2 bg-dark text-white rounded-pill fw-black shadow-sm small d-inline-block">
              <i class="bi bi-calendar3 me-2 opacity-75"></i>{{ currentWeekGroup.monthName }}
            </div>
          </div>

          <div class="col-md-4 col-12 d-flex justify-content-md-end">
            <div class="d-flex gap-2">
            <button
              class="btn btn-outline-secondary rounded-3 px-3 fw-bold shadow-sm"
              type="button"
              :disabled="!canGoPrevWeek"
              @click="goPrevWeek"
            >
              <i class="bi bi-chevron-left me-1"></i>Prev Week
            </button>
            <button
              class="btn btn-student rounded-3 px-3 fw-bold shadow-sm"
              type="button"
              :disabled="!canGoNextWeek"
              @click="goNextWeek"
            >
              Next Week<i class="bi bi-chevron-right ms-1"></i>
            </button>
          </div>
          </div>
        </div>

        <div class="flex-grow-1 border-top border-2 mb-4 opacity-10"></div>

        <!-- Attendance cards -->
        <div v-if="currentWeekGroup.records.length === 0" class="alert alert-light border text-muted">
          No classes found for this week.
        </div>

        <div v-else class="row g-3">
          <div
            v-for="record in currentWeekGroup.records"
            :key="record.id"
            class="col-md-6 col-lg-4"
          >
            <div class="att-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
              <!-- Card header same structure as assignment cards -->
              <div class="att-card-header p-3" :class="getAttHeaderClass(record.status)">
                <div class="d-flex justify-content-between align-items-center">
                  <div class="att-card-icon">
                    <i :class="`bi ${getAttendanceIcon(record.status)}`"></i>
                  </div>
                  <span class="badge rounded-pill text-white" :class="`bg-${getAttendanceColor(record.status)}`">
                    {{ record.status }}
                  </span>
                </div>
                <div class="mt-2">
                  <div class="fw-black text-dark fs-6 mb-0 text-truncate">
                    {{ record.subject_name || record.subject?.name }}
                  </div>
                  <small class="text-muted" :class="`text-${getAttendanceColor(record.status)}-50`">
                    {{ record.subject_code || record.subject?.code }}
                  </small>
                </div>
              </div>

              <!-- Card body -->
              <div class="card-body p-3">
                <div class="d-flex flex-column gap-2">
                  <div class="d-flex align-items-center text-muted small">
                    <i class="bi bi-calendar-event text-student me-2"></i>
                    <strong>{{ formatDateUtil(record.session_date, { weekday: 'short' }) }}</strong>
                    <span class="ms-1">{{ formatDateUtil(record.session_date, { month: 'short', day: 'numeric' }) }}</span>
                  </div>
                  <div class="d-flex align-items-center text-muted small">
                    <i class="bi bi-person-badge text-student me-2"></i>
                    <span>{{ record.marked_by_name || 'System Record' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, SelectInput, LoadingSpinner, EmptyState, StatCard } from '@/components/shared/common'
import { useEntityList } from '@/composables/shared'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { studentService } from '@/services/shared'
import studentPanelService from '@/services/student/studentPanelService'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { getAttendanceIcon } from '@/utils/badgeHelpers'
import { ATTENDANCE_STATUS_OPTIONS } from '@/utils/constants/options'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

// ── helpers ──────────────────────────────────────────────────────────────────
const getAttendanceColor = (status) => {
  return { present: 'success', absent: 'danger', late: 'warning', excused: 'info' }[status?.toLowerCase()] ?? 'secondary'
}
const getAttHeaderClass = (status) => {
  return {
    present: 'att-header-present',
    absent:  'att-header-absent',
    late:    'att-header-late',
    excused: 'att-header-excused'
  }[status?.toLowerCase()] ?? 'att-header-default'
}

// ── composables ───────────────────────────────────────────────────────────────
const { studentId, loadProfile } = useStudentBase()

const {
  loading,
  error,
  filteredData,
  filters,
  loadData
} = useEntityList({
  cacheKey: `student_attendance_${studentId?.value}`,
  defaultFilters: { subject: '', status: '', order: 'desc' },
  customFilter: (items, f) => {
    let res = items
    if (f.subject) res = res.filter(r => (r.subject_name || r.subject?.name) === f.subject)
    if (f.status && f.status !== 'all') res = res.filter(r => r.status?.toLowerCase() === f.status)
    const dir = f.order === 'asc' ? 1 : -1
    return res.sort((a, b) => dir * (new Date(a.session_date) - new Date(b.session_date)))
  }
})

// ── derived data ──────────────────────────────────────────────────────────────
const filteredRecords = computed(() => filteredData.value)
const hasActiveFilters = computed(() => {
  const activeFilters = filters.value || {}
  return activeFilters.status || activeFilters.subject
})
const selectedWeekIndex = ref(0)
const WEEK_MS = 7 * 24 * 60 * 60 * 1000

/** Get ISO week number */
const getWeekNumber = (date) => {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  const dayNum = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
}

const getWeekStart = (date) => {
  const weekStart = new Date(date)
  weekStart.setHours(0, 0, 0, 0)
  weekStart.setDate(weekStart.getDate() - ((weekStart.getDay() + 6) % 7))
  return weekStart
}

/** Group filtered records: one sortable list of weeks */
const weekGroups = computed(() => {
  const groups = {}
  let minWeekStart = null
  let maxWeekStart = null

  filteredRecords.value.forEach(r => {
    const d = new Date(r.session_date)
    const weekStart = getWeekStart(d)
    const weekStartTime = weekStart.getTime()
    const weekNum = getWeekNumber(weekStart)
    const weekKey = `${weekStart.getFullYear()}-W${weekNum}`
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 6)
    const monthName = weekStart.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    const weekLabel = `Week ${weekNum} · ${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} – ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`

    if (minWeekStart === null || weekStartTime < minWeekStart) minWeekStart = weekStartTime
    if (maxWeekStart === null || weekStartTime > maxWeekStart) maxWeekStart = weekStartTime

    if (!groups[weekKey]) {
      groups[weekKey] = {
        weekKey,
        weekLabel,
        monthName,
        weekStart: weekStartTime,
        records: []
      }
    }
    groups[weekKey].records.push(r)
  })

  if (minWeekStart === null || maxWeekStart === null) return []

  const timeline = []
  for (let current = maxWeekStart; current >= minWeekStart; current -= WEEK_MS) {
    const weekStart = new Date(current)
    const weekNum = getWeekNumber(weekStart)
    const weekKey = `${weekStart.getFullYear()}-W${weekNum}`
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 6)

    timeline.push(groups[weekKey] || {
      weekKey,
      weekLabel: `Week ${weekNum} · ${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} – ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`,
      monthName: weekStart.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
      weekStart: current,
      records: []
    })
  }

  return timeline
})

const currentWeekGroup = computed(() => weekGroups.value[selectedWeekIndex.value] || null)
const canGoPrevWeek = computed(() => selectedWeekIndex.value < weekGroups.value.length - 1)
const canGoNextWeek = computed(() => selectedWeekIndex.value > 0)

const subjectOptions = computed(() =>
  [...new Set(filteredData.value.map(r => r.subject_name || r.subject?.name).filter(Boolean))]
    .sort()
    .map(s => ({ value: s, label: s }))
)

/** Stats are always computed across ALL (unfiltered) records from useEntityList */
const allRecords = computed(() => filteredData.value)

const stats = computed(() => ({
  present: allRecords.value.filter(r => r.status === 'present').length,
  absent:  allRecords.value.filter(r => r.status === 'absent').length,
  late:    allRecords.value.filter(r => r.status === 'late').length,
  overall: studentPanelService.calculateAttendance(allRecords.value)
}))

const statCards = computed(() => [
  { title: 'Present Days',    value: stats.value.present,       icon: 'bi bi-check-circle',  type: 'student' },
  { title: 'Absent Days',     value: stats.value.absent,        icon: 'bi bi-x-circle',      type: 'teacher' },
  { title: 'Late Arrivals',   value: stats.value.late,          icon: 'bi bi-clock',         type: 'finance' },
  { title: 'Attendance Rate', value: `${stats.value.overall}%`, icon: 'bi bi-graph-up',      iconColor: 'text-success' }
])

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Attendance' }
]

// ── actions ───────────────────────────────────────────────────────────────────
const goPrevWeek = () => {
  if (canGoPrevWeek.value) selectedWeekIndex.value += 1
}

const goNextWeek = () => {
  if (canGoNextWeek.value) selectedWeekIndex.value -= 1
}

const handleFilterChange = () => {
  selectedWeekIndex.value = 0
}

const resetFilters = () => {
  filters.value = { subject: '', status: '', order: 'desc' }
  handleFilterChange()
}

watch([() => filters.value.status, () => filters.value.subject], handleFilterChange)

watch(weekGroups, (groups) => {
  if (!groups.length) {
    selectedWeekIndex.value = 0
    return
  }
  if (selectedWeekIndex.value > groups.length - 1) {
    selectedWeekIndex.value = groups.length - 1
  }
}, { immediate: true })

onMounted(async () => {
  loadProfile()
  await loadData(() => studentService.getAttendance(studentId))
})
</script>


