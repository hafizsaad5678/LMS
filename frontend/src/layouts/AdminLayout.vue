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
import { ref } from 'vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { sidebarSections, mainNav } from '@/pannel/admin.js'

const userName = ref('Admin')
</script>
