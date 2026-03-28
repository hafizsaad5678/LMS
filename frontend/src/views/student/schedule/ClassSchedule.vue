<template>
  <StudentPageTemplate :title="studentName ? `Class Schedule: ${studentName}` : 'Class Schedule'"
    :subtitle="studentEnrollment ? `Enrollment: ${studentEnrollment} - View your weekly class timetable` : 'View your weekly class timetable'"
    icon="bi bi-calendar3" :breadcrumbs="breadcrumbs">
    <div class="class-schedule">

      <!-- Summary Stats at Top -->
      <div v-if="weekSchedule.length > 0" class="row g-3 mb-4">
        <div class="col-md-3 col-6">
          <StatCard title="Total Classes" :value="totalClasses" icon="bi bi-book-fill" bg-color="bg-student-light"
            icon-color="text-student" />
        </div>
        <div class="col-md-3 col-6">
          <StatCard title="Total Hours" :value="totalHours" icon="bi bi-clock-fill" bg-color="bg-success-light"
            icon-color="text-success" />
        </div>
        <div class="col-md-3 col-6">
          <StatCard title="Subjects" :value="uniqueSubjects" icon="bi bi-calendar-check-fill" bg-color="bg-info-light"
            icon-color="text-info" />
        </div>
        <div class="col-md-3 col-6">
          <StatCard title="Instructors" :value="uniqueInstructors" icon="bi bi-people-fill" bg-color="bg-warning-light"
            icon-color="text-warning" />
        </div>
      </div>

      <!-- Week Navigation (Attendance Style) -->
      <div class="mb-4 px-2">
        <div class="row g-3 align-items-center">
          <div class="col-md-4 col-12">
            <span class="week-pill px-3 py-1 bg-student-light text-student rounded-pill fw-bold small border d-inline-block">
              <i class="bi bi-calendar-week me-1"></i>{{ weekRange }}
            </span>
            <div class="text-muted smaller mt-2">
              <strong>{{ weekClassCount }}</strong> classes this week
            </div>
          </div>
          <div class="col-md-4 col-12 text-center">
            <div class="month-pill px-4 py-2 bg-dark text-white rounded-pill fw-black shadow-sm small d-inline-block">
              <i class="bi bi-calendar3 me-2 opacity-75"></i>{{ currentMonthYear }}
            </div>
          </div>
          <div class="col-md-4 col-12 d-flex justify-content-md-end">
            <div class="d-flex gap-2">
              <button class="btn btn-outline-secondary rounded-3 px-3 fw-bold shadow-sm" @click="previousWeek">
                <i class="bi bi-chevron-left me-1"></i>Prev Week
              </button>
              <button class="btn btn-student rounded-3 px-3 fw-bold shadow-sm" @click="nextWeek">
                Next Week<i class="bi bi-chevron-right ms-1"></i>
              </button>
            </div>
          </div>
        </div>
        <div class="flex-grow-1 border-top border-2 mt-3 opacity-10"></div>
      </div>

      <!-- Loading State -->
      <LoadingSpinner v-if="loading" text="Loading schedule..." theme="student" class="py-5" />

      <!-- Error State -->
      <AlertMessage v-if="error" type="error" :message="error" title="Error" />

      <!-- Empty State -->
      <div v-else-if="weekSchedule.length === 0" class="text-center py-4">
        <i class="bi bi-calendar-x display-4 text-muted"></i>
        <h5 class="mt-3">No Classes Scheduled</h5>
        <p class="text-muted small">No classes scheduled for this week</p>
      </div>

      <!-- Weekly Schedule Grid -->
      <div v-else class="row g-4">
        <div v-for="day in prioritizedWeekSchedule" :key="day.date" class="col-12 col-xl-6">
          <div class="day-card card border-0 shadow-sm rounded-4 overflow-hidden" :class="isToday(day.date) ? 'border-top border-student border-4' : ''">
            <button
              type="button"
              class="card-header border-0 p-4 w-100 text-start day-toggle"
              :class="getDayHeaderClass(day)"
              @click="toggleDay(day)"
            >
              <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center">
                  <div class="day-icon-wrapper size-48 rounded-circle bg-white shadow-sm d-flex align-items-center justify-content-center me-3">
                    <i class="bi bi-calendar-day fs-4" :class="getDayIconClass(day)"></i>
                  </div>
                  <div>
                    <h5 class="mb-0 fw-bold" :class="isToday(day.date) ? 'text-student' : 'text-dark'">{{ formatDayName(day.date) }}</h5>
                    <small class="text-muted">{{ formatDate(day.date) }}</small>
                  </div>
                </div>
                <div class="d-flex align-items-center gap-2">
                  <span v-if="isToday(day.date)" class="badge bg-student text-white rounded-pill px-3 py-2">TODAY</span>
                  <span v-else-if="isSunday(day.date)" class="badge bg-warning text-dark rounded-pill px-3 py-2">HOLIDAY</span>
                  <span v-else class="badge bg-white text-muted border rounded-pill px-3 py-2 fw-bold">{{ day.classes.length }} Classes</span>
                  <i class="bi fs-6 text-muted" :class="isDayExpanded(day) ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                </div>
              </div>
            </button>

            <div v-if="isDayExpanded(day)" class="card-body p-4">
              <div v-if="isSunday(day.date)" class="py-5 text-center text-warning-emphasis bg-warning-subtle rounded-3">
                <i class="bi bi-sun display-5 mb-2"></i>
                <h6 class="fw-bold mb-1">Sunday Holiday</h6>
                <p class="small mb-0">No regular classes are scheduled on Sunday.</p>
              </div>
              <div v-else-if="day.classes.length === 0" class="py-5 text-center text-muted opacity-50">
                <i class="bi bi-journal-x display-4 mb-2"></i>
                <p class="small fw-medium">No classes scheduled</p>
              </div>
              <div v-else class="class-timeline">
                <div v-for="cls in day.classes" :key="cls.id"
                  class="class-item-v2 position-relative ps-4 pb-4 border-start border-2"
                  :class="getClassStatusBorder(cls)">
                  
                  <div class="timeline-dot position-absolute" :class="getClassStatusDot(cls)"></div>
                  
                  <div class="schedule-class-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
                    <div class="schedule-class-header p-3" :class="isCurrentClass(cls) ? 'bg-student-light' : 'bg-light'">
                      <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="schedule-class-icon rounded-3 bg-white shadow-sm d-flex align-items-center justify-content-center">
                          <i class="bi bi-journal-bookmark text-student"></i>
                        </div>
                        <span class="badge rounded-pill px-2 py-1" :class="getClassStatusBadge(cls)">
                          {{ isCurrentClass(cls) ? 'Live' : isUpcomingClass(cls) ? 'Upcoming' : 'Scheduled' }}
                        </span>
                      </div>
                      <h6 class="mb-1 fw-bold text-dark text-truncate-2">{{ cls.subject_name || cls.subject?.name }}</h6>
                      <small class="text-muted d-flex align-items-center">
                        <i class="bi bi-clock me-1 text-student"></i>
                        {{ formatScheduleTime(cls.start_time) }} - {{ formatScheduleTime(cls.end_time) }}
                      </small>
                    </div>

                    <div class="card-body p-3">
                      <div class="d-flex flex-column gap-2 mb-2">
                        <div class="d-flex align-items-center small text-muted">
                          <i class="bi bi-person-circle me-2 text-student"></i>
                          {{ cls.instructor_name || cls.teacher?.full_name || 'Instructor' }}
                        </div>
                        <div class="d-flex align-items-center small text-muted">
                          <i class="bi bi-geo-alt-fill me-2 text-info"></i>
                          {{ cls.room_number || cls.location || 'Room TBA' }}
                        </div>
                      </div>

                      <p v-if="cls.description" class="small text-muted mb-0 text-truncate-2">
                        {{ cls.description }}
                      </p>

                      <div v-if="isCurrentClass(cls)" class="mt-2 d-flex align-items-center">
                        <span class="pulse-primary me-2"></span>
                        <small class="text-student fw-bold">Live Now</small>
                      </div>
                    </div>
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
import { ref, computed, onMounted } from 'vue'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, StatCard, LoadingSpinner } from '@/components/shared/common'
import { useEntityList } from '@/composables/shared'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { useStudentId } from '@/composables/shared/domain/useStudentId'
import studentPanelService from '@/services/student/studentPanelService'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const { studentName, studentEnrollment, loadProfile } = useStudentBase()
const { getStudentId } = useStudentId()
const currentWeekStart = ref(new Date())
const expandedDayKey = ref(null)

const {
  loading,
  error,
  data: schedule,
  loadData
} = useEntityList({
  cacheKey: `student_schedule_v2`,
  searchFields: ['subject_name', 'subject.name', 'instructor_name', 'location'],
  defaultFilters: {}
})

const breadcrumbs = [{ name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path }, { name: 'Class Schedule' }]

const availableSubjects = computed(() => [...new Set(schedule.value.map(c => c.subject_name || c.subject?.name).filter(Boolean))].sort())
const availableInstructors = computed(() => [...new Set(schedule.value.map(c => c.instructor_name || c.teacher?.full_name).filter(Boolean))].sort())

const weekSchedule = computed(() => {
  const days = []; const start = new Date(currentWeekStart.value); start.setDate(start.getDate() - start.getDay())
  for (let i = 0; i < 7; i++) {
    const date = new Date(start); date.setDate(start.getDate() + i)
    const dayName = date.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
    const dayClasses = schedule.value.filter(cls => cls.day?.toLowerCase() === dayName)
    days.push({ date, classes: dayClasses.sort((a, b) => a.start_time.localeCompare(b.start_time)) })
  }
  return days
})

const totalClasses = computed(() => schedule.value.length)
const uniqueSubjects = computed(() => availableSubjects.value.length)
const uniqueInstructors = computed(() => availableInstructors.value.length)
const totalHours = computed(() => {
  let total = 0
  schedule.value.forEach(c => {
    const start = new Date(`2000-01-01T${c.start_time}`)
    const end = new Date(`2000-01-01T${c.end_time}`)
    total += (end - start) / (1000 * 60 * 60)
  })
  return total.toFixed(1)
})

const weekRange = computed(() => {
  const start = new Date(currentWeekStart.value); start.setDate(start.getDate() - start.getDay())
  const end = new Date(start); end.setDate(start.getDate() + 6)
  return `${formatDate(start)} - ${formatDate(end)}`
})

const currentMonthYear = computed(() => {
  const start = new Date(currentWeekStart.value)
  start.setDate(start.getDate() - start.getDay())
  return start.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const weekClassCount = computed(() => weekSchedule.value.reduce((total, d) => total + d.classes.length, 0))

const prioritizedWeekSchedule = computed(() => {
  return [...weekSchedule.value].sort((a, b) => {
    const aIsToday = isToday(a.date)
    const bIsToday = isToday(b.date)
    if (aIsToday && !bIsToday) return -1
    if (!aIsToday && bIsToday) return 1
    return a.date - b.date
  })
})

const isToday = (date) => new Date().toDateString() === date.toDateString()
const isSunday = (date) => new Date(date).getDay() === 0
const getDayKey = (date) => new Date(date).toDateString()
const isDayExpanded = (day) => expandedDayKey.value === getDayKey(day.date)

const getDayHeaderClass = (day) => {
  if (isToday(day.date)) return 'bg-student-light'
  if (isSunday(day.date)) return 'bg-warning-subtle'

  const dayName = formatDayName(day.date)
  const tones = {
    Monday: 'bg-danger-subtle',
    Tuesday: 'bg-warning-subtle',
    Wednesday: 'bg-danger-subtle',
    Thursday: 'bg-warning-subtle',
    Friday: 'bg-danger-subtle',
    Saturday: 'bg-warning-subtle'
  }

  return tones[dayName] || 'bg-warning-subtle'
}

const getDayIconClass = (day) => {
  if (isToday(day.date)) return 'text-student'
  if (isSunday(day.date)) return 'text-warning-emphasis'

  const dayName = formatDayName(day.date)
  const iconTones = {
    Monday: 'text-danger',
    Tuesday: 'text-warning-emphasis',
    Wednesday: 'text-danger',
    Thursday: 'text-warning-emphasis',
    Friday: 'text-danger',
    Saturday: 'text-warning-emphasis'
  }

  return iconTones[dayName] || 'text-warning-emphasis'
}

const toggleDay = (day) => {
  const dayKey = getDayKey(day.date)
  expandedDayKey.value = expandedDayKey.value === dayKey ? null : dayKey
}

const formatDayName = (date) => date.toLocaleDateString('en-US', { weekday: 'long' })
const formatDate = (date) => formatDateUtil(date)
const formatScheduleTime = (t) => t ? t.substring(0, 5) : ''

const isCurrentClass = (cls) => {
  const now = new Date(); const day = now.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
  if (cls.day?.toLowerCase() !== day) return false
  const time = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0')
  return time >= cls.start_time && time <= cls.end_time
}

const isUpcomingClass = (cls) => {
  const now = new Date(); const day = now.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
  if (cls.day?.toLowerCase() !== day) return false
  const time = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0')
  return time < cls.start_time
}

const getClassStatusBorder = (cls) => {
  if (isCurrentClass(cls)) return 'border-student'
  if (isUpcomingClass(cls)) return 'border-warning'
  return 'border-light'
}

const getClassStatusDot = (cls) => {
  if (isCurrentClass(cls)) return 'bg-student ring-student shadow-student'
  if (isUpcomingClass(cls)) return 'bg-warning shadow-warning'
  return 'bg-light border'
}

const getClassStatusBadge = (cls) => {
  if (isCurrentClass(cls)) return 'bg-student text-white'
  if (isUpcomingClass(cls)) return 'bg-warning text-dark'
  return 'bg-light text-muted border'
}

const nextWeek = () => { currentWeekStart.value = new Date(currentWeekStart.value.setDate(currentWeekStart.value.getDate() + 7)) }
const previousWeek = () => { currentWeekStart.value = new Date(currentWeekStart.value.setDate(currentWeekStart.value.getDate() - 7)) }
const currentWeek = () => { currentWeekStart.value = new Date() }

const loadClassSchedule = async () => {
  const resolvedStudentId = getStudentId()
  if (!resolvedStudentId) {
    throw new Error('Student ID not found. Please login again.')
  }
  await loadData(() => studentPanelService.getClassSchedule(resolvedStudentId))
}

onMounted(async () => {
  await loadProfile()
  await loadClassSchedule()
})
</script>


