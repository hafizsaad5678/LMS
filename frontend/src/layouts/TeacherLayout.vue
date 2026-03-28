<template>
  <DashboardLayout
    :main-nav="mainNav"
    :sidebar-sections="sidebarSections"
    :user-name="authStore.userName"
    header-color="bg-primary"
    header-text-color="text-primary"
    dashboard-highlight-bg="bg-light"
    dashboard-highlight-text="text-primary"
    sidebar-theme="teacher"
  />
</template>

<script setup>
import { useAuth } from '@/store/auth.js'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { sidebarSections, mainNav } from '@/panels/teacher.js'

const authStore = useAuth()
</script>
