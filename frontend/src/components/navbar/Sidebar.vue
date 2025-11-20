<template>
  <!-- Sidebar -->
  <aside :class="['sidebar', sidebarTheme]">
    <!-- Sidebar Header -->
    <div class="sidebar-header border-bottom">
      <div class="d-flex align-items-center gap-3">
        <div :class="['logo-icon', `${sidebarTheme}-icon`]">
          <i :class="dashboardIcon"></i>
        </div>
        <div>
          <h6 class="mb-0 fw-bold">{{ dashboardTitle }}</h6>
          <small class="text-muted">{{ dashboardSubtitle }}</small>
        </div>
      </div>
    </div>

    <!-- Sidebar Navigation -->
    <nav class="p-3">
      <div v-for="section in sidebarSections" :key="section.title" class="mb-4">
        <h6 
          v-if="section.items.length > 1 || section.items[0]?.name !== section.title"
          class="text-muted small fw-bold text-uppercase px-3 mb-2">
          {{ section.title }}
        </h6>
        
        <div class="d-flex flex-column gap-1">
          <div v-for="item in section.items" :key="item.name">
            <!-- Main Item -->
            <router-link
              v-if="!item.submenu || item.submenu.length === 0"
              :to="item.href"
              :class="['nav-item', { 'active': isActive(item.href) }]"
              @click="closeSubmenu(item.name)">
              <span v-if="item.icon" class="me-3">{{ item.icon }}</span>
              <span>{{ item.name }}</span>
            </router-link>

            <button
              v-else
              @click="toggleExpanded(item.name)"
              :class="['nav-item', 'btn', 'w-100', 'text-start', { 'active': expandedItems[item.name] }]">
              <div class="d-flex align-items-center justify-content-between">
                <div>
                  <span v-if="item.icon" class="me-3">{{ item.icon }}</span>
                  <span>{{ item.name }}</span>
                </div>
                <i :class="['bi', 'bi-chevron-down', 'small', { 'rotate-180': expandedItems[item.name] }]"></i>
              </div>
            </button>

            <!-- Submenu -->
            <Transition name="submenu">
              <div v-if="item.submenu && item.submenu.length > 0 && expandedItems[item.name]" class="submenu ms-4 mt-1">
                <router-link 
                  v-for="subitem in item.submenu"
                  :key="subitem.name"
                  :to="subitem.href"
                  :class="['submenu-item', 'd-flex', 'align-items-center', 'gap-2', { 'active': isActive(subitem.href) }]">
                  <span v-if="subitem.icon">{{ subitem.icon }}</span>
                  <span>{{ subitem.name }}</span>
                </router-link>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </nav>
  </aside>

  <!-- Support Floating Button -->
  <button 
    :class="['support-float-btn', 'btn', 'rounded-circle', 'shadow-lg', `${sidebarTheme}-float`]"
    @click="toggleSupportCard"
    title="Need Help?">
    <i class="bi bi-question-circle-fill fs-3"></i>
  </button>

  <!-- Support Card -->
  <Transition name="support-card">
    <div v-if="showSupportCard" class="support-card-container">
      <div :class="['card', 'shadow-lg', 'border-3', `${sidebarTheme}-support`]">
        <div class="card-body text-center p-4">
          <button class="btn-close position-absolute top-0 end-0 m-2" @click="toggleSupportCard"></button>
          <div class="fs-1 mb-3">💬</div>
          <h6 class="fw-bold mb-2">Need Help?</h6>
          <p class="text-muted small mb-3">Our support team is here to assist you</p>
          <button :class="['btn', 'w-100', 'text-white', 'fw-semibold', `${sidebarTheme}-btn`]">
            Contact Support
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { reactive, computed, ref } from 'vue'

const props = defineProps({
  sidebarSections: {
    type: Array,
    default: () => []
  },
  sidebarTheme: {
    type: String,
    default: 'admin',
    validator: (value) => ['admin', 'teacher', 'student'].includes(value)
  },
  dashboardHighlightBg:{
    type: String,
    default: ''
  },
  dashboardHighlightText: {
    type: String,
    default: ''
  }
})

const route = useRoute()
const expandedItems = reactive({})
const showSupportCard = ref(false)

const dashboardTitle = computed(() => {
  const titles = { admin: 'Admin Panel', teacher: 'Teacher Hub', student: 'Student Portal' }
  return titles[props.sidebarTheme]
})

const dashboardSubtitle = computed(() => {
  const subtitles = { admin: 'Management System', teacher: 'Teaching Dashboard', student: 'Learning Center' }
  return subtitles[props.sidebarTheme]
})

const dashboardIcon = computed(() => {
  const icons = { admin: 'bi bi-shield-fill-check', teacher: 'bi bi-mortarboard-fill', student: 'bi bi-book-fill' }
  return icons[props.sidebarTheme]
})

const toggleExpanded = (itemName) => {
  expandedItems[itemName] = !expandedItems[itemName]
}

const closeSubmenu = (itemName) => {
  expandedItems[itemName] = false
}

const isActive = (href) => {
  return route.path === href || route.path.startsWith(href + '/')
}

const toggleSupportCard = () => {
  showSupportCard.value = !showSupportCard.value
}
</script>

<style scoped>
.sidebar {
  width: 280px;
  position: fixed;
  left: 0;
  top: 56px;
  bottom: 0;
  overflow-y: auto;
  z-index: 1020;
}

.sidebar.admin { background: linear-gradient(180deg, #ffe5e8 0%, #ffd6db 100%); }
.sidebar.teacher { background: linear-gradient(180deg, #e7f1ff 0%, #d4e7ff 100%); }
.sidebar.student { background: linear-gradient(180deg, #e8f5e9 0%, #d4edda 100%); }

.sidebar-header { padding: 1.5rem 1.25rem; }

.logo-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.admin-icon { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3); }
.teacher-icon { background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%); box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3); }
.student-icon { background: linear-gradient(135deg, #198754 0%, #146c43 100%); box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3); }

.nav-item {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  color: #495057;
  text-decoration: none;
  background: transparent;
  border: none;
  transition: all 0.2s;
  display: block;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.6);
  color: #1a1a1a;
  transform: translateX(4px);
}

.sidebar.admin .nav-item.active {
  background: rgba(220, 53, 69, 0.15);
  color: #dc3545;
  font-weight: 600;
  border-left: 4px solid #dc3545;
}

.sidebar.teacher .nav-item.active {
  background: rgba(13, 110, 253, 0.15);
  color: #0d6efd;
  font-weight: 600;
  border-left: 4px solid #0d6efd;
}

.sidebar.student .nav-item.active {
  background: rgba(25, 135, 84, 0.15);
  color: #198754;
  font-weight: 600;
  border-left: 4px solid #198754;
}

.rotate-180 { transform: rotate(180deg); transition: transform 0.3s; }

.submenu {
  padding-left: 1.5rem;
  border-left: 2px solid rgba(0, 0, 0, 0.1);
}

.submenu-item {
  padding: 0.625rem 1rem;
  border-radius: 8px;
  color: #6c757d;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s;
  display: block;
}

.submenu-item:hover {
  background: rgba(255, 255, 255, 0.5);
  color: #1a1a1a;
}

.sidebar.admin .submenu-item.active { background: rgba(220, 53, 69, 0.12); color: #dc3545; font-weight: 600; }
.sidebar.teacher .submenu-item.active { background: rgba(13, 110, 253, 0.12); color: #0d6efd; font-weight: 600; }
.sidebar.student .submenu-item.active { background: rgba(25, 135, 84, 0.12); color: #198754; font-weight: 600; }

.submenu-enter-active, .submenu-leave-active { transition: all 0.3s; overflow: hidden; }
.submenu-enter-from, .submenu-leave-to { opacity: 0; max-height: 0; }
.submenu-enter-to, .submenu-leave-from { opacity: 1; max-height: 500px; }

.support-float-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 60px;
  height: 60px;
  border: none;
  color: white;
  z-index: 9998;
  transition: all 0.3s;
}

.admin-float { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); }
.teacher-float { background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%); }
.student-float { background: linear-gradient(135deg, #198754 0%, #146c43 100%); }

.support-float-btn:hover {
  transform: scale(1.1) rotate(15deg);
}

.support-card-container {
  position: fixed;
  bottom: 100px;
  right: 24px;
  z-index: 9999;
  min-width: 280px;
}

.admin-support { border-color: #dc3545 !important; }
.teacher-support { border-color: #0d6efd !important; }
.student-support { border-color: #198754 !important; }

.admin-btn { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); }
.teacher-btn { background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%); }
.student-btn { background: linear-gradient(135deg, #198754 0%, #146c43 100%); }

.support-card-enter-active, .support-card-leave-active { transition: all 0.3s; }
.support-card-enter-from, .support-card-leave-to { opacity: 0; transform: translateY(20px) scale(0.9); }

@media (max-width: 992px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.show { transform: translateX(0); }
}
</style>