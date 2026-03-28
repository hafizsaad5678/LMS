<template>
  <div :class="[`${theme}-page-template`]">
    <!-- Page Header -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
        <!-- Title Section -->
        <div class="header-content">
          <div class="d-flex align-items-center gap-3 mb-2">
            <div v-if="icon" class="page-icon" :class="themeIconClass">
              <i :class="icon"></i>
            </div>
            <div>
              <h1 class="page-title mb-1">{{ title }}</h1>
              <p v-if="subtitle" class="page-subtitle mb-0">{{ subtitle }}</p>
            </div>
          </div>
          <nav v-if="breadcrumbs && breadcrumbs.length > 0" aria-label="breadcrumb">
            <ol class="breadcrumb mb-0">
              <li 
                v-for="(crumb, index) in breadcrumbs" 
                :key="index"
                :class="['breadcrumb-item', { 'active': index === breadcrumbs.length - 1 }]"
              >
                <router-link 
                  v-if="crumb.href && index !== breadcrumbs.length - 1" 
                  :to="crumb.href"
                  :class="themeLinkClass"
                >
                  {{ crumb.name }}
                </router-link>
                <span v-else>{{ crumb.name }}</span>
              </li>
            </ol>
          </nav>
        </div>

        <!-- Action Buttons -->
        <div v-if="showActions" class="header-actions d-flex gap-2 flex-wrap">
          <slot name="actions">
            <button
              v-for="(action, index) in actions"
              :key="index"
              :class="['btn', action.variant || themePrimaryBtnClass, action.class]"
              @click="handleActionClick(action)"
              :disabled="action.disabled"
            >
              <i v-if="action.icon" :class="[action.icon, 'me-2']"></i>
              {{ action.label }}
            </button>
          </slot>
        </div>
      </div>
    </div>

    <!-- Stats Section -->
    <div v-if="$slots.stats" class="stats-section mb-4">
      <slot name="stats"></slot>
    </div>

    <!-- Filters Section -->
    <div v-if="$slots.filters" class="filters-section mb-4">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <slot name="filters"></slot>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="content-section">
      <div v-if="showContentCard" class="card border-0 shadow-sm">
        <div v-if="contentTitle" class="card-header bg-white border-bottom">
          <h5 class="card-title mb-0 fw-semibold">{{ contentTitle }}</h5>
        </div>
        <div class="card-body" :class="contentClass">
          <slot name="subcontent">
            <slot></slot>
          </slot>
        </div>
      </div>
      <div v-else>
        <slot name="subcontent">
          <slot></slot>
        </slot>
      </div>
    </div>

    <!-- Footer Section -->
    <div v-if="$slots.footer" class="footer-section mt-4">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: '' },
  breadcrumbs: { type: Array, default: () => [] },
  showActions: { type: Boolean, default: true },
  actions: { type: Array, default: () => [] },
  showContentCard: { type: Boolean, default: true },
  contentTitle: { type: String, default: '' },
  contentClass: { type: String, default: '' },
  theme: {
    type: String,
    default: 'admin',
    validator: (v) => ['admin', 'teacher', 'student'].includes(v)
  }
})

const emit = defineEmits(['action-click'])

// Theme-based computed classes
const themeConfig = {
  admin: {
    primary: '#dc3545',
    gradient: 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)',
    iconClass: 'page-icon-admin',
    linkClass: 'breadcrumb-link-admin',
    btnClass: 'btn-admin-primary'
  },
  teacher: {
    primary: '#0d6efd',
    gradient: 'linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%)',
    iconClass: 'page-icon-teacher',
    linkClass: 'breadcrumb-link-teacher',
    btnClass: 'btn-teacher-primary'
  },
  student: {
    primary: '#198754',
    gradient: 'linear-gradient(135deg, #198754 0%, #157347 100%)',
    iconClass: 'page-icon-student',
    linkClass: 'breadcrumb-link-student',
    btnClass: 'btn-student-primary'
  }
}

const themeIconClass = computed(() => themeConfig[props.theme].iconClass)
const themeLinkClass = computed(() => themeConfig[props.theme].linkClass)
const themePrimaryBtnClass = computed(() => themeConfig[props.theme].btnClass)

const handleActionClick = (action) => {
  if (action.onClick && typeof action.onClick === 'function') {
    action.onClick()
  }
  emit('action-click', action)
}
</script>

<!-- All styles moved to assets/css/components.css -->
