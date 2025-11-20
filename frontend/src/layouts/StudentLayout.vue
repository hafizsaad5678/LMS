<template>
  <DashboardLayout
    :main-nav="mainNav"
    :sidebar-sections="sidebarSections"
    :user-name="authStore.userName"
    header-color="bg-success"
    header-text-color="text-success"
    dashboard-highlight-bg="bg-light"
    dashboard-highlight-text="text-success"
    sidebar-theme="student"
  />
</template>

<script setup>
import { useAuth } from '@/store/auth.js'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { sidebarSections, mainNav } from '@/pannel/student.js'

const authStore = useAuth()
</script>
