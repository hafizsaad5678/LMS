<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <h5 class="card-title fw-bold text-dark mb-4">
        <i class="bi bi-trophy me-2 text-warning"></i>Top Performers
      </h5>
      <div v-if="performers.length > 0" class="d-flex flex-column gap-3">
        <div 
          v-for="(student, index) in performers" 
          :key="student.id" 
          class="d-flex align-items-center p-2 rounded hover-bg-light"
        >
          <div class="rank-badge me-3">{{ index + 1 }}</div>
          <div class="flex-grow-1">
            <div class="fw-bold text-dark">{{ student.name || 'Unknown Student' }}</div>
            <small v-if="student.roll_no" class="text-muted">{{ student.roll_no }}</small>
          </div>
          <div class="text-end">
            <div class="fw-bold text-success">{{ student.average }}%</div>
            <small class="text-muted">{{ student.grade }}</small>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-4">
        <i class="bi bi-trophy display-4 text-muted"></i>
        <p class="text-muted mt-2 mb-0">No data available</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  performers: {
    type: Array,
    default: () => []
  }
})
</script>
