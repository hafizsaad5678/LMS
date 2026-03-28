<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <h5 class="card-title fw-bold text-dark mb-4">
        <i class="bi bi-bar-chart me-2 text-teacher"></i>Grade Distribution
      </h5>
      <div v-if="distribution.length > 0" class="d-flex flex-column gap-3">
        <div v-for="grade in distribution" :key="grade.grade" class="grade-bar-item">
          <div class="d-flex justify-content-between mb-2">
            <span class="fw-semibold text-dark">{{ grade.grade }}</span>
            <span class="text-muted">{{ grade.count }} students ({{ grade.percentage }}%)</span>
          </div>
          <div class="progress progress-h-12">
            <div 
              class="progress-bar" 
              :class="getGradeColor(grade.grade)"
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
</script>
