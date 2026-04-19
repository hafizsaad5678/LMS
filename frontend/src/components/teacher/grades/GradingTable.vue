<template>
  <div class="table-responsive">
    <table class="table table-hover align-middle custom-grading-table">
      <thead>
        <tr>
          <th class="ps-0 border-0 text-muted small fw-bold">STUDENT</th>
          <th class="border-0 text-muted small fw-bold text-center table-col-w-140">MARKS</th>
          <th class="border-0 text-muted small fw-bold text-center table-col-w-80">%</th>
          <th class="border-0 text-muted small fw-bold">REMARKS</th>
          <th class="pe-0 border-0 text-muted small fw-bold text-center table-col-w-100">STATUS</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in marksData" :key="student.student" :class="{ 'row-dirty': student.is_dirty }">
          <td class="ps-0 py-3">
            <div class="d-flex align-items-center">
              <div class="avatar-cell me-3">{{ student.student_name.charAt(0) }}</div>
              <div>
                <div class="fw-bold text-dark">{{ student.student_name }}</div>
                <div class="d-flex align-items-center gap-2 mt-1">
                  <span class="small text-muted">{{ student.student_enrollment }}</span>
                  <span v-if="student.marks_obtained != null" class="badge bg-light text-primary extra-small border-primary-subtle pt-1">
                    Score: {{ student.marks_obtained }} / {{ maxMarks }}
                  </span>
                </div>
              </div>
            </div>
          </td>
          <td class="text-center">
            <div class="d-flex justify-content-center">
              <input 
                type="number" 
                class="form-control form-control-marks" 
                v-model.number="student.marks_obtained"
                :class="{ 'is-invalid-input': student.marks_obtained > maxMarks }"
                :max="maxMarks"
                min="0"
                step="0.5"
                @input="handleInput(student)"
                :disabled="student.is_locked"
              >
            </div>
            <div v-if="student.marks_obtained > maxMarks" class="text-danger extra-small mt-1 fw-bold">
              Max is {{ maxMarks }}
            </div>
          </td>
          <td class="text-center">
            <span v-if="student.marks_obtained != null" 
                  class="badge rounded-pill px-3" 
                  :class="`grade-badge-${getGradeColor(student.marks_obtained)}`">
              {{ Math.round((student.marks_obtained / maxMarks) * 100) }}%
            </span>
            <span v-else class="text-muted small">-</span>
          </td>
          <td>
            <div class="remarks-input-wrapper">
              <input 
                v-if="!student.is_locked"
                type="text" 
                class="form-control form-control-remarks" 
                placeholder="Add feedback..."
                v-model="student.remarks"
                @input="student.is_dirty = true"
              >
              <div v-else class="form-control form-control-remarks bg-light text-muted border-0 d-flex align-items-center" v-html="student.remarks || 'No feedback'"></div>
            </div>
          </td>
          <td class="pe-0 text-center">
            <button 
              @click="student.is_locked = !student.is_locked; student.is_dirty = true"
              class="btn btn-sm rounded-circle lock-btn"
              :class="student.is_locked ? 'btn-soft-danger' : 'btn-soft-success'"
              :title="student.is_locked ? 'Click to Unlock for editing' : 'Click to Lock grade'"
            >
              <i class="bi" :class="student.is_locked ? 'bi-lock-fill' : 'bi-unlock'"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  marksData: {
    type: Array,
    required: true
  },
  maxMarks: {
    type: Number,
    required: true
  }
})

const handleInput = (student) => {
  student.is_dirty = true
  if (student.marks_obtained > props.maxMarks) {
    // Optional: Auto-correct to max or just leave for validation
    // student.marks_obtained = props.maxMarks
  }
}

const getGradeColor = (marks) => {
  const percentage = (marks / props.maxMarks) * 100
  if (percentage > 100) return 'danger'
  if (percentage >= 80) return 'success'
  if (percentage >= 50) return 'warning'
  return 'danger'
}
</script>
