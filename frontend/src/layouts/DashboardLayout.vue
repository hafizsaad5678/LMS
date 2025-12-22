<template>
  <div class="min-vh-100 bg-light">
    <!-- Navbar fixed on top -->
    <Navbar 
      :main-nav="mainNav"
      :user-name="userName"
      :header-color="headerColor"
      :header-text-color="headerTextColor"
      @toggle-sidebar="toggleSidebar"
    />
    
    <div class="d-flex">
      <!-- Sidebar Overlay (mobile) -->
      <div 
        class="sidebar-overlay" 
        :class="{ 'show': sidebarOpen }"
        @click="closeSidebar"
      ></div>
      
      <!-- Sidebar fixed on left -->
      <Sidebar 
        :sidebar-sections="sidebarSections"
        :dashboard-highlight-bg="dashboardHighlightBg"
        :dashboard-highlight-text="dashboardHighlightText"
        :sidebar-theme="sidebarTheme"
        :is-open="sidebarOpen"
        @close="closeSidebar"
      />
      
      <!-- Main Content Area with router-view -->
      <main class="main-content flex-grow-1">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
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

const route = useRoute()
const sidebarOpen = ref(false)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

// Close sidebar on route change (mobile)
watch(() => route.path, () => {
  closeSidebar()
})
</script>

<style scoped>
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1019;
  transition: opacity 0.3s ease;
}

@media (max-width: 992px) {
  .sidebar-overlay.show {
    display: block;
  }
}
</style>
