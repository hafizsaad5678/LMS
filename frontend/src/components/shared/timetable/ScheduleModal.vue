<template>
  <div v-if="show" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header bg-admin text-white">
          <h5 class="modal-title">
            <i class="bi bi-calendar-plus me-2"></i>
            {{ isEdit ? 'Edit Class Schedule' : 'Add Class Schedule' }}
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="$emit('save')">
            <AlertMessage
              v-if="showTeacherUnavailableAlert"
              type="warning"
              title="Teacher Unavailable"
              :message="teacherUnavailableAlertMessage"
              :auto-close="false"
              @close="dismissTeacherAlert"
            />

            <!-- Day and Time Selection -->
            <div class="row mb-3">
              <div class="col-md-4">
                <label class="form-label">Day <span class="text-danger">*</span></label>
                <select v-model="form.day" class="form-select" required @change="$emit('time-change')">
                  <option value="">Select Day</option>
                  <option v-for="(day, index) in days" :key="day" :value="day">{{ dayLabels[index] }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Start Time <span class="text-danger">*</span></label>
                <input v-model="form.start_time" type="time" class="form-control" required @change="$emit('time-change')">
                <small class="text-muted">End time will auto-calculate</small>
              </div>
              <div class="col-md-4">
                <label class="form-label">End Time <span class="text-danger">*</span></label>
                <input v-model="form.end_time" type="time" class="form-control" required>
                <small class="text-muted">You can adjust manually</small>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Subject <span class="text-danger">*</span></label>
                <select v-model="form.subject" class="form-select" :disabled="!form.semester" required>
                  <option value="">{{ form.semester ? 'Select Subject' : 'Select Semester First' }}</option>
                  <option v-for="subject in filteredSubjects" :key="subject.id" :value="subject.id">
                    {{ subject.code }} - {{ subject.name }}
                  </option>
                </select>
                <small v-if="!form.semester" class="text-muted">Select a semester first</small>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Teacher <span class="text-danger">*</span></label>
                <select v-model="form.teacher" class="form-select" required>
                  <option value="">Select Teacher</option>
                  <option
                    v-for="teacher in teachers"
                    :key="teacher.id"
                    :value="teacher.id"
                    :disabled="isTeacherUnavailable(teacher.id)"
                  >
                    {{ teacher.full_name }} - {{ teacher.employee_id }}
                  </option>
                </select>
                <small v-if="unavailableTeacherIds.length" class="text-muted">Busy teachers are disabled for the selected day and time.</small>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Room <span class="text-danger">*</span></label>
                <input v-model="form.room" type="text" class="form-control" placeholder="e.g., Room 101" required>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Program <span class="text-danger">*</span></label>
                <select v-model="form.program" class="form-select" required @change="$emit('program-change')">
                  <option value="">Select Program</option>
                  <option v-for="program in programs" :key="program.id" :value="program.id">{{ program.name }}</option>
                </select>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Semester <span class="text-danger">*</span></label>
                <select v-model="form.semester" class="form-select" :disabled="!form.program" required>
                  <option value="">Select Semester</option>
                  <option v-for="semester in semesters" :key="semester.id" :value="semester.id">
                    {{ formatSemesterLabel(semester) }}
                  </option>
                </select>
                <small v-if="!form.program" class="text-muted">Select a program first</small>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Status</label>
                <div class="form-check form-switch mt-2">
                  <input v-model="form.is_active" class="form-check-input" type="checkbox" id="activeSwitch">
                  <label class="form-check-label" for="activeSwitch">{{ form.is_active ? 'Active' : 'Inactive' }}</label>
                </div>
              </div>
            </div>

            <div class="d-flex gap-2 justify-content-end">
              <button type="button" @click="$emit('close')" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-admin-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                {{ isEdit ? 'Update' : 'Add' }} Schedule
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { AlertMessage } from '@/components/shared/common'
import { DAYS_OF_WEEK, DAY_LABELS } from '@/utils/constants/config'

const extractSemesterId = (subject) => {
  const raw = subject?.semester_id ?? subject?.semester ?? subject?.semesterId
  if (raw && typeof raw === 'object') return raw.id ?? raw.pk ?? ''
  return raw ?? ''
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

const props = defineProps({
  show: { type: Boolean, default: false },
  form: { type: Object, required: true },
  isEdit: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  subjects: { type: Array, default: () => [] },
  teachers: { type: Array, default: () => [] },
  unavailableTeacherIds: { type: Array, default: () => [] },
  unavailableTeacherConflicts: { type: Object, default: () => ({}) },
  programs: { type: Array, default: () => [] },
  semesters: { type: Array, default: () => [] },
  days: { type: Array, default: () => DAYS_OF_WEEK },
  dayLabels: { type: Array, default: () => DAY_LABELS }
})

const isTeacherUnavailable = (teacherId) => props.unavailableTeacherIds.includes(String(teacherId)) || props.unavailableTeacherIds.includes(Number(teacherId))

const filteredSubjects = computed(() => {
  const selectedSemesterId = String(props.form?.semester || '')
  if (!selectedSemesterId) return []
  return props.subjects.filter(subject => String(extractSemesterId(subject)) === selectedSemesterId)
})

const dismissedTeacherAlert = ref(false)

const selectedTeacherConflictTimes = computed(() => {
  const teacherKey = String(props.form?.teacher || '')
  if (!teacherKey) return []
  return props.unavailableTeacherConflicts[teacherKey] || []
})

const teacherUnavailableAlertMessage = computed(() => {
  if (!selectedTeacherConflictTimes.value.length) return ''
  return `Selected teacher is unavailable at this time. Existing lecture time(s): ${selectedTeacherConflictTimes.value.join(', ')}`
})

const showTeacherUnavailableAlert = computed(() => selectedTeacherConflictTimes.value.length > 0 && !dismissedTeacherAlert.value)

const dismissTeacherAlert = () => {
  dismissedTeacherAlert.value = true
}

watch(
  () => `${props.form?.day || ''}|${props.form?.start_time || ''}|${props.form?.end_time || ''}|${props.form?.teacher || ''}`,
  () => {
    dismissedTeacherAlert.value = false
  }
)

watch(
  () => props.form?.semester,
  () => {
    props.form.subject = ''
  }
)

defineEmits(['close', 'save', 'time-change', 'program-change'])
</script>
