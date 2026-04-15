<template>
  <TeacherPageTemplate
    title="Class Schedule"
    subtitle="View your weekly class timetable"
    icon="bi bi-calendar3"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <div class="row g-4 teacher-class-schedule">
      <!-- Schedule Overview -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold">
                <i class="bi bi-calendar-week me-2 text-teacher"></i>Weekly Schedule
              </h6>
              <div class="d-flex gap-2">
                <button @click="previousWeek" class="btn btn-sm btn-outline-secondary">
                  <i class="bi bi-chevron-left"></i>
                </button>
                <span class="btn btn-sm btn-outline-secondary disabled">
                  {{ currentWeekLabel }}
                </span>
                <button @click="nextWeek" class="btn btn-sm btn-outline-secondary">
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </div>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-bordered mb-0 schedule-table">
                <thead class="table-light">
                  <tr>
                    <th class="table-col-w-100">Time</th>
                    <th v-for="day in weekDays" :key="day" class="text-center">{{ day }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="timeSlot in timeSlots" :key="timeSlot.time">
                    <td class="fw-semibold text-muted">{{ timeSlot.time }}</td>
                    <td v-for="day in weekDays" :key="day" class="schedule-cell">
                      <div 
                        v-if="getClassForSlot(day, timeSlot.time)" 
                        class="schedule-item"
                        :class="getClassColor(getClassForSlot(day, timeSlot.time))"
                      >
                        <div class="fw-semibold">{{ getClassForSlot(day, timeSlot.time).subject }}</div>
                        <small>{{ getClassForSlot(day, timeSlot.time).room }}</small>

                        <div class="schedule-hover-detail">
                          <div class="fw-semibold mb-1">{{ getClassForSlot(day, timeSlot.time).subject }}</div>
                          <div class="small"><i class="bi bi-upc-scan me-1"></i>{{ getClassForSlot(day, timeSlot.time).subjectCode || 'N/A' }}</div>
                          <div class="small"><i class="bi bi-clock me-1"></i>{{ getClassForSlot(day, timeSlot.time).time }} - {{ getClassForSlot(day, timeSlot.time).endTime }}</div>
                          <div class="small"><i class="bi bi-geo-alt me-1"></i>{{ getClassForSlot(day, timeSlot.time).room || 'N/A' }}</div>
                          <div class="small"><i class="bi bi-people me-1"></i>{{ getClassForSlot(day, timeSlot.time).students }} students</div>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Today's Classes -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h6 class="mb-0 fw-semibold">
              <i class="bi bi-calendar-day me-2 text-teacher"></i>Today's Classes
            </h6>
          </div>
          <div class="card-body">
            <div v-if="todayClasses.length === 0" class="text-center py-4">
              <i class="bi bi-calendar-x display-4 text-muted"></i>
              <p class="text-muted mt-2">No classes today</p>
            </div>
            <div v-else class="d-flex flex-column gap-3">
              <div 
                v-for="cls in todayClasses" 
                :key="cls.id"
                class="class-card p-3 rounded"
                :class="cls.status === 'current' ? 'bg-teacher-light border-teacher' : 'bg-light'"
              >
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="mb-0 fw-semibold">{{ cls.subject }}</h6>
                  <span :class="['badge', getStatusBadge(cls.status)]">
                    {{ cls.status }}
                  </span>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                  <small class="text-muted">
                    <i class="bi bi-clock me-1"></i>{{ cls.time }} - {{ cls.endTime }}
                  </small>
                  <small class="text-muted">
                    <i class="bi bi-geo-alt me-1"></i>{{ cls.room }}
                  </small>
                </div>
                <div class="mt-2">
                  <small class="text-muted">
                    <i class="bi bi-people me-1"></i>{{ cls.students }} students
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Schedule', href: TEACHER_ROUTES.CLASS_SCHEDULE.path },
  { name: 'Class Schedule' }
]

const actions = [
  { label: 'Mark Attendance', icon: 'bi bi-calendar-check', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.MARK_ATTENDANCE.name }) },
  { label: 'Exam Schedule', icon: 'bi bi-calendar-event', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.EXAM_SCHEDULE.name }) }
]

const currentWeek = ref(new Date())
const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

const normalizeTime = (value) => {
  const raw = String(value || '').trim()
  if (!raw) return ''
  const parts = raw.split(':')
  if (parts.length < 2) return ''
  const hours = String(parts[0]).padStart(2, '0')
  const minutes = String(parts[1]).padStart(2, '0')
  return `${hours}:${minutes}`
}

const timeToMinutes = (value) => {
  const normalized = normalizeTime(value)
  if (!normalized) return NaN
  const [hours, minutes] = normalized.split(':').map(Number)
  if (!Number.isFinite(hours) || !Number.isFinite(minutes)) return NaN
  return hours * 60 + minutes
}

const dayLabel = (value) => {
  const day = String(value || '').trim().toLowerCase()
  if (!day) return ''
  return day.charAt(0).toUpperCase() + day.slice(1)
}

const timeSlots = computed(() => {
  if (!schedule.value.length) {
    return Array.from({ length: 10 }, (_, idx) => ({ time: `${String(idx + 8).padStart(2, '0')}:00` }))
  }

  const starts = schedule.value
    .map(item => timeToMinutes(item.time))
    .filter(Number.isFinite)

  if (!starts.length) {
    return Array.from({ length: 10 }, (_, idx) => ({ time: `${String(idx + 8).padStart(2, '0')}:00` }))
  }

  const minHour = Math.max(6, Math.floor(Math.min(...starts) / 60) - 1)
  const maxHour = Math.min(20, Math.ceil(Math.max(...starts) / 60) + 1)
  const slots = []
  for (let hour = minHour; hour <= maxHour; hour += 1) {
    slots.push({ time: `${String(hour).padStart(2, '0')}:00` })
  }
  return slots
})

const schedule = ref([])

const loadSchedule = async () => {
  try {
    const response = await teacherPanelService.getTimetable()
    const rows = Array.isArray(response) ? response : (response?.results || [])
    const now = new Date()
    const currentDay = now.toLocaleDateString('en-US', { weekday: 'long' })
    
    schedule.value = rows.map(slot => {
      // Determine status based on current time
      const currentTime = now.getHours() * 60 + now.getMinutes()
      const normalizedStart = normalizeTime(slot.start_time)
      const normalizedEnd = normalizeTime(slot.end_time)
      const [startHour, startMin] = normalizedStart.split(':').map(Number)
      const [endHour, endMin] = normalizedEnd.split(':').map(Number)
      const slotStart = startHour * 60 + startMin
      const slotEnd = endHour * 60 + endMin
      
      // Normalize day from backend for comparison
      const slotDay = dayLabel(slot.day)
      
      let status = 'upcoming'
      if (slotDay === currentDay) {
        if (currentTime >= slotStart && currentTime <= slotEnd) {
          status = 'current'
        } else if (currentTime > slotEnd) {
          status = 'completed'
        }
      }
      
      return {
        id: slot.id,
        day: slotDay,
        time: normalizedStart,
        endTime: normalizedEnd,
        subject: slot.subject || slot.subject_name || slot.subjectCode || 'N/A',
        subjectCode: slot.subject_code,
        room: slot.room,
        students: slot.students ?? slot.student_count ?? 0,
        status: status
      }
    })
  } catch (error) {
    schedule.value = []
  }
}

const currentWeekLabel = computed(() => {
  const start = new Date(currentWeek.value)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  
  return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
})

const todayClasses = computed(() => {
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long' })
  return schedule.value.filter(cls => cls.day === today).sort((a, b) => {
    return timeToMinutes(a.time) - timeToMinutes(b.time)
  })
})

const getClassForSlot = (day, time) => {
  const slotStart = timeToMinutes(time)
  const slotEnd = slotStart + 60

  return schedule.value.find(cls => {
    if (cls.day !== day) return false
    const classStart = timeToMinutes(cls.time)
    // render class in the slot where its start time falls
    return classStart >= slotStart && classStart < slotEnd
  })
}

const getClassColor = (cls) => {
  const palette = [
    'bg-primary text-white',
    'bg-success text-white',
    'bg-info text-white',
    'bg-warning text-dark',
    'bg-danger text-white',
    'bg-secondary text-white'
  ]

  const seed = String(cls?.subjectCode || cls?.subject || cls?.id || '')
  if (!seed) return palette[palette.length - 1]

  const hash = seed
    .split('')
    .reduce((acc, ch) => acc + ch.charCodeAt(0), 0)

  return palette[hash % palette.length]
}

const getStatusBadge = (status) => {
  const badges = {
    current: 'bg-success',
    upcoming: 'bg-primary',
    completed: 'bg-secondary'
  }
  return badges[status] || 'bg-secondary'
}

const previousWeek = () => {
  const newDate = new Date(currentWeek.value)
  newDate.setDate(newDate.getDate() - 7)
  currentWeek.value = newDate
}

const nextWeek = () => {
  const newDate = new Date(currentWeek.value)
  newDate.setDate(newDate.getDate() + 7)
  currentWeek.value = newDate
}

const markAttendance = () => {
  router.push(TEACHER_ROUTES.MARK_ATTENDANCE.path)
}

const viewExamSchedule = () => {
  router.push(TEACHER_ROUTES.EXAM_SCHEDULE.path)
}

onMounted(() => {
  loadSchedule()
})
</script>

