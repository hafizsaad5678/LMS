<template>
  <div class="min-vh-100 bg-light">
    <!-- Navbar fixed on top -->
    <Navbar 
      :main-nav="mainNav"
      :user-name="userName"
      :header-color="headerColor"
      :header-text-color="headerTextColor"
    />
    
    <div class="d-flex">
      <!-- Sidebar fixed on left -->
      <Sidebar 
        :sidebar-sections="sidebarSections"
        :dashboard-highlight-bg="dashboardHighlightBg"
        :dashboard-highlight-text="dashboardHighlightText"
        :sidebar-theme="sidebarTheme"
      />
      
      <!-- Main Content Area with router-view -->
      <main class="flex-grow-1" style="margin-left: 280px; margin-top: 56px; padding: 32px;">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import Navbar from '@/components/navbar/Navbar.vue'
import Sidebar from '@/components/navbar/Sidebar.vue'

defineProps({
  mainNav: {
    type: Array,
    default: () => []
  },
  sidebarSections: {
    type: Array,
    default: () => []
  },
  userName: {
    type: String,
    default: ''
  },
  headerColor: {
    type: String,
    default: 'bg-primary'
  },
  headerTextColor: {
    type: String,
    default: 'text-primary'
  },
  dashboardHighlightBg: {
    type: String,
    default: 'bg-light'
  },
  dashboardHighlightText: {
    type: String,
    default: 'text-primary'
  },
  sidebarTheme: {
    type: String,
    default: 'admin',
    validator: (value) => ['admin', 'teacher', 'student'].includes(value)
  }
})
</script>
