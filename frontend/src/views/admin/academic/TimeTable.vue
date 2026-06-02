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
          <div class="row g-3 align-items-end">
            <!-- Row 1: Academic Hierarchy -->
            <div class="col-md-4">
              <label class="form-label fw-semibold mb-1 small">Filter by Program</label>
              <select v-model="filterProgram" class="form-select form-select-sm" @change="onFilterProgramChange">
                <option value="">All Programs</option>
                <option v-for="program in programs" :key="program.id" :value="program.id">{{ program.name }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label fw-semibold mb-1 small">Filter by Session</label>
              <select v-model="filterSession" class="form-select form-select-sm" @change="onFilterSessionChange" :disabled="!filterProgram">
                <option value="">All Sessions</option>
                <option v-for="session in mainFilterSessions" :key="session.id" :value="session.id">{{ session.session_name }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label fw-semibold mb-1 small">Filter by Semester</label>
              <select v-model="filterSemester" class="form-select form-select-sm" @change="loadSchedule" :disabled="!filterSession">
                <option value="">All Semesters (Active)</option>
                <option v-for="semester in filteredSemesters" :key="semester.id" :value="semester.id">
                  {{ formatSemesterLabel(semester) }}
                </option>
              </select>
            </div>

            <!-- Row 2: Secondary Filters and Actions -->
            <div class="col-md-4">
              <label class="form-label fw-semibold mb-1 small">Filter by Teacher</label>
              <select v-model="filterTeacher" class="form-select form-select-sm" @change="loadSchedule">
                <option value="">All Teachers</option>
                <option v-for="teacher in teachers" :key="teacher.id" :value="String(teacher.id)">
                  {{ teacher.full_name }}
                </option>
              </select>
            </div>
            <div class="col-md-8 d-flex gap-2 justify-content-end">
              <button @click="loadSchedule" class="btn btn-outline-secondary btn-sm" title="Refresh"><i class="bi bi-arrow-clockwise"></i></button>
              <button @click="addSchedule()" class="btn btn-admin-primary btn-sm px-4">
                <i class="bi bi-plus-circle me-1"></i>Add Class
              </button>
            </div>
          </div>
          <div class="small text-muted mt-2 mb-0 d-flex justify-content-between align-items-center">
            <span><i class="bi bi-info-circle me-1"></i>Horizontal Timeline mode. Scroll right for later times.</span>
            <div class="d-flex align-items-center gap-2">
               <span class="badge bg-light text-dark border">Found: {{ schedule.length }} classes</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Weekly Timetable (Horizontal Timeline V2) -->
      <div class="card border-0 shadow-sm overflow-hidden">
        <!-- Controls Bar -->
        <div class="admin-tt-v2-controls">
          <div class="admin-tt-v2-zoom-label"><i class="bi bi-zoom-in me-1"></i>Zoom:</div>
          <div class="btn-group btn-group-sm">
            <button class="btn btn-outline-secondary" @click="zoomOut" :disabled="zoomLevel <= 0.5"><i class="bi bi-dash"></i></button>
            <div class="btn btn-light border-top border-bottom admin-tt-v2-zoom-val d-flex align-items-center justify-content-center">
              {{ zoomLevel.toFixed(1) }}x
            </div>
            <button class="btn btn-outline-secondary" @click="zoomIn" :disabled="zoomLevel >= 10"><i class="bi bi-plus"></i></button>
          </div>
          <div class="ms-auto d-flex align-items-center gap-2 me-2">
            
            <div class="btn-group btn-group-sm">
              <button @click="prevWeek" class="btn btn-outline-secondary" title="Previous Week"><i class="bi bi-chevron-left"></i></button>
              <button @click="currentWeek" class="btn btn-outline-secondary fw-bold px-3">
                {{ weekRangeLabel }}
              </button>
              <button @click="nextWeek" class="btn btn-outline-secondary" title="Next Week"><i class="bi bi-chevron-right"></i></button>
            </div>
          </div>

          <div class="btn-group btn-group-sm">
            <button @click="showAddMultipleModal = true" class="btn btn-outline-secondary"><i class="bi bi-files me-1"></i>Bulk Add</button>
          </div>
        </div>

        <div v-if="loading" class="card-body py-5 text-center">
          <div class="spinner-border text-admin" role="status"></div>
          <div class="small text-muted mt-2">Loading timeline...</div>
        </div>
        
        <div v-else class="admin-tt-v2-wrapper" ref="wrapperRef">
          <div class="admin-tt-v2-inner" :style="{ minWidth: (totalTimelineWidth + 120) + 'px', '--admin-tt-v2-hour-w': (60 * zoomLevel) + 'px' }">
            
            <!-- Global Now Line (Spans entire height) -->
            <div v-if="nowLeft > 0 && nowLeft < totalTimelineWidth" class="admin-tt-v2-global-now" :style="{ left: (nowLeft + 90) + 'px' }"></div>

            <!-- Ruler Row (Time Header) -->
            <div class="admin-tt-v2-ruler-row">
              <div class="admin-tt-v2-day-col">Day</div>
              <div class="admin-tt-v2-ruler-track">
                <div v-for="tick in rulerTicks" :key="tick.time" 
                     class="admin-tt-v2-tick" 
                     :class="[tick.isMajor ? 'admin-tt-v2-tick--major' : 'admin-tt-v2-tick--minor', isCurrentHour(tick) ? 'admin-tt-v2-tick--current' : '']"
                     :style="{ left: tick.left + 'px' }">
                  <div class="admin-tt-v2-tick-line"></div>
                  <div v-if="tick.isMajor" class="admin-tt-v2-tick-label">{{ tick.label }}</div>
                </div>
              </div>
            </div>

            <!-- Day Rows -->
            <div v-for="(dayStr, index) in DAYS_OF_WEEK" :key="dayStr" 
                 class="admin-tt-v2-row" 
                 :class="{ 'admin-tt-v2-row--today': isToday(dayStr) }">
                 
              <!-- Day Label -->
              <div class="admin-tt-v2-row-label">
                <div class="day-name">{{ DAY_LABELS[index] }}</div>
                <div class="day-date">{{ getDayDate(index) }}</div>
              </div>
              
              <!-- Timeline Track -->
              <div class="admin-tt-v2-track" 
                   @dragover.prevent 
                   @drop.prevent="onRowDrop(dayStr)"
                   :style="{ minHeight: getRowHeight(dayStr) + 'px' }">
                
                <!-- Lecture Blocks (Overlaps stack automatically via top property) -->
                <div v-for="block in getDayBlocks(dayStr)" :key="block.id"
                     class="admin-tt-v2-block"
                     :class="[
                       block.schedule_type === 'temporary' ? 'admin-tt-v2-block--temporary' : 'admin-tt-v2-block--permanent',
                       { 'opacity-75': block.semester_status === 'completed' },
                       { 'admin-tt-v2-block--live': isLive(block) }
                     ]"
                     :style="{ left: block.left + 'px', width: block.width + 'px', top: block.top + 'px', cursor: block.semester_status === 'completed' ? 'default' : 'pointer' }"
                     :draggable="block.semester_status !== 'completed'"
                     @dragstart="block.semester_status !== 'completed' && onBlockDragStart(block)"
                     @mouseenter="onBlockMouseEnter(block, $event)"
                     @mousemove="onBlockMouseMove($event)"
                     @mouseleave="onBlockMouseLeave">
                  
                  <!-- Case 1: Very Narrow Block (< 50px) - Icon only -->
                  <div v-if="block.width < 50" class="admin-tt-v2-block-compact">
                    <i class="bi bi-journal-bookmark-fill"></i>
                  </div>

                  <!-- Case 2: Narrow Block (50px - 100px) - Subject only, hide time -->
                  <div v-else-if="block.width < 100" class="admin-tt-v2-block-narrow">
                    <div class="admin-tt-v2-block-subject text-truncate">{{ block.subject_name || block.subject_code }}</div>
                    <div v-if="block.schedule_type === 'temporary'" class="admin-tt-v2-temp-dot" title="Temporary"></div>
                  </div>

                  <!-- Case 3: Normal Block (> 100px) - Full content -->
                  <template v-else>
                    <div class="admin-tt-v2-block-subject">{{ block.subject_name || block.subject_code || 'Lecture' }} <span v-if="block.schedule_type === 'temporary'" class="admin-tt-v2-temp-badge">●TEMP</span></div>
                    <div class="admin-tt-v2-block-time">{{ formatTime(block.start_time) }} - {{ formatTime(block.end_time) }}</div>
                  </template>
                  
                  <!-- Quick Actions on Block Hover -->
                    <div class="admin-tt-v2-block-actions" v-if="block.semester_status !== 'completed'">
                    <button class="btn btn-sm btn-light text-primary border-0 p-0 px-1" @click.stop="editSchedule(block)"><i class="bi bi-pencil"></i></button>
                    <button class="btn btn-sm btn-light text-danger border-0 p-0 px-1" @click.stop="deleteSchedule(block)"><i class="bi bi-trash"></i></button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>

  <!-- Modals -->
  <Teleport to="body">
    <!-- Global Tooltip -->
    <div v-if="hoveredBlock" class="admin-tt-v2-tooltip-global" :style="tooltipStyle">
      <div class="fw-bold mb-1">{{ hoveredBlock.subject_name }} ({{ hoveredBlock.subject_code }})</div>
      <div class="mb-1"><i class="bi bi-clock me-1 text-info"></i>{{ formatTime(hoveredBlock.start_time) }} - {{ formatTime(hoveredBlock.end_time) }}</div>
      <div class="mb-1"><i class="bi bi-person-badge me-1 text-warning"></i>{{ hoveredBlock.teacher_name || 'No teacher' }}</div>
      <div class="mb-1"><i class="bi bi-geo-alt me-1 text-success"></i>Room: {{ hoveredBlock.room || '-' }}</div>
      <div class="mb-1"><i class="bi bi-mortarboard me-1 text-danger"></i>Prog: {{ hoveredBlock.program_name }}</div>
      <div class="mb-1"><i class="bi bi-layers me-1 text-primary"></i>Sem: {{ hoveredBlock.semester_name }}</div>
      <div v-if="hoveredBlock.schedule_type === 'temporary'" class="text-warning mt-1 fw-semibold"><i class="bi bi-exclamation-circle me-1"></i>Temp Date: {{ hoveredBlock.specific_date }}</div>
    </div>

    <ScheduleModal
      :show="showModal"
      :form="scheduleForm"
      :is-edit="!!editingSchedule"
      :saving="saving"
      :subjects="subjects"
      :teachers="teachers"
      :unavailable-teacher-ids="[]"
      :unavailable-teacher-conflicts="{}"
      :programs="programs"
      :sessions="modalSessions"
      :semesters="programSemesters"
      @close="closeModal"
      @save="saveSchedule"
      @program-change="onProgramChange"
      @session-change="onModalSessionChange"
      @semester-change="handleSemesterChange"
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { ScheduleModal, BulkScheduleModal } from '@/components/shared/timetable'
import { timetableService } from '@/services/admin/managementService'
import { subjectService, teacherService, programService, cacheService } from '@/services/shared'
import sessionService from '@/services/shared/academic/sessionService'
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
const sessions = ref([])
const programSemesters = ref([])
const filteredSemesters = ref([])
const filterProgram = ref('')
const filterSession = ref('')
const filterSemester = ref('')
const filterTeacher = ref('')
const showModal = ref(false)
const showAddMultipleModal = ref(false)
const editingSchedule = ref(null)
const showConfirmDialog = ref(false)
const scheduleToDelete = ref(null)

const scheduleForm = ref({ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', academic_session: '', semester: '', is_active: true, schedule_type: 'permanent', specific_date: '' })
const multipleScheduleForms = ref([{ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', academic_session: '', semester: '', is_active: true, schedule_type: 'permanent', specific_date: '', availableSemesters: [] }])
const modalSessions = computed(() => {
  if (!scheduleForm.value.program) return []
  return sessions.value.filter(s => getSafeId(s.program) === String(scheduleForm.value.program))
})
const mainFilterSessions = computed(() => {
  if (!filterProgram.value) return []
  return sessions.value.filter(s => getSafeId(s.program) === String(filterProgram.value))
})

const handleSemesterChange = () => {
  scheduleForm.value.subject = ''
}

// ── Timeline V2 Logic ────────────────────────────────────────────────────────
const zoomLevel = ref(2)
const DAY_START_MIN = 7 * 60  // 7:00 AM
const DAY_END_MIN = 24 * 60   // 11:00 PM

const currentDate = ref(new Date())
const getWeekRange = computed(() => {
  const d = new Date(currentDate.value)
  const day = d.getDay() || 7
  const start = new Date(d)
  start.setDate(d.getDate() - day + 1)
  start.setHours(0, 0, 0, 0)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  end.setHours(23, 59, 59, 999)
  return { start, end }
})

const weekRangeLabel = computed(() => {
  const { start, end } = getWeekRange.value
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const optionsShort = { month: 'short', day: 'numeric' }
  const optionsLong = { month: 'short', day: 'numeric', year: 'numeric' }
  
  const rangeStr = `${start.toLocaleDateString('en-US', optionsShort)} - ${end.toLocaleDateString('en-US', optionsLong)}`
  
  if (start <= today && today <= end) return `This Week (${start.getFullYear()})`
  return rangeStr
})

const nextWeek = () => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + 7)
  currentDate.value = d
}
const prevWeek = () => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() - 7)
  currentDate.value = d
}
const currentWeek = () => { currentDate.value = new Date() }
const LANE_HEIGHT = 46        // Block height + padding

// Global Tooltip Logic
const hoveredBlock = ref(null)
const mousePos = ref({ x: 0, y: 0 })

const onBlockMouseEnter = (block, event) => {
  hoveredBlock.value = block
  mousePos.value = { x: event.clientX, y: event.clientY }
}
const onBlockMouseMove = (event) => {
  if (hoveredBlock.value) {
    mousePos.value = { x: event.clientX, y: event.clientY }
  }
}
const onBlockMouseLeave = () => {
  hoveredBlock.value = null
}

const tooltipStyle = computed(() => {
  let x = mousePos.value.x + 15
  let y = mousePos.value.y + 15
  
  // Prevent overflowing right edge
  if (x + 260 > window.innerWidth) {
    x = mousePos.value.x - 275
  }
  // Prevent overflowing bottom edge
  if (y + 150 > window.innerHeight) {
    y = mousePos.value.y - 165
  }
  
  return { left: x + 'px', top: y + 'px' }
})

const zoomIn = () => { zoomLevel.value = Math.min(zoomLevel.value + 0.5, 10) }
const zoomOut = () => { zoomLevel.value = Math.max(zoomLevel.value - 0.5, 0.5) }

const totalTimelineWidth = computed(() => (DAY_END_MIN - DAY_START_MIN) * zoomLevel.value)
const getLeftPos = (minutes) => (minutes - DAY_START_MIN) * zoomLevel.value

// Time parser helper
const timeToMinutes = (timeStr) => {
  if (!timeStr) return 0
  const [h, m] = timeStr.split(':').map(Number)
  return (h * 60) + (m || 0)
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

// Generate Ruler Ticks (Every 15 min)
const rulerTicks = computed(() => {
  const ticks = []
  for (let m = DAY_START_MIN; m <= DAY_END_MIN; m += 15) {
    const isMajor = m % 60 === 0
    let label = ''
    if (isMajor) {
      const hr = Math.floor(m / 60)
      const hr12 = hr % 12 || 12
      const suffix = hr >= 12 ? 'PM' : 'AM'
      label = `${hr12}:00 ${suffix}`
    }
    const leftPos = (m - DAY_START_MIN) * zoomLevel.value
    ticks.push({ min: m, isMajor, label, time: m, left: leftPos })
  }
  return ticks
})

// Now Line Logic
const nowMinutes = ref(0)
let nowTimer = null
const updateNow = () => {
  const d = new Date()
  nowMinutes.value = d.getHours() * 60 + d.getMinutes()
}
const nowLeft = computed(() => getLeftPos(nowMinutes.value))

const isToday = (dayStr) => {
  const { start, end } = getWeekRange.value
  const today = new Date()
  if (today < start || today > end) return false
  const todayIndex = (today.getDay() || 7) - 1
  const dayIndex = DAYS_OF_WEEK.indexOf(dayStr.toLowerCase())
  return todayIndex === dayIndex
}

const isCurrentHour = (tick) => {
  if (!tick.isMajor) return false
  const nowHr = Math.floor(nowMinutes.value / 60)
  const tickHr = Math.floor(tick.min / 60)
  return nowHr === tickHr && isToday(DAYS_OF_WEEK[new Date().getDay() - 1] || '') // strict current check
}

const getDayDate = (dayIndex) => {
  const { start } = getWeekRange.value
  const d = new Date(start)
  d.setDate(d.getDate() + dayIndex)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// Processed Blocks & Lanes (Overlap Stacking)
const processedSchedule = computed(() => {
  const out = {}
  DAYS_OF_WEEK.forEach(d => out[d] = { blocks: [], laneCount: 1 })
  
    DAYS_OF_WEEK.forEach((day, index) => {
      const { start, end } = getWeekRange.value
      // Calculate the specific date for this day of the week
      const currentDayDate = new Date(start)
      currentDayDate.setDate(currentDayDate.getDate() + index)
      currentDayDate.setHours(12, 0, 0, 0) // Use noon to avoid TZ issues
      
      const dayItems = schedule.value
        .filter(item => {
          if (String(item.day || '').toLowerCase() !== day) return false
          
          // Permanent classes show every week, but ONLY within their semester's date range
          if (item.schedule_type === 'permanent') {
            if (item.semester_start_date && item.semester_end_date) {
              const semStart = new Date(item.semester_start_date)
              const semEnd = new Date(item.semester_end_date)
              semStart.setHours(0, 0, 0, 0)
              semEnd.setHours(23, 59, 59, 999)
              
              // Check if THIS SPECIFIC DAY falls within the semester range
              return currentDayDate >= semStart && currentDayDate <= semEnd
            }
            return true
          }
        
        // Temporary classes only show on their specific week
        if (item.schedule_type === 'temporary' && item.specific_date) {
          const itemDate = new Date(item.specific_date)
          itemDate.setHours(0, 0, 0, 0)
          return itemDate >= start && itemDate <= end
        }
        return false
      })
      .sort((a, b) => timeToMinutes(a.start_time) - timeToMinutes(b.start_time))
      
    const lanes = []
    
    dayItems.forEach(item => {
      const startMin = Math.max(timeToMinutes(item.start_time), DAY_START_MIN)
      const endMin = Math.min(timeToMinutes(item.end_time), DAY_END_MIN)
      const duration = endMin - startMin
      
      const blockWidth = Math.max(duration * zoomLevel.value, 24) // min 24px width
      
      let placedLane = -1
      for (let i = 0; i < lanes.length; i++) {
        const laneEnd = lanes[i]
        if (startMin >= laneEnd) {
          placedLane = i
          lanes[i] = endMin
          break
        }
      }
      
      if (placedLane === -1) {
        placedLane = lanes.length
        lanes.push(endMin)
      }
      
      out[day].blocks.push({
        ...item,
        left: getLeftPos(startMin),
        width: blockWidth,
        top: placedLane * LANE_HEIGHT + 4
      })
    })
    out[day].laneCount = Math.max(1, lanes.length)
  })
  return out
})

const getDayBlocks = (day) => processedSchedule.value[day]?.blocks || []
const getRowHeight = (day) => {
  const lanes = processedSchedule.value[day]?.laneCount || 1
  return Math.max(52, lanes * LANE_HEIGHT + 10)
}

// ── Drag & Drop ───────────────────────────────────────────────────────────────
const draggingBlock = ref(null)
const onBlockDragStart = (block) => { draggingBlock.value = block }
const onRowDrop = async (targetDay) => {
  if (!draggingBlock.value) return
  const item = draggingBlock.value
  draggingBlock.value = null
  
  if (item.day === targetDay) return // same day
  
  try {
    const payload = buildSchedulePayload(item, { day: targetDay })
    await timetableService.update(item.id, payload)
    showSuccess(`Moved to ${targetDay}`)
    loadSchedule()
  } catch(e) {
    showError('Failed to move class')
  }
}

// ── Form & Data Logic ─────────────────────────────────────────────────────────
// BUG #2 FIX: Ensure primitive strings are extracted safely from objects
const getSafeId = (v) => {
  if (v == null) return ''
  if (typeof v === 'object') return String(v.id || v.pk || '')
  return String(v)
}

const buildSchedulePayload = (item, overrides = {}) => {
  return {
    day: String(overrides.day ?? item.day ?? '').toLowerCase(),
    start_time: overrides.start_time ?? item.start_time,
    end_time: overrides.end_time ?? item.end_time,
    subject: overrides.subject ?? getSafeId(item.subject) ?? getSafeId(item.subject_id),
    teacher: overrides.teacher ?? getSafeId(item.teacher) ?? getSafeId(item.teacher_id),
    room: overrides.room ?? item.room,
    program: overrides.program ?? (item.program || null),
    academic_session: overrides.academic_session ?? (item.academic_session || null),
    semester: overrides.semester ?? (item.semester || null),
    is_active: overrides.is_active ?? (item.is_active !== false),
    schedule_type: overrides.schedule_type ?? item.schedule_type ?? 'permanent',
    specific_date: (overrides.specific_date || item.specific_date) || null
  }
}

const addSchedule = () => {
  editingSchedule.value = null
  scheduleForm.value = {
    day: '', start_time: '08:00:00', end_time: '09:00:00', 
    subject: '', teacher: '', room: '', program: '', academic_session: '', semester: '', 
    is_active: true, schedule_type: 'permanent', specific_date: ''
  }
  showModal.value = true
}

const editSchedule = (item) => {
  editingSchedule.value = item
  scheduleForm.value = {
    ...item,
    subject: getSafeId(item.subject) || getSafeId(item.subject_id),
    teacher: getSafeId(item.teacher) || getSafeId(item.teacher_id),
    program: getSafeId(item.program),
    academic_session: getSafeId(item.academic_session),
    semester: getSafeId(item.semester),
    is_active: item.is_active !== false,
    schedule_type: item.schedule_type || 'permanent',
    specific_date: item.specific_date || ''
  }
  if (scheduleForm.value.academic_session) loadSemestersBySession(scheduleForm.value.academic_session, 'form')
  else if (scheduleForm.value.program) loadSemestersByProgram(scheduleForm.value.program, 'form')
  showModal.value = true
}

const deleteSchedule = (item) => { scheduleToDelete.value = item; showConfirmDialog.value = true }
const confirmDeleteSchedule = async () => {
  try {
    await timetableService.delete(scheduleToDelete.value.id)
    showSuccess('Schedule deleted')
    loadSchedule()
  } catch (error) { showError('Failed to delete') } 
  finally { showConfirmDialog.value = false; scheduleToDelete.value = null }
}

const loadSchedule = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterProgram.value) params.program = filterProgram.value
    if (filterSemester.value) params.semester = filterSemester.value
    if (filterTeacher.value) params.teacher = filterTeacher.value
    if (filterSession.value) params.academic_session = filterSession.value
    const response = await timetableService.getAll(params, { forceRefresh: true })
    schedule.value = response.data?.results || response.data || response.results || response
  } catch (error) { showError('Failed to load timetable') } 
  finally { loading.value = false }
}

const isSemesterActive = (s) => {
  if (!s || typeof s !== 'object') return false
  // Return true ONLY if status is explicitly 'active'
  return String(s.status || '').toLowerCase() === 'active'
}

const isLive = (block) => {
  if (!block) return false
  const now = new Date()
  const dayName = now.toLocaleString('en-us', { weekday: 'long' }).toLowerCase()
  if (block.day.toLowerCase() !== dayName) return false
  
  if (block.schedule_type === 'temporary' && block.specific_date) {
    const todayStr = now.toISOString().split('T')[0]
    if (block.specific_date !== todayStr) return false
  }

  const parseTime = (timeStr) => {
    const [h, m, s] = timeStr.split(':').map(Number)
    const d = new Date()
    d.setHours(h, m, s || 0, 0)
    return d
  }
  
  const start = parseTime(block.start_time)
  const end = parseTime(block.end_time)
  return now >= start && now <= end
}

const formatSemesterLabel = (s) => {
  if (!s) return ''
  let label = `Semester ${s.number}`
  if (s.session?.session_name) label += ` (${s.session.session_name})`
  if (String(s.status || '').toLowerCase() === 'completed') label += ' [Completed]'
  return label
}

const loadSemestersByProgram = async (programId, target = 'form') => {
  try {
    const response = await programService.getProgramSemesters(programId)
    const list = (response.results || response)
    if (target === 'form') programSemesters.value = list.filter(isSemesterActive)
    else filteredSemesters.value = list
  } catch (error) { console.error(error) }
}


const onProgramChange = async () => {
  scheduleForm.value.academic_session = ''
  scheduleForm.value.semester = ''
  scheduleForm.value.subject = ''
  programSemesters.value = []
}

const onModalSessionChange = async () => {
  scheduleForm.value.semester = ''
  scheduleForm.value.subject = ''
  if (scheduleForm.value.academic_session) await loadSemestersBySession(scheduleForm.value.academic_session, 'form')
  else programSemesters.value = []
}

const loadSemestersBySession = async (sessionId, target = 'form') => {
  try {
    const response = await sessionService.getSessionSemesters(sessionId)
    const list = (response.results || response)
    const activeList = list.filter(isSemesterActive)
    if (target === 'form') programSemesters.value = activeList
    else filteredSemesters.value = activeList
  } catch (error) { console.error(error) }
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

const onFilterProgramChange = async () => {
  filterSession.value = ''
  filterSemester.value = ''
  filteredSemesters.value = []
  loadSchedule()
}

const onFilterSessionChange = async () => {
  filterSemester.value = ''
  if (filterSession.value) await loadSemestersBySession(filterSession.value, 'filter')
  else filteredSemesters.value = []
  loadSchedule()
}

const loadDropdowns = async () => {
  try {
    const [subRes, teaRes, progRes, sessRes] = await Promise.all([
      subjectService.getAllSubjects(),
      teacherService.getAllTeachers(),
      programService.getAllPrograms(),
      sessionService.getSessions()
    ])
    subjects.value = subRes.results || subRes
    teachers.value = teaRes.results || teaRes
    programs.value = progRes.results || progRes
    sessions.value = sessRes.results || sessRes
  } catch (e) { console.error(e) }
}

const saveSchedule = async () => {
  saving.value = true
  try {
    const payload = buildSchedulePayload(scheduleForm.value)
    if (editingSchedule.value) await timetableService.update(editingSchedule.value.id, payload)
    else await timetableService.create(payload)
    showSuccess(editingSchedule.value ? 'Updated' : 'Added')
    closeModal()
    loadSchedule()
  } catch (e) { 
    showError(e.response?.data?.error || 'Failed to save schedule')
  }
  finally { saving.value = false }
}

const saveMultipleSchedules = async () => {
  saving.value = true
  try {
    await Promise.all(multipleScheduleForms.value.map(data => timetableService.create(buildSchedulePayload(data))))
    showSuccess('Bulk added successfully')
    closeMultipleModal()
    loadSchedule()
  } catch (e) { showError('Failed to save') }
  finally { saving.value = false }
}

const closeModal = () => { showModal.value = false; editingSchedule.value = null }
const closeMultipleModal = () => { showAddMultipleModal.value = false }
const addScheduleForm = () => { multipleScheduleForms.value.push({ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true, schedule_type: 'permanent', specific_date: '', availableSemesters: [] }) }
const removeScheduleForm = (i) => { multipleScheduleForms.value.splice(i, 1) }

onMounted(() => {
  loadSchedule()
  loadDropdowns()
  updateNow()
  nowTimer = setInterval(updateNow, 60000)
})

onUnmounted(() => {
  if (nowTimer) clearInterval(nowTimer)
})
</script>
