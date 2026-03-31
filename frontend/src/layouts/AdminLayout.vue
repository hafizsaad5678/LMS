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
import { computed } from 'vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { sidebarSections, mainNav } from '@/panels/admin.js'
import { useAuth } from '@/store/auth'

const authStore = useAuth()

// Get username from auth store with fallback
const userName = computed(() => 'Admin')
</script>
