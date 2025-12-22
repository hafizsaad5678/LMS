<template>
  <div class="admin-page-template">
    <!-- Page Header -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
        <!-- Title Section -->
        <div class="header-content">
          <div class="d-flex align-items-center gap-3 mb-2">
            <div v-if="icon" class="page-icon">
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
                <router-link v-if="crumb.href && index !== breadcrumbs.length - 1" :to="crumb.href">
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
            <!-- Default action buttons if provided via props -->
            <button
              v-for="(action, index) in actions"
              :key="index"
              :class="['btn', action.variant || 'btn-admin-primary', action.class]"
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

    <!-- Stats/Quick Info Section (Optional) -->
    <div v-if="$slots.stats" class="stats-section mb-4">
      <slot name="stats"></slot>
    </div>

    <!-- Filters/Search Section (Optional) -->
    <div v-if="$slots.filters" class="filters-section mb-4">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <slot name="filters"></slot>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="content-section">
      <div v-if="showContentCard" class="card border-0 shadow-sm">
        <div v-if="contentTitle" class="card-header bg-white border-bottom">
          <h5 class="card-title mb-0 fw-semibold">{{ contentTitle }}</h5>
        </div>
        <div class="card-body" :class="contentClass">
          <slot></slot>
        </div>
      </div>
      <div v-else>
        <slot></slot>
      </div>
    </div>

    <!-- Footer Section (Optional) -->
    <div v-if="$slots.footer" class="footer-section mt-4">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>


const props = defineProps({
  // Page title and metadata
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  breadcrumbs: {
    type: Array,
    default: () => []
    // Example: [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Students' }]
  },
  
  // Action buttons
  showActions: {
    type: Boolean,
    default: true
  },
  actions: {
    type: Array,
    default: () => []
    // Example: [{ label: 'Add Student', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => {} }]
  },
  
  // Content card settings
  showContentCard: {
    type: Boolean,
    default: true
  },
  contentTitle: {
    type: String,
    default: ''
  },
  contentClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['action-click'])

const handleActionClick = (action) => {
  if (action.onClick && typeof action.onClick === 'function') {
    action.onClick()
  }
  emit('action-click', action)
}
</script>

<style scoped>
.admin-page-template {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Page Header */
.page-header {
  padding-bottom: 1rem;
  border-bottom: 2px solid #f8f9fa;
}

.header-content {
  flex: 1;
}

.page-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  box-shadow: 0 4px 16px rgba(220, 53, 69, 0.3);
  transition: all 0.3s ease;
}

.page-icon:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 1rem;
  color: #6c757d;
  font-weight: 400;
}

/* Breadcrumbs */
.breadcrumb {
  background: transparent;
  padding: 0.5rem 0 0 0;
  margin: 0;
  font-size: 0.875rem;
}

.breadcrumb-item a {
  color: #dc3545;
  text-decoration: none;
  transition: all 0.2s;
}

.breadcrumb-item a:hover {
  color: #c82333;
  text-decoration: underline;
}

.breadcrumb-item.active {
  color: #6c757d;
}

.breadcrumb-item + .breadcrumb-item::before {
  color: #adb5bd;
}

/* Action Buttons */
.header-actions {
  align-items: flex-start;
}

.btn-admin-primary {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  border: none;
  color: white;
  font-weight: 600;
  padding: 0.625rem 1.5rem;
  border-radius: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
}

.btn-admin-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
  background: linear-gradient(135deg, #c82333 0%, #bd2130 100%);
}

.btn-admin-primary:active {
  transform: translateY(0);
}

.btn-admin-secondary {
  background: white;
  border: 2px solid #dc3545;
  color: #dc3545;
  font-weight: 600;
  padding: 0.625rem 1.5rem;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.btn-admin-secondary:hover {
  background: #dc3545;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.2);
}

.btn-admin-outline {
  background: transparent;
  border: 1px solid #dee2e6;
  color: #495057;
  font-weight: 500;
  padding: 0.625rem 1.5rem;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.btn-admin-outline:hover {
  background: #f8f9fa;
  border-color: #dc3545;
  color: #dc3545;
}

/* Content Card */
.card {
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  padding: 1.25rem 1.5rem;
  border-radius: 12px 12px 0 0 !important;
}

.card-body {
  padding: 1.5rem;
}

.card-title {
  color: #1a1a1a;
  font-size: 1.125rem;
}

/* Stats Section */
.stats-section {
  animation: slideUp 0.4s ease-out 0.1s both;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Filters Section */
.filters-section {
  animation: slideUp 0.4s ease-out 0.2s both;
}

/* Content Section */
.content-section {
  animation: slideUp 0.4s ease-out 0.3s both;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.5rem;
  }

  .page-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
    min-width: auto;
  }

  .card-body {
    padding: 1rem;
  }
}

@media (max-width: 576px) {
  .page-header {
    padding-bottom: 0.75rem;
  }

  .page-title {
    font-size: 1.25rem;
  }

  .page-subtitle {
    font-size: 0.875rem;
  }

  .btn-admin-primary,
  .btn-admin-secondary,
  .btn-admin-outline {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }
}

/* Loading State */
.content-section.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6c757d;
}

.empty-state i {
  font-size: 4rem;
  color: #dee2e6;
  margin-bottom: 1rem;
}

/* Utility Classes */
.text-admin {
  color: #dc3545 !important;
}

.bg-admin-light {
  background-color: rgba(220, 53, 69, 0.1) !important;
}

.border-admin {
  border-color: #dc3545 !important;
}
</style>
