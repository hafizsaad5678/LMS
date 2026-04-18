<template>
  <!-- Sidebar -->
  <aside :class="['sidebar', sidebarTheme, { 'show': isOpen }]">
    <!-- Sidebar Header -->
    <div class="sidebar-header border-bottom">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-3">
          <div :class="['logo-icon', `${sidebarTheme}-icon`]">
            <i :class="dashboardIcon"></i>
          </div>
          <div>
            <h6 class="mb-0 fw-bold">{{ dashboardTitle }}</h6>
            <small class="text-muted">{{ dashboardSubtitle }}</small>
          </div>
        </div>
        <!-- Close button for mobile -->
        <button 
          class="btn btn-link text-muted d-lg-none p-0"
          @click="emit('close')"
          aria-label="Close sidebar"
        >
          <i class="bi bi-x-lg fs-5"></i>
        </button>
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

  <!-- Support Floating Button
  <button 
    :class="['support-float-btn', 'btn', 'rounded-circle', 'shadow-lg', `${sidebarTheme}-float`]"
    @click="toggleSupportCard"
    title="Need Help?">
    <i class="bi bi-question-circle-fill fs-3"></i>
  </button> -->

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
  },
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

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

