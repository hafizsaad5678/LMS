<template>
  <TeacherPageTemplate
    title="Class Schedule"
    subtitle="View your weekly class timetable"
    icon="bi bi-calendar3"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <div class="row g-4">
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
const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const timeSlots = [
  { time: '08:00' },
  { time: '09:00' },
  { time: '10:00' },
  { time: '11:00' },
  { time: '12:00' },
  { time: '13:00' },
  { time: '14:00' },
  { time: '15:00' },
  { time: '16:00' }
]

// Mock schedule data - will be replaced with real API data
const schedule = ref([])

const loadSchedule = async () => {
  try {
    const response = await teacherPanelService.getTimetable()
    const now = new Date()
    const currentDay = now.toLocaleDateString('en-US', { weekday: 'long' })
    
    schedule.value = response.results.map(slot => {
      // Determine status based on current time
      const currentTime = now.getHours() * 60 + now.getMinutes()
      const [startHour, startMin] = slot.start_time.split(':').map(Number)
      const [endHour, endMin] = slot.end_time.split(':').map(Number)
      const slotStart = startHour * 60 + startMin
      const slotEnd = endHour * 60 + endMin
      
      // Capitalize the day from backend for comparison
      const slotDay = slot.day.charAt(0).toUpperCase() + slot.day.slice(1)
      
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
        time: slot.start_time,
        endTime: slot.end_time,
        subject: slot.subject,
        subjectCode: slot.subject_code,
        room: slot.room,
        students: slot.students,
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
    return a.time.localeCompare(b.time)
  })
})

const getClassForSlot = (day, time) => {
  return schedule.value.find(cls => cls.day === day && cls.time === time)
}

const getClassColor = (cls) => {
  const colors = {
    'Data Structures': 'bg-primary text-white',
    'Database Systems': 'bg-success text-white',
    'Web Development': 'bg-info text-white'
  }
  return colors[cls.subject] || 'bg-secondary text-white'
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

