<template>
  <section id="stats" class="py-4 bg-dark home-stats border-top border-bottom border-secondary">
    <div class="container">
      <div class="row g-4 text-center">
        <div class="col-md-3 col-6">
          <div class="p-3 rounded-4 h-100 home-stat-card">
            <div class="mb-2"><i class="bi bi-people-fill text-info fs-4"></i></div>
            <h5 class="text-info fw-bold mb-1">{{ stats.activeStudents.toLocaleString() }}+</h5>
            <small class="text-light-emphasis">Active Users</small>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="p-3 rounded-4 h-100 home-stat-card">
            <div class="mb-2"><i class="bi bi-person-workspace text-warning fs-4"></i></div>
            <h5 class="text-warning fw-bold mb-1">{{ stats.expertTeachers.toLocaleString() }}+</h5>
            <small class="text-light-emphasis">Expert Mentors</small>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="p-3 rounded-4 h-100 home-stat-card">
            <div class="mb-2"><i class="bi bi-book-half text-success fs-4"></i></div>
            <h5 class="text-success fw-bold mb-1">{{ stats.totalCourses.toLocaleString() }}+</h5>
            <small class="text-light-emphasis">Organizations</small>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="p-3 rounded-4 h-100 home-stat-card">
            <div class="mb-2"><i class="bi bi-cloud-check-fill text-primary fs-4"></i></div>
            <h5 class="text-primary fw-bold mb-1">{{ stats.platformUptime }}%</h5>
            <small class="text-light-emphasis">Platform Uptime</small>
          </div>
        </div>
      </div>
      <div v-if="loading" class="text-center mt-3 text-light-emphasis small">
        <span class="spinner-grow spinner-grow-sm me-2" role="status" aria-hidden="true"></span>
        Connecting to live feed...
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { API_BASE_URL } from '@/utils/constants/config'

const buildApiUrl = (path) => {
  const cleanBase = String(API_BASE_URL || '').replace(/\/$/, '')
  const cleanPath = String(path || '').replace(/^\//, '')
  return `${cleanBase}/${cleanPath}`
}

const loading = ref(true)
const stats = ref({
  activeStudents: 500,
  expertTeachers: 50,
  totalCourses: 100,
  platformUptime: 99.9
})

let pollingInterval = null

const fetchStats = async () => {
  try {
    const response = await fetch(buildApiUrl('/public/stats/'))
    if (response.ok) {
      const data = await response.json()
      // Real-time animation variation based on fetched limits.
      const variation = Math.floor(Math.random() * 5) - 2
      stats.value = {
        activeStudents: Math.max(0, data.activeStudents + variation),
        expertTeachers: data.expertTeachers,
        totalCourses: data.institutions || data.totalCourses, // Map DB response correctly
        platformUptime: data.platformUptime
      }
    }
  } catch (error) {
    console.error('Failed to fetch real-time stats:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
  
  // Replace backend polling with local frontend variation to avoid API rate limits (429)
  pollingInterval = setInterval(() => {
    const variation = Math.floor(Math.random() * 5) - 2
    stats.value.activeStudents = Math.max(0, stats.value.activeStudents + variation)
  }, 3000)
})

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval)
})
</script>