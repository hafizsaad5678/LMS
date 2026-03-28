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
                <select v-model="form.subject" class="form-select" required>
                  <option value="">Select Subject</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.code }} - {{ subject.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Teacher <span class="text-danger">*</span></label>
                <select v-model="form.teacher" class="form-select" required>
                  <option value="">Select Teacher</option>
                  <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                    {{ teacher.full_name }} - {{ teacher.employee_id }}
                  </option>
                </select>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Room <span class="text-danger">*</span></label>
                <input v-model="form.room" type="text" class="form-control" placeholder="e.g., Room 101" required>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Program</label>
                <select v-model="form.program" class="form-select" @change="$emit('program-change')">
                  <option value="">Select Program (Optional)</option>
                  <option v-for="program in programs" :key="program.id" :value="program.id">{{ program.name }}</option>
                </select>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Semester</label>
                <select v-model="form.semester" class="form-select" :disabled="!form.program">
                  <option value="">Select Semester (Optional)</option>
                  <option v-for="semester in semesters" :key="semester.id" :value="semester.id">
                    Semester {{ semester.number }} - {{ semester.name }}
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
import { DAYS_OF_WEEK, DAY_LABELS } from '@/utils/constants/config'

defineProps({
  show: { type: Boolean, default: false },
  form: { type: Object, required: true },
  isEdit: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  subjects: { type: Array, default: () => [] },
  teachers: { type: Array, default: () => [] },
  programs: { type: Array, default: () => [] },
  semesters: { type: Array, default: () => [] },
  days: { type: Array, default: () => DAYS_OF_WEEK },
  dayLabels: { type: Array, default: () => DAY_LABELS }
})

defineEmits(['close', 'save', 'time-change', 'program-change'])
</script>
