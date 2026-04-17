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
import { cacheService, studentService, teacherService, departmentService, programService, subjectService, sessionService } from '@/services/shared'

const authStore = useAuth()
const ADMIN_WARMUP_KEY = 'admin:listWarmup:v1'

// Use actual logged-in identity instead of a hardcoded label.
const userName = computed(() => authStore.displayName)

onMounted(() => {
  authStore.hydrateDisplayName().catch(() => {})

  if (cacheService.get(ADMIN_WARMUP_KEY)) return
  cacheService.set(ADMIN_WARMUP_KEY, true)

  // Warm common list caches in the background to reduce first-open delay.
  setTimeout(async () => {
    const normalize = (result) => Array.isArray(result) ? result : (result?.results || result?.data || [])

    const tasks = [
      ['students_list', () => studentService.getAllStudents()],
      ['teachers_list', () => teacherService.getAllTeachers()],
      ['departments_list', () => departmentService.getAllDepartments()],
      ['courses_list', () => programService.getAllPrograms()],
      ['subjects_list', () => subjectService.getAllSubjects()],
      ['sessions_list', () => sessionService.getSessions()]
    ]

    await Promise.allSettled(
      tasks.map(async ([key, fetchFn]) => {
        if (cacheService.get(key)) return
        const response = await fetchFn()
        cacheService.set(key, normalize(response))
      })
    )
  }, 300)
})
</script>
