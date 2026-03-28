<template>
  <div v-if="show" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050; overflow-y: auto;">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header bg-admin text-white">
          <h5 class="modal-title"><i class="bi bi-calendar-plus me-2"></i>Add Multiple Class Schedules</h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>Add multiple class schedules at once. Click "Add Row" to add more classes.
          </div>

          <div v-for="(form, index) in forms" :key="index" class="card mb-3">
            <div class="card-header bg-light d-flex justify-content-between align-items-center">
              <span class="fw-semibold">Class {{ index + 1 }}</span>
              <button v-if="forms.length > 1" @click="$emit('remove', index)" class="btn btn-sm btn-outline-danger">
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
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.code }} - {{ subject.name }}</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label small">Teacher <span class="text-danger">*</span></label>
                  <select v-model="form.teacher" class="form-select form-select-sm" required>
                    <option value="">Select Teacher</option>
                    <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">{{ teacher.full_name }}</option>
                  </select>
                </div>
                <div class="col-md-2">
                  <label class="form-label small">Room <span class="text-danger">*</span></label>
                  <input v-model="form.room" type="text" class="form-control form-control-sm" placeholder="101" required>
                </div>
                <div class="col-md-3">
                  <label class="form-label small">Program</label>
                  <select v-model="form.program" class="form-select form-select-sm" @change="$emit('program-change', index)">
                    <option value="">Select</option>
                    <option v-for="program in programs" :key="program.id" :value="program.id">{{ program.name }}</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label small">Semester</label>
                  <select v-model="form.semester" class="form-select form-select-sm" :disabled="!form.program">
                    <option value="">Select</option>
                    <option v-for="semester in form.availableSemesters || []" :key="semester.id" :value="semester.id">Sem {{ semester.number }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <button @click="$emit('add')" class="btn btn-outline-admin w-100">
            <i class="bi bi-plus-circle me-2"></i>Add Another Class
          </button>
        </div>
        <div class="modal-footer">
          <button type="button" @click="$emit('close')" class="btn btn-secondary">Cancel</button>
          <button type="button" @click="$emit('save')" class="btn btn-admin-primary" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            Save All Schedules
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { DAYS_OF_WEEK, DAY_LABELS } from '@/utils/constants/config'

defineProps({
  show: { type: Boolean, default: false },
  forms: { type: Array, required: true },
  saving: { type: Boolean, default: false },
  subjects: { type: Array, default: () => [] },
  teachers: { type: Array, default: () => [] },
  programs: { type: Array, default: () => [] },
  days: { type: Array, default: () => DAYS_OF_WEEK },
  dayLabels: { type: Array, default: () => DAY_LABELS }
})

defineEmits(['close', 'save', 'add', 'remove', 'program-change'])
</script>
