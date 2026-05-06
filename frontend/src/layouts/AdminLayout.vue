<template>
  <DashboardLayout
    :main-nav="mainNav"
    :sidebar-sections="sidebarSections"
    :user-name="userName"
    header-color="bg-danger"
    header-text-color="text-danger"
    dashboard-highlight-bg="bg-primary-light"
    dashboard-highlight-text="text-primary"
    sidebar-theme="admin"
  />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { sidebarSections, mainNav } from '@/panels/admin.js'
import { useAuth } from '@/store/auth'
import { cacheService, adminPanelService, studentService, teacherService, departmentService, programService, subjectService, sessionService } from '@/services/shared'

const authStore = useAuth()
const ADMIN_WARMUP_KEY = 'admin:listWarmup:v1'

// Use actual logged-in identity instead of a hardcoded label.
const userName = computed(() => authStore.displayName)

onMounted(() => {
  authStore.hydrateDisplayName().catch(() => {})

  // Warm common list caches in the background to reduce first-open delay.
  setTimeout(async () => {
    // 1. Load the unified dashboard stats first (handles 70% of metrics)
    await adminPanelService.getDashboardStats()

    // 2. Warm other lists with staggering to prevent "flurries"
    if (cacheService.get(ADMIN_WARMUP_KEY)) return
    cacheService.set(ADMIN_WARMUP_KEY, true)

    const normalize = (result) => Array.isArray(result) ? result : (result?.results || result?.data || [])
    
    // We only warm things NOT covered by dashboard stats or that are likely to be visited soon
    const tasks = [
      ['students_list', () => studentService.getAllStudents()],
      ['teachers_list', () => teacherService.getAllTeachers()],
      ['departments_list', () => departmentService.getAllDepartments()],
      ['sessions_list', () => sessionService.getSessions()]
    ]

    for (const [key, fetchFn] of tasks) {
      if (!cacheService.get(key)) {
        const response = await fetchFn()
        cacheService.set(key, normalize(response))
        // Stagger requests by 1 second to stay under rate limits
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
  }, 1000)
})
</script>
