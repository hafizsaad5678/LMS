<template>
  <div class="card border-0 shadow-sm h-100">
    <div class="card-body">
      <h5 class="card-title fw-semibold text-dark mb-4">Recent Activities</h5>
      
      <!-- Loading State -->
      <div v-if="loading" class="activity-feed">
        <div v-for="i in 4" :key="i" class="d-flex gap-3 mb-3">
          <div class="flex-shrink-0">
            <div class="skeleton-activity-dot rounded-circle bg-secondary bg-opacity-25"></div>
          </div>
          <div class="flex-grow-1">
            <div class="skeleton-activity-text bg-secondary bg-opacity-10 rounded mb-2" :class="`w-${70 + (i * 5)}`"></div>
            <div class="skeleton-activity-text-sm bg-secondary bg-opacity-10 rounded"></div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!activities || activities.length === 0" class="text-center py-4">
        <i class="bi bi-inbox text-muted empty-state-icon"></i>
        <p class="text-muted mt-2 mb-0">No recent activities</p>
      </div>

      <!-- Activities List -->
      <div v-else class="activity-feed">
        <div v-for="activity in activities" :key="activity.id" class="d-flex gap-3 mb-3">
          <div class="flex-shrink-0">
            <div 
              v-if="activity.icon" 
              class="activity-icon-wrapper d-flex align-items-center justify-content-center" 
              :class="activity.color || 'text-primary'"
            >
              <i :class="activity.icon"></i>
            </div>
            <div v-else class="activity-dot rounded-circle bg-primary"></div>
          </div>
          <div class="flex-grow-1 min-w-0">
            <p class="text-dark mb-1" v-if="activity.message">{{ activity.message }}</p>
            <p class="text-dark mb-1 fw-medium" v-else-if="activity.title">{{ activity.title }}</p>
            <p class="small text-muted mb-0" v-if="activity.description">{{ activity.description }}</p>
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
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script>
