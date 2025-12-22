<template>
  <AdminPageTemplate title="Class Timetable" subtitle="Manage class schedules and timetables" icon="bi bi-calendar-week" :breadcrumbs="breadcrumbs" :actions="actions">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <!-- Filter Section -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label fw-semibold">Filter by Program</label>
            <select v-model="filterProgram" class="form-select" @change="onFilterProgramChange">
              <option value="">All Programs</option>
              <option v-for="program in programs" :key="program.id" :value="program.id">
                {{ program.name }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-semibold">Filter by Semester</label>
            <select v-model="filterSemester" class="form-select" @change="loadSchedule" :disabled="!filterProgram">
              <option value="">All Semesters</option>
              <option v-for="semester in filteredSemesters" :key="semester.id" :value="semester.id">
                Semester {{ semester.number }} - {{ semester.name }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <button @click="clearFilters" class="btn btn-outline-secondary w-100">
              <i class="bi bi-x-circle me-2"></i>Clear Filters
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Weekly Timetable -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom">
        <h5 class="card-title mb-0 fw-semibold">
          <i class="bi bi-calendar-week me-2 text-admin"></i>Weekly Schedule
        </h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-bordered mb-0 timetable">
            <thead class="bg-light">
              <tr>
                <th style="width: 100px;">Time</th>
                <th v-for="(day, index) in days" :key="day">{{ dayLabels[index] }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="slot in timeSlots" :key="slot">
                <td class="fw-semibold text-center">{{ slot }}</td>
                <td v-for="day in days" :key="day" class="schedule-cell" @click="addSchedule(day, slot)">
                  <div v-if="getSchedule(day, slot)" class="schedule-item">
                    <div class="fw-semibold">{{ getSchedule(day, slot).subject_name || 'Unknown' }}</div>
                    <small class="text-muted">{{ getSchedule(day, slot).teacher_name || '' }}</small>
                    <small class="d-block text-muted">{{ getSchedule(day, slot).room }}</small>
                  </div>
                  <div v-else class="text-muted small text-center">+</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <!-- Pagination -->
      <div class="card-footer bg-white border-top">
        <div class="d-flex justify-content-between align-items-center">
          <div class="text-muted small">
            Showing {{ schedule.length }} schedule(s)
            <span v-if="filterProgram || filterSemester" class="badge bg-info ms-2">Filtered</span>
          </div>
          <div class="d-flex gap-2">
            <button @click="loadSchedule" class="btn btn-sm btn-outline-secondary">
              <i class="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
            <button @click="showAddMultipleModal = true" class="btn btn-sm btn-admin-primary">
              <i class="bi bi-plus-circle me-1"></i>Add Multiple Classes
            </button>
          </div>
        </div>
      </div>
    </div>

  </AdminPageTemplate>

  <!-- Modals teleported to body for proper overlay -->
  <Teleport to="body">
    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-admin text-white">
            <h5 class="modal-title">
              <i class="bi bi-calendar-plus me-2"></i>
              {{ editingSchedule ? 'Edit Class Schedule' : 'Add Class Schedule' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSchedule">
              <!-- Day and Time Selection -->
              <div class="row mb-3">
                <div class="col-md-4">
                  <label class="form-label">Day <span class="text-danger">*</span></label>
                  <select v-model="scheduleForm.day" class="form-select" required>
                    <option value="">Select Day</option>
                    <option v-for="(day, index) in days" :key="day" :value="day">
                      {{ dayLabels[index] }}
                    </option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Start Time <span class="text-danger">*</span></label>
                  <input v-model="scheduleForm.start_time" type="time" class="form-control" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label">End Time <span class="text-danger">*</span></label>
                  <input v-model="scheduleForm.end_time" type="time" class="form-control" required>
                </div>
              </div>

              <div class="row">
                <!-- Subject Selection -->
                <div class="col-md-6 mb-3">
                  <label class="form-label">Subject <span class="text-danger">*</span></label>
                  <select v-model="scheduleForm.subject" class="form-select" required @change="onSubjectChange">
                    <option value="">Select Subject</option>
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                      {{ subject.code }} - {{ subject.name }}
                    </option>
                  </select>
                </div>

                <!-- Teacher Selection -->
                <div class="col-md-6 mb-3">
                  <label class="form-label">Teacher <span class="text-danger">*</span></label>
                  <select v-model="scheduleForm.teacher" class="form-select" required>
                    <option value="">Select Teacher</option>
                    <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                      {{ teacher.full_name }} - {{ teacher.employee_id }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="row">
                <!-- Room -->
                <div class="col-md-6 mb-3">
                  <label class="form-label">Room <span class="text-danger">*</span></label>
                  <input v-model="scheduleForm.room" type="text" class="form-control" placeholder="e.g., Room 101" required>
                </div>

                <!-- Program Selection -->
                <div class="col-md-6 mb-3">
                  <label class="form-label">Program</label>
                  <select v-model="scheduleForm.program" class="form-select" @change="onProgramChange">
                    <option value="">Select Program (Optional)</option>
                    <option v-for="program in programs" :key="program.id" :value="program.id">
                      {{ program.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="row">
                <!-- Semester Selection -->
                <div class="col-md-6 mb-3">
                  <label class="form-label">Semester</label>
                  <select v-model="scheduleForm.semester" class="form-select" :disabled="!scheduleForm.program">
                    <option value="">Select Semester (Optional)</option>
                    <option v-for="semester in programSemesters" :key="semester.id" :value="semester.id">
                      Semester {{ semester.number }} - {{ semester.name }}
                    </option>
                  </select>
                  <small v-if="!scheduleForm.program" class="text-muted">Select a program first</small>
                </div>

                <!-- Active Status -->
                <div class="col-md-6 mb-3">
                  <label class="form-label">Status</label>
                  <div class="form-check form-switch mt-2">
                    <input v-model="scheduleForm.is_active" class="form-check-input" type="checkbox" id="activeSwitch">
                    <label class="form-check-label" for="activeSwitch">
                      {{ scheduleForm.is_active ? 'Active' : 'Inactive' }}
                    </label>
                  </div>
                </div>
              </div>

              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editingSchedule ? 'Update' : 'Add' }} Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Multiple Classes Modal -->
    <div v-if="showAddMultipleModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050; overflow-y: auto;">
      <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header bg-admin text-white">
            <h5 class="modal-title">
              <i class="bi bi-calendar-plus me-2"></i>Add Multiple Class Schedules
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeMultipleModal"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              Add multiple class schedules at once. Click "Add Row" to add more classes.
            </div>

            <!-- Multiple Schedule Forms -->
            <div v-for="(form, index) in multipleScheduleForms" :key="index" class="card mb-3">
              <div class="card-header bg-light d-flex justify-content-between align-items-center">
                <span class="fw-semibold">Class {{ index + 1 }}</span>
                <button v-if="multipleScheduleForms.length > 1" @click="removeScheduleForm(index)" class="btn btn-sm btn-outline-danger">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
              <div class="card-body">
                <div class="row g-3">
                  <div class="col-md-3">
                    <label class="form-label small">Day <span class="text-danger">*</span></label>
                    <select v-model="form.day" class="form-select form-select-sm" required>
                      <option value="">Select</option>
                      <option v-for="(day, idx) in days" :key="day" :value="day">{{ dayLabels[idx] }}</option>
                    </select>
                  </div>
                  <div class="col-md-2">
                    <label class="form-label small">Start <span class="text-danger">*</span></label>
                    <input v-model="form.start_time" type="time" class="form-control form-control-sm" required>
                  </div>
                  <div class="col-md-2">
                    <label class="form-label small">End <span class="text-danger">*</span></label>
                    <input v-model="form.end_time" type="time" class="form-control form-control-sm" required>
                  </div>
                  <div class="col-md-5">
                    <label class="form-label small">Subject <span class="text-danger">*</span></label>
                    <select v-model="form.subject" class="form-select form-select-sm" required>
                      <option value="">Select Subject</option>
                      <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                        {{ subject.code }} - {{ subject.name }}
                      </option>
                    </select>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">Teacher <span class="text-danger">*</span></label>
                    <select v-model="form.teacher" class="form-select form-select-sm" required>
                      <option value="">Select Teacher</option>
                      <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                        {{ teacher.full_name }}
                      </option>
                    </select>
                  </div>
                  <div class="col-md-2">
                    <label class="form-label small">Room <span class="text-danger">*</span></label>
                    <input v-model="form.room" type="text" class="form-control form-control-sm" placeholder="101" required>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label small">Program</label>
                    <select v-model="form.program" class="form-select form-select-sm" @change="onMultipleProgramChange(index)">
                      <option value="">Select</option>
                      <option v-for="program in programs" :key="program.id" :value="program.id">
                        {{ program.name }}
                      </option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label small">Semester</label>
                    <select v-model="form.semester" class="form-select form-select-sm" :disabled="!form.program">
                      <option value="">Select</option>
                      <option v-for="semester in form.availableSemesters || []" :key="semester.id" :value="semester.id">
                        Sem {{ semester.number }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <button @click="addScheduleForm" class="btn btn-outline-admin w-100">
              <i class="bi bi-plus-circle me-2"></i>Add Another Class
            </button>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeMultipleModal" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="saveMultipleSchedules" class="btn btn-admin-primary" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              Save All Schedules
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { timetableService } from '@/services/managementService'
import { subjectService } from '@/services/subjectService'
import { teacherService } from '@/services/teacherService'
import { programService } from '@/services/programService'
import { semesterService } from '@/services/semesterService'
import cacheService from '@/services/cacheService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Timetable' }]
const actions = [{ label: 'Print', icon: 'bi bi-printer', variant: 'btn-admin-outline', onClick: () => window.print() }]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(false)
const saving = ref(false)
const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
const dayLabels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const timeSlots = ['08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00', '14:00-15:00', '15:00-16:00']
const schedule = ref([])
const subjects = ref([])
const teachers = ref([])
const programs = ref([])
const semesters = ref([])
const programSemesters = ref([])
const filteredSemesters = ref([])
const filterProgram = ref('')
const filterSemester = ref('')
const showModal = ref(false)
const showAddMultipleModal = ref(false)
const editingSchedule = ref(null)
const scheduleForm = ref({ 
  day: '', 
  start_time: '', 
  end_time: '', 
  subject: '', 
  teacher: '', 
  room: '',
  program: '',
  semester: '',
  is_active: true
})
const multipleScheduleForms = ref([
  { day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true, availableSemesters: [] }
])

const getDayLabel = (day) => {
  const index = days.indexOf(day)
  return index !== -1 ? dayLabels[index] : day
}

const getSchedule = (day, time) => {
  const [start] = time.split('-')
  return schedule.value.find(s => s.day === day.toLowerCase() && s.start_time?.startsWith(start))
}

const addSchedule = (day, time) => {
  const [start, end] = time.split('-')
  editingSchedule.value = null
  scheduleForm.value = { 
    day: day.toLowerCase(), 
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

const loadSchedule = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterProgram.value) params.program = filterProgram.value
    if (filterSemester.value) params.semester = filterSemester.value
    
    const response = await timetableService.getAll(params)
    schedule.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading timetable:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to load timetable' }
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  filterProgram.value = ''
  filterSemester.value = ''
  filteredSemesters.value = []
  loadSchedule()
}

const onFilterProgramChange = async () => {
  filterSemester.value = ''
  if (filterProgram.value) {
    await loadSemestersByProgram(filterProgram.value, 'filter')
  } else {
    filteredSemesters.value = []
  }
  loadSchedule()
}

const loadSemestersByProgram = async (programId, target = 'form') => {
  try {
    const response = await programService.getProgramSemesters(programId)
    const semestersList = response.results || response
    
    if (target === 'form') {
      programSemesters.value = semestersList
    } else if (target === 'filter') {
      filteredSemesters.value = semestersList
    }
  } catch (error) {
    console.error('Error loading semesters for program:', error)
  }
}

const onProgramChange = async () => {
  scheduleForm.value.semester = ''
  if (scheduleForm.value.program) {
    await loadSemestersByProgram(scheduleForm.value.program, 'form')
  } else {
    programSemesters.value = []
  }
}

const onMultipleProgramChange = async (index) => {
  const form = multipleScheduleForms.value[index]
  form.semester = ''
  if (form.program) {
    try {
      const response = await programService.getProgramSemesters(form.program)
      form.availableSemesters = response.results || response
    } catch (error) {
      console.error('Error loading semesters:', error)
      form.availableSemesters = []
    }
  } else {
    form.availableSemesters = []
  }
}

const loadSubjects = async () => {
  try {
    // Check cache first
    const cached = cacheService.get('subjects_list')
    if (cached) {
      subjects.value = cached
      return
    }
    
    const response = await subjectService.getAllSubjects()
    const result = response.results || response
    
    // Store in cache
    cacheService.set('subjects_list', result)
    subjects.value = result
  } catch (error) {
    console.error('Error loading subjects:', error)
  }
}

const loadTeachers = async () => {
  try {
    // Check cache first
    const cached = cacheService.get('teachers_list')
    if (cached) {
      teachers.value = cached
      return
    }
    
    const response = await teacherService.getAllTeachers()
    const result = response.results || response
    
    // Store in cache
    cacheService.set('teachers_list', result)
    teachers.value = result
  } catch (error) {
    console.error('Error loading teachers:', error)
  }
}

const loadPrograms = async () => {
  try {
    // Check cache first
    const cached = cacheService.get('programs_list')
    if (cached) {
      programs.value = cached
      return
    }
    
    const response = await programService.getAllPrograms()
    const result = response.results || response
    
    // Store in cache
    cacheService.set('programs_list', result)
    programs.value = result
  } catch (error) {
    console.error('Error loading programs:', error)
  }
}

const loadSemesters = async () => {
  try {
    // Check cache first
    const cached = cacheService.get('semesters_list')
    if (cached) {
      semesters.value = cached
      return
    }
    
    const response = await semesterService.getAllSemesters()
    const result = response.results || response
    
    // Store in cache
    cacheService.set('semesters_list', result)
    semesters.value = result
  } catch (error) {
    console.error('Error loading semesters:', error)
  }
}

const onSubjectChange = () => {
  // Optional: Auto-select teacher if subject has assigned teacher
  // This can be implemented if needed
}

const saveSchedule = async () => {
  saving.value = true
  try {
    if (editingSchedule.value) {
      await timetableService.update(editingSchedule.value.id, scheduleForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Schedule updated successfully' }
    } else {
      await timetableService.create(scheduleForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Schedule added successfully' }
    }
    closeModal()
    loadSchedule()
  } catch (error) {
    console.error('Error saving schedule:', error)
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Failed to save schedule'
    alert.value = { show: true, type: 'danger', title: 'Error', message: errorMsg }
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  editingSchedule.value = null
  scheduleForm.value = { 
    day: '', 
    start_time: '', 
    end_time: '', 
    subject: '', 
    teacher: '', 
    room: '',
    program: '',
    semester: '',
    is_active: true
  }
  programSemesters.value = []
}

const addScheduleForm = () => {
  multipleScheduleForms.value.push({
    day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', 
    program: '', semester: '', is_active: true, availableSemesters: []
  })
}

const removeScheduleForm = (index) => {
  multipleScheduleForms.value.splice(index, 1)
}

const closeMultipleModal = () => {
  showAddMultipleModal.value = false
  multipleScheduleForms.value = [
    { day: '', start_time: '', end_time: '', subject: '', teacher: '', room: '', program: '', semester: '', is_active: true, availableSemesters: [] }
  ]
}

const saveMultipleSchedules = async () => {
  saving.value = true
  try {
    const promises = multipleScheduleForms.value.map(form => {
      const { availableSemesters, ...formData } = form
      return timetableService.create(formData)
    })
    
    await Promise.all(promises)
    alert.value = { show: true, type: 'success', title: 'Success', message: `${multipleScheduleForms.value.length} schedules added successfully` }
    closeMultipleModal()
    loadSchedule()
  } catch (error) {
    console.error('Error saving schedules:', error)
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Failed to save schedules'
    alert.value = { show: true, type: 'danger', title: 'Error', message: errorMsg }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSchedule()
  loadSubjects()
  loadTeachers()
  loadPrograms()
  loadSemesters()
})
</script>


