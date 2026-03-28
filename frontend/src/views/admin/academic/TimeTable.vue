<template>
  <AdminPageTemplate title="Class Timetable" subtitle="Manage class schedules and timetables" icon="bi bi-calendar-week" :breadcrumbs="breadcrumbs" :actions="actions">
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
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label fw-semibold">Filter by Program</label>
            <select v-model="filterProgram" class="form-select" @change="onFilterProgramChange">
              <option value="">All Programs</option>
              <option v-for="program in programs" :key="program.id" :value="program.id">{{ program.name }}</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label fw-semibold">Filter by Semester</label>
            <select v-model="filterSemester" class="form-select" @change="loadSchedule" :disabled="!filterProgram">
              <option value="">All Semesters</option>
              <option v-for="semester in filteredSemesters" :key="semester.id" :value="semester.id">
                Semester {{ semester.number }} - {{ semester.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label fw-semibold">Default Period</label>
            <select v-model="periodDuration" class="form-select" @change="generateTimeSlots">
              <option v-for="opt in PERIOD_DURATIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label fw-semibold">Start Time</label>
            <input v-model="startTime" type="time" class="form-control" @change="generateTimeSlots">
          </div>
          <div class="col-md-2">
            <button @click="showPeriodSettings = true" class="btn btn-outline-admin w-100">
              <i class="bi bi-gear me-2"></i>Day Settings
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Weekly Timetable -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom">
        <h5 class="card-title mb-0 fw-semibold"><i class="bi bi-calendar-week me-2 text-admin"></i>Weekly Schedule</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-bordered mb-0 timetable">
            <thead class="bg-light">
              <tr>
                <th class="col-w-100">Time</th>
                <th v-for="(day, index) in DAYS_OF_WEEK" :key="day">{{ DAY_LABELS[index] }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="slot in timeSlots" :key="slot">
                <td class="fw-semibold text-center">{{ slot }}</td>
                <td v-for="day in DAYS_OF_WEEK" :key="day" class="schedule-cell">
                  <div v-if="getSchedule(day, slot)" class="schedule-item" @click.stop>
                    <div class="d-flex justify-content-between align-items-start mb-1">
                      <div class="fw-semibold flex-grow-1">{{ getSchedule(day, slot).subject_name || 'Unknown' }}</div>
                      <div class="btn-group btn-group-sm">
                        <button @click="editSchedule(getSchedule(day, slot))" class="btn btn-sm btn-outline-primary p-0 px-1" title="Edit"><i class="bi bi-pencil"></i></button>
                        <button @click="deleteSchedule(getSchedule(day, slot))" class="btn btn-sm btn-outline-danger p-0 px-1" title="Delete"><i class="bi bi-trash"></i></button>
                      </div>
                    </div>
                    <small class="text-muted d-block">{{ getSchedule(day, slot).teacher_name || '' }}</small>
                    <small class="text-muted d-block">{{ getSchedule(day, slot).room }}</small>
                  </div>
                  <div v-else class="text-muted small text-center add-slot" @click="addSchedule(day, slot)">
                    <i class="bi bi-plus-circle"></i>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card-footer bg-white border-top">
        <div class="d-flex justify-content-between align-items-center">
          <div class="text-muted small">
            Showing {{ schedule.length }} schedule(s)
            <span v-if="filterProgram || filterSemester" class="badge bg-info ms-2">Filtered</span>
          </div>
          <div class="d-flex gap-2">
            <button @click="loadSchedule" class="btn btn-sm btn-outline-secondary"><i class="bi bi-arrow-clockwise me-1"></i>Refresh</button>
            <button @click="showAddMultipleModal = true" class="btn btn-sm btn-admin-primary"><i class="bi bi-plus-circle me-1"></i>Add Multiple Classes</button>
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
    <DaySettingsModal
      :show="showPeriodSettings"
      :settings="daySettings"
      @close="showPeriodSettings = false"
      @apply="applyDaySettings"
    />
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { ScheduleModal, BulkScheduleModal, DaySettingsModal } from '@/components/shared/timetable'
import { timetableService } from '@/services/admin/managementService'
import { subjectService, teacherService, programService, cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { DAYS_OF_WEEK, DAY_LABELS, PERIOD_DURATIONS } from '@/utils/constants/config'

const breadcrumbs = [{ name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path }, { name: 'Timetable' }]
const actions = [{ label: 'Print', icon: 'bi bi-printer', variant: 'btn-admin-outline', onClick: () => window.print() }]

const { alert, showSuccess, showError } = useAlert()
const loading = ref(false)
const saving = ref(false)
const periodDuration = ref(50)
const startTime = ref('08:00')
const showPeriodSettings = ref(false)
const daySettings = ref({
  monday: { duration: 45, startTime: '08:00' },
  tuesday: { duration: 45, startTime: '08:00' },
  wednesday: { duration: 45, startTime: '08:00' },
  thursday: { duration: 45, startTime: '08:00' },
  friday: { duration: 30, startTime: '08:00' },
  saturday: { duration: 45, startTime: '08:00' }
})
const timeSlots = ref([])
const schedule = ref([])
const subjects = ref([])
const teachers = ref([])
const programs = ref([])
const programSemesters = ref([])
const filteredSemesters = ref([])
const filterProgram = ref('')
const filterSemester = ref('')
const showModal = ref(false)
const showAddMultipleModal = ref(false)
const editingSchedule = ref(null)
const showConfirmDialog = ref(false)
const scheduleToDelete = ref(null)
const scheduleForm = ref({ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true })
const multipleScheduleForms = ref([{ day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true, availableSemesters: [] }])

const calculateEndTime = (start, duration) => {
  const [hours, minutes] = start.split(':').map(Number)
  const total = hours * 60 + minutes + duration
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
}

const onStartTimeChange = () => {
  if (scheduleForm.value.start_time && scheduleForm.value.day) {
    const daySetting = daySettings.value[scheduleForm.value.day]
    scheduleForm.value.end_time = calculateEndTime(scheduleForm.value.start_time, daySetting?.duration || periodDuration.value)
  }
}

const applyDaySettings = () => {
  showPeriodSettings.value = false
  generateTimeSlots()
  showSuccess('Day settings applied')
}

const generateTimeSlots = () => {
  const slots = []
  const [startHour, startMin] = startTime.value.split(':').map(Number)
  let currentMinutes = startHour * 60 + startMin
  for (let i = 0; i < 8; i++) {
    const startH = Math.floor(currentMinutes / 60), startM = currentMinutes % 60
    const endMinutes = currentMinutes + periodDuration.value
    const endH = Math.floor(endMinutes / 60), endM = endMinutes % 60
    slots.push(`${String(startH).padStart(2, '0')}:${String(startM).padStart(2, '0')}-${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`)
    currentMinutes = endMinutes
  }
  timeSlots.value = slots
}

const getSchedule = (day, time) => {
  const [start] = time.split('-')
  return schedule.value.find(s => s.day === day.toLowerCase() && s.start_time?.startsWith(start))
}

const addSchedule = (day, time) => {
  const [start, end] = time.split('-')
  editingSchedule.value = null
  scheduleForm.value = { day: day.toLowerCase(), start_time: start + ':00', end_time: end + ':00', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true }
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
    const list = (response.results || response).filter(s => s.is_active === undefined || s.is_active)
    if (target === 'form') programSemesters.value = list
    else filteredSemesters.value = list
  } catch (error) { console.error('Error loading semesters:', error) }
}

const onProgramChange = async () => {
  scheduleForm.value.semester = ''
  if (scheduleForm.value.program) await loadSemestersByProgram(scheduleForm.value.program, 'form')
  else programSemesters.value = []
}

const onMultipleProgramChange = async (index) => {
  const form = multipleScheduleForms.value[index]
  form.semester = ''
  if (form.program) {
    try {
      const response = await programService.getProgramSemesters(form.program)
      form.availableSemesters = (response.results || response).filter(s => s.is_active === undefined || s.is_active)
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

const saveSchedule = async () => {
  saving.value = true
  try {
    if (editingSchedule.value) await timetableService.update(editingSchedule.value.id, scheduleForm.value)
    else await timetableService.create(scheduleForm.value)
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
    showSuccess(`${multipleScheduleForms.value.length} schedules added`)
    closeMultipleModal()
    loadSchedule()
  } catch (error) {
    showError(error.response?.data?.error || 'Failed to save')
  } finally { saving.value = false }
}

onMounted(() => { generateTimeSlots(); loadSchedule(); loadDropdowns() })
</script>


