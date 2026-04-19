<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <h5 class="card-title fw-bold text-dark mb-4">
        <i class="bi bi-bar-chart me-2 text-teacher"></i>Grade Distribution
      </h5>
      <div class="small text-muted mb-3">Passing criteria: <span class="fw-semibold text-success">40% and above</span> | <span class="fw-semibold text-danger">Below 40% = F</span></div>
      <div v-if="distribution.length > 0" class="d-flex flex-column gap-3">
        <div v-for="grade in distribution" :key="grade.grade" class="grade-bar-item">
          <div class="d-flex justify-content-between mb-2">
            <span class="fw-semibold text-dark">
              {{ grade.grade }}
              <small v-if="grade.grade === 'F'" class="text-danger ms-1">(Below 40%)</small>
              <small v-else-if="grade.grade === 'Pending'" class="text-warning ms-1">(Not graded yet)</small>
            </span>
            <span class="text-muted">{{ grade.count }} students ({{ grade.percentage }}%)</span>
          </div>
          <div class="progress progress-h-12">
            <div 
              class="progress-bar" 
              :class="getBarClass(grade.grade)"
              :style="{ width: `${grade.percentage}%` }"
              role="progressbar"
            ></div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-5">
        <i class="bi bi-bar-chart display-4 text-muted"></i>
        <p class="text-muted mt-3">No grade data available</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useGradeManagement } from '@/composables/teacher/useGradeManagement'

defineProps({
  distribution: {
    type: Array,
    default: () => []
  }
})

const { getGradeColor } = useGradeManagement()

const getBarClass = (grade) => {
  if (grade === 'Pending') return 'bg-warning'
  return getGradeColor(grade)
}
</script>
