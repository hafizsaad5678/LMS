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
                <div class="small text-muted">{{ student.student_enrollment }}</div>
              </div>
            </div>
          </td>
          <td class="text-center">
            <div class="marks-input-wrapper mx-auto">
              <input 
                type="number" 
                class="form-control form-control-marks" 
                v-model.number="student.marks_obtained"
                :max="maxMarks"
                min="0"
                step="0.5"
                @input="student.is_dirty = true"
                :disabled="student.is_locked"
              >
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
                type="text" 
                class="form-control form-control-remarks px-0" 
                placeholder="Add feedback..."
                v-model="student.remarks"
                @input="student.is_dirty = true"
                :disabled="student.is_locked"
              >
              <i v-if="student.remarks" class="bi bi-chat-text-fill icon-hint"></i>
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

const getGradeColor = (marks) => {
  const percentage = (marks / props.maxMarks) * 100
  if (percentage >= 80) return 'bg-success'
  if (percentage >= 50) return 'bg-warning text-dark'
  return 'bg-danger'
}
</script>
