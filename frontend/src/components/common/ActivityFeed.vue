<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <h5 class="card-title fw-semibold text-dark mb-4">Recent Activities</h5>
      <div class="activity-feed">
        <div v-for="activity in activities" :key="activity.id" class="d-flex gap-3 mb-3">
          <div class="flex-shrink-0">
            <div class="rounded-circle bg-primary" style="width: 8px; height: 8px; margin-top: 6px;"></div>
          </div>
          <div class="flex-grow-1 min-w-0">
            <p class="text-dark mb-1">{{ activity.message }}</p>
            <p class="small text-muted mb-0">{{ activity.time }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  activities: {
    type: Array,
    default: () => []
  }
});
</script>


