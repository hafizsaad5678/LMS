<template>
  <DashboardLayout
    :main-nav="mainNav"
    :sidebar-sections="sidebarSections"
    :user-name="displayName"
    header-color="bg-success"
    header-text-color="text-success"
    dashboard-highlight-bg="bg-light"
    dashboard-highlight-text="text-success"
    sidebar-theme="student"
  />

  <!-- Floating Academic Assistant -->
  <StudentAIChatbot />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuth } from '@/store/auth.js'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { sidebarSections, mainNav } from '@/panels/student.js'
import { StudentAIChatbot } from '@/components/shared/panels'

const authStore = useAuth()
const displayName = computed(() => authStore.displayName)

onMounted(() => {
  authStore.hydrateDisplayName().catch(() => {})
})
</script>
