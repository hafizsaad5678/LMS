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
import { ref, computed, onMounted } from 'vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { sidebarSections, mainNav } from '@/pannel/admin.js'
import { useAuth } from '@/store/auth'

const authStore = useAuth()

// Get username from store or localStorage, fallback to 'Admin'
const userName = computed(() => {
  return authStore.userName || localStorage.getItem('username') || 'Admin'
})

// Update store username from localStorage on mount if not already set
onMounted(() => {
  if (!authStore.userName && localStorage.getItem('username')) {
    authStore.userName = localStorage.getItem('username')
  }
})
</script>
