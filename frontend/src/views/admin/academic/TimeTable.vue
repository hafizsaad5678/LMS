<template>
  <AdminPageTemplate title="Class Timetable" subtitle="Manage class schedules and timetables" icon="bi bi-calendar-week" :breadcrumbs="breadcrumbs" :actions="actions">
    <div class="admin-tt-view">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Delete Schedule"
      :message="scheduleToDelete ? `Delete this class?\n\n${scheduleToDelete.subject_name}\n${scheduleToDelete.teacher_name}\n${scheduleToDelete.room}` : 'Delete this schedule?'"
      type="danger"
      theme="admin"
      confirm-text="Delete"
      @confirm="confirmDeleteSchedule"
    />
    
    <!-- Filter Section -->
    <div class="card border-0 shadow-sm mb-3 admin-tt-filter">
      <div class="card-body">
        <div class="row g-2 align-items-end">
          <div class="col-lg-3 col-md-6">
            <label class="form-label fw-semibold mb-1 small">Filter by Program</label>
            <select v-model="filterProgram" class="form-select form-select-sm" @change="onFilterProgramChange">
              <option value="">All Programs</option>
              <option v-for="program in programs" :key="program.id" :value="program.id">{{ program.name }}</option>
            </select>
          </div>
          <div class="col-lg-3 col-md-6">
            <label class="form-label fw-semibold mb-1 small">Filter by Semester</label>
            <select v-model="filterSemester" class="form-select form-select-sm" @change="loadSchedule" :disabled="!filterProgram">
              <option value="">All Semesters</option>
              <option v-for="semester in filteredSemesters" :key="semester.id" :value="semester.id">
                {{ formatSemesterLabel(semester) }}
              </option>
            </select>
          </div>
          <div class="col-lg-3 col-md-6">
            <label class="form-label fw-semibold mb-1 small">Filter by Teacher</label>
            <select v-model="filterTeacher" class="form-select form-select-sm" @change="loadSchedule">
              <option value="">All Teachers</option>
              <option v-for="teacher in teachers" :key="teacher.id" :value="String(teacher.id)">
                {{ teacher.full_name }}
              </option>
            </select>
          </div>
          <div class="col-lg-3 col-md-6">
            <button @click="addSchedule()" class="btn btn-admin-primary btn-sm w-100">
              <i class="bi bi-plus-circle me-2"></i>Add Class
            </button>
          </div>
        </div>
        <div class="small text-muted mt-2 mb-0">
          <i class="bi bi-info-circle me-1"></i>
          Flexible calendar mode: each day can have its own class timings.
        </div>
      </div>
    </div>

    <!-- Weekly Timetable -->
    <div class="card border-0 shadow-sm admin-tt-board">
      <div class="card-header bg-white border-bottom py-2">
        <h6 class="card-title mb-0 fw-semibold"><i class="bi bi-calendar-week me-2 text-admin"></i>Weekly Schedule (Flexible Time Ranges)</h6>
      </div>
      <div v-if="loading" class="card-body py-5 text-center">
        <div class="spinner-border text-admin" role="status"></div>
        <div class="small text-muted mt-2">Loading timetable...</div>
      </div>
      <div v-else class="card-body p-2 p-md-3">
        <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-2">
          <div class="btn-group btn-group-sm" role="group" aria-label="Week navigation">
            <button class="btn btn-outline-secondary" @click="shiftWeek(-1)"><i class="bi bi-chevron-left"></i></button>
            <button class="btn btn-outline-secondary" @click="jumpToCurrentWeek">This Week</button>
            <button class="btn btn-outline-secondary" @click="shiftWeek(1)"><i class="bi bi-chevron-right"></i></button>
          </div>
          <span class="badge text-bg-light border admin-tt-week-label">{{ weekRangeLabel }}</span>
        </div>

        <div class="admin-tt-calendar-grid" role="grid" aria-label="Weekly timetable grid">
          <div class="admin-tt-grid-time-header text-uppercase">Time</div>
          <div
            v-for="(day, index) in DAYS_OF_WEEK"
            :key="`header-${day}`"
            class="admin-tt-grid-day-header"
            :class="isTodayColumn(index) ? 'admin-tt-today' : ''"
          >
            <div class="fw-semibold small">{{ DAY_LABELS[index] }}</div>
            <div class="text-muted admin-tt-day-date">{{ formatDayDate(index) }}</div>
          </div>

          <template v-for="hour in hourSlots" :key="`row-${hour}`">
            <div class="admin-tt-grid-time-cell">
              <span>{{ formatTime(`${String(hour).padStart(2, '0')}:00`) }}</span>
              <button
                class="btn btn-link text-decoration-none p-0 admin-tt-time-add"
                @click="addSchedule('', hour)"
                title="Add class at this time"
              >
                <i class="bi bi-plus-circle"></i>
              </button>
            </div>

            <div
              v-for="day in DAYS_OF_WEEK"
              :key="`${day}-${hour}`"
              class="admin-tt-grid-slot"
              :class="dragHoverSlot === getSlotKey(day, hour) ? 'admin-tt-drop-target' : ''"
              @dragover.prevent
              @dragenter.prevent="onSlotDragEnter(day, hour)"
              @dragleave="onSlotDragLeave(day, hour)"
              @drop.prevent="onSlotDrop(day, hour)"
            >
              <template v-if="getSlotActiveItems(day, hour).length">
                <div
                  class="admin-tt-class-card admin-tt-summary-block border rounded-2 p-1"
                  :class="getSlotActiveItems(day, hour).some(item => item.hasOverlap) ? 'border-warning-subtle' : 'border-danger-subtle'"
                >
                  <div class="fw-semibold admin-tt-subject">{{ getSlotSummaryLabel(getSlotActiveItems(day, hour).length) }}</div>
                  <div class="admin-tt-time">{{ getSlotTimeRangeLabel(day, hour) }}</div>
                  <div class="admin-tt-meta">Hover to view details</div>

                  <div class="admin-tt-hover-detail border rounded-2 p-1" :class="getSlotActiveItems(day, hour).some(item => item.hasOverlap) ? 'border-warning-subtle' : 'border-danger-subtle'">
                    <div
                      v-for="item in getSlotActiveItems(day, hour)"
                      :key="`hover-${item.id}-${hour}`"
                      class="admin-tt-hover-item"
                      draggable="true"
                      @dragstart="onClassDragStart(item)"
                      @dragend="onClassDragEnd"
                    >
                      <div class="d-flex justify-content-between align-items-start gap-1">
                        <span class="fw-semibold admin-tt-subject">{{ item.subject_name || 'Lecture' }}</span>
                        <div class="btn-group btn-group-sm">
                          <button @click="editSchedule(item)" class="btn btn-outline-primary admin-tt-icon-btn" title="Edit"><i class="bi bi-pencil"></i></button>
                          <button @click="deleteSchedule(item)" class="btn btn-outline-danger admin-tt-icon-btn" title="Delete"><i class="bi bi-trash"></i></button>
                        </div>
                      </div>
                      <div class="admin-tt-time">{{ formatTimeRange(item.start_time, item.end_time) }}</div>
                      <div class="admin-tt-meta">{{ item.teacher_name || '-' }}</div>
                      <div class="admin-tt-meta"><i class="bi bi-geo-alt me-1"></i>{{ item.room || '-' }}</div>
                    </div>
                  </div>
                </div>
              </template>
              <button
                v-else-if="!isSlotCovered(day, hour)"
                class="btn btn-link text-muted text-decoration-none p-0 admin-tt-empty-slot"
                @click="addSchedule(day, hour)"
              >
                <i class="bi bi-plus-circle me-1"></i>Add
              </button>
            </div>
          </template>
        </div>
      </div>
      <div class="card-footer bg-white border-top py-2">
        <div class="d-flex justify-content-between align-items-center">
          <div class="text-muted small me-2">
            Showing {{ schedule.length }} schedule(s)
            <span v-if="filterProgram || filterSemester || filterTeacher" class="badge bg-info ms-2">Filtered</span>
            <span v-if="filterTeacher" class="badge bg-secondary ms-2">Teacher: {{ selectedTeacherName }}</span>
            <span v-if="filterTeacher" class="badge bg-light text-dark border ms-2">Lectures: {{ teacherLectureCount }}</span>
          </div>
          <div class="d-flex gap-2 flex-shrink-0">
            <button @click="loadSchedule" class="btn btn-sm btn-outline-secondary"><i class="bi bi-arrow-clockwise me-1"></i>Refresh</button>
            <button @click="showAddMultipleModal = true" class="btn btn-sm btn-admin-primary"><i class="bi bi-plus-circle me-1"></i>Add Multiple</button>
          </div>
        </div>
      </div>
    </div>
    </div>
  </AdminPageTemplate>

  <!-- Modals -->
  <Teleport to="body">
    <ScheduleModal
      :show="showModal"
      :form="scheduleForm"
      :is-edit="!!editingSchedule"
      :saving="saving"
      :subjects="subjects"
      :teachers="teachers"
      :unavailable-teacher-ids="unavailableTeacherIds"
      :unavailable-teacher-conflicts="unavailableTeacherConflicts"
      :programs="programs"
      :semesters="programSemesters"
      @close="closeModal"
      @save="saveSchedule"
      @time-change="onStartTimeChange"
      @program-change="onProgramChange"
    />
    <BulkScheduleModal
      :show="showAddMultipleModal"
      :forms="multipleScheduleForms"
      :saving="saving"
      :subjects="subjects"
      :teachers="teachers"
      :programs="programs"
      @close="closeMultipleModal"
      @save="saveMultipleSchedules"
      @add="addScheduleForm"
      @remove="removeScheduleForm"
      @program-change="onMultipleProgramChange"
    />
  </Teleport>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAlert } from '@/composables/shared'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { ScheduleModal, BulkScheduleModal } from '@/components/shared/timetable'
import { timetableService } from '@/services/admin/managementService'
import { subjectService, teacherService, programService, cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { DAYS_OF_WEEK, DAY_LABELS } from '@/utils/constants/config'

const breadcrumbs = [{ name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path }, { name: 'Timetable' }]
const actions = [{ label: 'Print', icon: 'bi bi-printer', variant: 'btn-admin-outline', onClick: () => window.print() }]

const { alert, showSuccess, showError } = useAlert()
const loading = ref(false)
const saving = ref(false)
const schedule = ref([])
const subjects = ref([])
const teachers = ref([])
const programs = ref([])
const programSemesters = ref([])
const filteredSemesters = ref([])
const filterProgram = ref('')
const filterSemester = ref('')
const filterTeacher = ref('')
const showModal = ref(false)
const showAddMultipleModal = ref(false)
const editingSchedule = ref(null)
const draggingScheduleId = ref('')
const dragHoverSlot = ref('')
const showConfirmDialog = ref(false)
const scheduleToDelete = ref(null)
const currentWeekStart = ref(getMonday(new Date()))
const scheduleForm = ref({ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true })
const multipleScheduleForms = ref([{ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true, availableSemesters: [] }])

const isSemesterActive = (semester) => {
  if (!semester || typeof semester !== 'object') return false
  if (typeof semester.is_active === 'boolean') return semester.is_active
  const statusValue = String(semester.status || '').trim().toLowerCase()
  if (statusValue) return statusValue === 'active'
  return true
}

const formatSemesterLabel = (semester) => {
  if (!semester) return 'Semester'
  const number = semester.number != null ? `Semester ${semester.number}` : 'Semester'
  const name = String(semester.name || '').trim()
  if (!name) return number

  const normalizedName = name.toLowerCase()
  if (normalizedName.startsWith(number.toLowerCase())) {
    return name
  }
  return `${number} - ${name}`
}

const timeToMinutes = (timeValue) => {
  const raw = String(timeValue || '').trim()
  if (!raw) return 0
  const [h, m] = raw.split(':').map(Number)
  if (!Number.isFinite(h) || !Number.isFinite(m)) return 0
  return h * 60 + m
}

const minutesToTime = (minutesValue) => {
  const clamped = Math.max(0, Math.min(1439, Number(minutesValue) || 0))
  const h = Math.floor(clamped / 60)
  const m = clamped % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

function getMonday(date) {
  const base = new Date(date)
  const day = base.getDay()
  const diff = day === 0 ? -6 : 1 - day
  base.setHours(0, 0, 0, 0)
  base.setDate(base.getDate() + diff)
  return base
}

const hourSlots = computed(() => {
  const hours = []
  for (let hour = 7; hour <= 18; hour += 1) {
    hours.push(hour)
  }
  return hours
})

const weekRangeLabel = computed(() => {
  const start = new Date(currentWeekStart.value)
  const end = new Date(start)
  end.setDate(start.getDate() + 5)
  const fmt = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' })
  return `${fmt.format(start)} - ${fmt.format(end)}`
})

const getDateForDayIndex = (index) => {
  const d = new Date(currentWeekStart.value)
  d.setDate(d.getDate() + index)
  return d
}

const formatDayDate = (index) => {
  const d = getDateForDayIndex(index)
  return new Intl.DateTimeFormat('en-US', { day: '2-digit', month: 'short' }).format(d)
}

const isTodayColumn = (index) => {
  const today = new Date()
  const d = getDateForDayIndex(index)
  return d.getDate() === today.getDate() && d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear()
}

const shiftWeek = (delta) => {
  const next = new Date(currentWeekStart.value)
  next.setDate(next.getDate() + (delta * 7))
  currentWeekStart.value = getMonday(next)
}

const jumpToCurrentWeek = () => {
  currentWeekStart.value = getMonday(new Date())
}

const formatTime = (timeValue) => {
  const raw = String(timeValue || '').slice(0, 5)
  if (!raw) return '--:--'
  const [h, m] = raw.split(':').map(Number)
  if (!Number.isFinite(h) || !Number.isFinite(m)) return raw
  const suffix = h >= 12 ? 'PM' : 'AM'
  const hour12 = h % 12 || 12
  return `${String(hour12).padStart(2, '0')}:${String(m).padStart(2, '0')} ${suffix}`
}

const formatTimeRange = (start, end) => `${formatTime(start)} - ${formatTime(end)}`

const hasOverlap = (current, list) => {
  const currentStart = timeToMinutes(current.start_time)
  const currentEnd = timeToMinutes(current.end_time)
  if (currentEnd <= currentStart) return false

  return list.some(item => {
    if (item.id === current.id) return false
    const start = timeToMinutes(item.start_time)
    const end = timeToMinutes(item.end_time)
    if (end <= start) return false
    return currentStart < end && start < currentEnd
  })
}

const scheduleWithOverlap = computed(() => {
  const out = {}
  for (const day of DAYS_OF_WEEK) {
    const dayList = schedule.value
      .filter(item => String(item.day || '').toLowerCase() === day)
      .slice()
      .sort((a, b) => timeToMinutes(a.start_time) - timeToMinutes(b.start_time))

    out[day] = dayList.map(item => ({
      ...item,
      hasOverlap: hasOverlap(item, dayList),
    }))
  }
  return out
})

const daySchedules = computed(() => scheduleWithOverlap.value)

const selectedTeacherName = computed(() => {
  if (!filterTeacher.value) return 'All'
  const teacher = teachers.value.find(item => String(item.id) === String(filterTeacher.value))
  return teacher?.full_name || 'Selected Teacher'
})

const teacherLectureCount = computed(() => {
  if (!filterTeacher.value) return schedule.value.length
  return schedule.value.filter(item => {
    const itemTeacher = item.teacher ?? item.teacher_id
    return String(itemTeacher) === String(filterTeacher.value)
  }).length
})

const getSlotKey = (day, hour) => `${String(day || '').toLowerCase()}-${hour}`

const getHourStartMinute = (hour) => hour * 60

const getHourEndMinute = (hour) => (hour + 1) * 60

const getSlotActiveItems = (day, hour) => {
  const normalized = String(day || '').toLowerCase()
  const startMin = getHourStartMinute(hour)
  const endMin = getHourEndMinute(hour)
  return (daySchedules.value[normalized] || []).filter(item => {
    const itemStart = timeToMinutes(item.start_time)
    const itemEnd = timeToMinutes(item.end_time)
    return itemStart < endMin && startMin < itemEnd
  })
}

const getSlotSummaryLabel = (count) => {
  const safeCount = Number(count) || 0
  if (safeCount <= 1) return '1 Lecture'
  return `${safeCount} Lectures`
}

const getSlotTimeRangeLabel = (day, hour) => {
  const items = getSlotActiveItems(day, hour)
  if (!items.length) return ''

  const starts = items.map(item => timeToMinutes(item.start_time)).filter(Number.isFinite)
  const ends = items.map(item => timeToMinutes(item.end_time)).filter(Number.isFinite)
  if (!starts.length || !ends.length) return ''

  const minStart = Math.min(...starts)
  const maxEnd = Math.max(...ends)
  return `${formatTime(minutesToTime(minStart))} - ${formatTime(minutesToTime(maxEnd))}`
}

const isSlotCovered = (day, hour) => {
  return getSlotActiveItems(day, hour).length > 0
}

const rangesOverlap = (startA, endA, startB, endB) => startA < endB && startB < endA

const unavailableTeacherConflicts = computed(() => {
  const day = String(scheduleForm.value.day || '').toLowerCase()
  const start = timeToMinutes(scheduleForm.value.start_time)
  const end = timeToMinutes(scheduleForm.value.end_time)
  if (!day || !start || !end || end <= start) return {}

  const editingId = String(editingSchedule.value?.id || '')
  const unavailable = {}

  for (const item of schedule.value) {
    if (String(item.day || '').toLowerCase() !== day) continue
    if (editingId && String(item.id) === editingId) continue

    const itemStart = timeToMinutes(item.start_time)
    const itemEnd = timeToMinutes(item.end_time)
    if (!itemStart || !itemEnd || itemEnd <= itemStart) continue
    if (!rangesOverlap(start, end, itemStart, itemEnd)) continue

    const teacherId = item.teacher ?? item.teacher_id
    if (teacherId !== undefined && teacherId !== null && String(teacherId) !== '') {
      const teacherKey = String(teacherId)
      if (!unavailable[teacherKey]) unavailable[teacherKey] = []
      unavailable[teacherKey].push(`${formatTimeRange(item.start_time, item.end_time)}`)
    }
  }

  return unavailable
})

const unavailableTeacherIds = computed(() => Object.keys(unavailableTeacherConflicts.value))

const calculateEndTime = (start, duration) => {
  const [hours, minutes] = start.split(':').map(Number)
  const total = hours * 60 + minutes + duration
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
}

const onStartTimeChange = () => {
  if (scheduleForm.value.start_time && !scheduleForm.value.end_time) {
    scheduleForm.value.end_time = calculateEndTime(scheduleForm.value.start_time, 50)
  }
}

const buildSchedulePayload = (item, overrides = {}) => {
  return {
    day: String(overrides.day ?? item.day ?? '').toLowerCase(),
    start_time: overrides.start_time ?? item.start_time,
    end_time: overrides.end_time ?? item.end_time,
    subject: overrides.subject ?? item.subject,
    teacher: overrides.teacher ?? item.teacher,
    room: overrides.room ?? item.room,
    program: overrides.program ?? (item.program || null),
    semester: overrides.semester ?? (item.semester || null),
    is_active: overrides.is_active ?? (item.is_active !== false),
  }
}

const onClassDragStart = (item) => {
  draggingScheduleId.value = String(item?.id || '')
}

const onClassDragEnd = () => {
  draggingScheduleId.value = ''
  dragHoverSlot.value = ''
}

const onSlotDragEnter = (day, hour) => {
  if (!draggingScheduleId.value) return
  dragHoverSlot.value = getSlotKey(day, hour)
}

const onSlotDragLeave = (day, hour) => {
  if (dragHoverSlot.value === getSlotKey(day, hour)) {
    dragHoverSlot.value = ''
  }
}

const onSlotDrop = async (targetDay, targetHour) => {
  if (!draggingScheduleId.value) return

  const moved = schedule.value.find(item => String(item.id) === draggingScheduleId.value)
  onClassDragEnd()
  if (!moved) return

  const normalizedTarget = String(targetDay || '').toLowerCase()
  if (!normalizedTarget) return

  const originalStart = timeToMinutes(moved.start_time)
  const originalEnd = timeToMinutes(moved.end_time)
  const duration = Math.max(1, originalEnd - originalStart)
  const originalMinute = originalStart % 60
  const nextStartMinute = (Number(targetHour) * 60) + originalMinute
  let nextEndMinute = nextStartMinute + duration
  if (nextEndMinute > 1439) {
    nextEndMinute = 1439
  }

  const sameDay = String(moved.day || '').toLowerCase() === normalizedTarget
  const sameStart = nextStartMinute === originalStart
  if (sameDay && sameStart) return

  try {
    await timetableService.create(buildSchedulePayload(moved, {
      day: normalizedTarget,
      start_time: `${minutesToTime(nextStartMinute)}:00`,
      end_time: `${minutesToTime(nextEndMinute)}:00`,
    }))
    invalidateTimetableCaches()
    showSuccess(`Copied ${moved.subject_name || 'class'} to ${normalizedTarget.charAt(0).toUpperCase() + normalizedTarget.slice(1)}`)
    await loadSchedule()
  } catch (error) {
    let msg = 'Unable to copy class. Please check for time conflicts.'
    const d = error?.response?.data
    if (d) {
      if (typeof d === 'string') msg = d
      else if (d.error) msg = d.error
      else if (d.detail) msg = d.detail
      else if (typeof d === 'object') {
        msg = Object.entries(d).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('; ')
      }
    }
    showError(msg)
  }
}
const addSchedule = (day = '', hour = 8) => {
  const normalizedHour = Number.isFinite(Number(hour)) ? Number(hour) : 8
  const start = `${String(Math.max(0, Math.min(23, normalizedHour))).padStart(2, '0')}:00`
  const end = calculateEndTime(start, 50)

  editingSchedule.value = null
  scheduleForm.value = {
    day: String(day || '').toLowerCase(),
    start_time: start + ':00',
    end_time: end + ':00',
    subject: '',
    teacher: '',
    room: '',
    program: '',
    semester: '',
    is_active: true
  }

  showModal.value = true
}

const editSchedule = (item) => {
  editingSchedule.value = item
  scheduleForm.value = { ...item, program: item.program || '', semester: item.semester || '', is_active: item.is_active !== false }
  if (item.program) loadSemestersByProgram(item.program, 'form')
  showModal.value = true
}

const deleteSchedule = (item) => { scheduleToDelete.value = item; showConfirmDialog.value = true }

const confirmDeleteSchedule = async () => {
  try {
    await timetableService.delete(scheduleToDelete.value.id)
    invalidateTimetableCaches()
    showSuccess('Schedule deleted')
    loadSchedule()
  } catch (error) {
    showError(error.response?.data?.error || 'Failed to delete')
  } finally { showConfirmDialog.value = false; scheduleToDelete.value = null }
}

const loadSchedule = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterProgram.value) params.program = filterProgram.value
    if (filterSemester.value) params.semester = filterSemester.value
    if (filterTeacher.value) params.teacher = filterTeacher.value
    const response = await timetableService.getAll(params)
    schedule.value = response.data.results || response.data
  } catch (error) {
    showError('Failed to load timetable')
  } finally { loading.value = false }
}

const onFilterProgramChange = async () => {
  filterSemester.value = ''
  if (filterProgram.value) await loadSemestersByProgram(filterProgram.value, 'filter')
  else filteredSemesters.value = []
  loadSchedule()
}

const loadSemestersByProgram = async (programId, target = 'form') => {
  try {
    const response = await programService.getProgramSemesters(programId)
    const list = (response.results || response).filter(isSemesterActive)
    if (target === 'form') programSemesters.value = list
    else filteredSemesters.value = list
  } catch (error) { console.error('Error loading semesters:', error) }
}

const onProgramChange = async () => {
  scheduleForm.value.semester = ''
  scheduleForm.value.subject = ''
  if (scheduleForm.value.program) await loadSemestersByProgram(scheduleForm.value.program, 'form')
  else programSemesters.value = []
}

const onMultipleProgramChange = async (index) => {
  const form = multipleScheduleForms.value[index]
  form.semester = ''
  form.subject = ''
  if (form.program) {
    try {
      const response = await programService.getProgramSemesters(form.program)
      form.availableSemesters = (response.results || response).filter(isSemesterActive)
    } catch (error) { form.availableSemesters = [] }
  } else form.availableSemesters = []
}

const loadDropdowns = async () => {
  const loadCached = async (key, service, setter) => {
    const cached = cacheService.get(key)
    if (cached) { setter(cached); return }
    try {
      const response = await service()
      const result = response.results || response
      cacheService.set(key, result)
      setter(result)
    } catch (e) { console.error(`Error loading ${key}:`, e) }
  }
  await Promise.all([
    loadCached('subjects_list', subjectService.getAllSubjects, v => subjects.value = v),
    loadCached('teachers_list', teacherService.getAllTeachers, v => teachers.value = v),
    loadCached('programs_list', programService.getAllPrograms, v => programs.value = v)
  ])
}

const invalidateTimetableCaches = () => {
  cacheService.clear('student_schedule_v2')
  cacheService.clearPattern('student:')
}

const saveSchedule = async () => {
  saving.value = true
  try {
    const selectedTeacherId = String(scheduleForm.value.teacher || '')
    if (selectedTeacherId && unavailableTeacherIds.value.includes(selectedTeacherId)) {
      const conflicts = unavailableTeacherConflicts.value[selectedTeacherId] || []
      const conflictDetails = conflicts.length ? ` Busy at: ${conflicts.join(', ')}.` : ''
      showError(`Selected teacher is unavailable for the chosen day/time.${conflictDetails} Please choose another teacher or time slot.`)
      return
    }

    if (editingSchedule.value) await timetableService.update(editingSchedule.value.id, scheduleForm.value)
    else await timetableService.create(scheduleForm.value)
    invalidateTimetableCaches()
    showSuccess(editingSchedule.value ? 'Schedule updated' : 'Schedule added')
    closeModal()
    loadSchedule()
  } catch (error) {
    let msg = 'Failed to save'
    if (error.response?.data) {
      const d = error.response.data
      if (Array.isArray(d)) msg = d.join(', ')
      else if (d.error) msg = d.error
      else if (d.detail) msg = d.detail
      else if (typeof d === 'object') msg = Object.entries(d).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('; ')
    }
    showError(msg)
  } finally { saving.value = false }
}

const closeModal = () => {
  showModal.value = false
  editingSchedule.value = null
  scheduleForm.value = { day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true }
  programSemesters.value = []
}

const addScheduleForm = () => multipleScheduleForms.value.push({ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true, availableSemesters: [] })
const removeScheduleForm = (index) => multipleScheduleForms.value.splice(index, 1)
const closeMultipleModal = () => { showAddMultipleModal.value = false; multipleScheduleForms.value = [{ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true, availableSemesters: [] }] }

const saveMultipleSchedules = async () => {
  saving.value = true
  try {
    await Promise.all(multipleScheduleForms.value.map(({ availableSemesters, ...data }) => timetableService.create(data)))
    invalidateTimetableCaches()
    showSuccess(`${multipleScheduleForms.value.length} schedules added`)
    closeMultipleModal()
    loadSchedule()
  } catch (error) {
    showError(error.response?.data?.error || 'Failed to save')
  } finally { saving.value = false }
}

onMounted(() => { loadSchedule(); loadDropdowns() })
</script>


