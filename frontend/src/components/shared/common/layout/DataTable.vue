<template>
  <div class="data-table-wrapper">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-admin" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">{{ loadingText }}</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!data || data.length === 0" class="text-center py-5">
      <i :class="[emptyIcon, 'display-1 text-muted mb-3']"></i>
      <h5 class="text-muted">{{ emptyTitle }}</h5>
      <p class="text-muted small">{{ emptySubtitle }}</p>
      <slot name="empty-action"></slot>
    </div>

    <!-- Table -->
    <div v-else class="table-responsive">
      <table class="table table-hover align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th 
              v-for="col in columns" 
              :key="col.key"
              :class="[col.headerClass, { 'text-center': col.center, 'd-none d-md-table-cell': col.hideOnMobile }]"
              :style="col.width ? { width: col.width } : {}"
            >
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in data" :key="row[rowKey] || index">
            <td 
              v-for="col in columns" 
              :key="col.key"
              :class="[col.cellClass, { 'text-center': col.center, 'd-none d-md-table-cell': col.hideOnMobile }]"
            >
              <!-- Custom slot for column -->
              <slot :name="`cell-${col.key}`" :row="row" :value="getNestedValue(row, col.key)" :index="index">
                <!-- Default rendering -->
                <template v-if="col.type === 'badge'">
                  <span :class="['badge', getBadgeClass(row, col)]">
                    {{ getNestedValue(row, col.key) }}
                  </span>
                </template>
                <template v-else-if="col.type === 'date'">
                  {{ formatDate(getNestedValue(row, col.key)) }}
                </template>
                <template v-else-if="col.type === 'avatar'">
                  <div class="d-flex align-items-center">
                    <div class="avatar-circle me-2">
                      {{ getAvatarLetter(row, col) }}
                    </div>
                    <span class="fw-semibold">{{ getNestedValue(row, col.key) }}</span>
                  </div>
                </template>
                <template v-else-if="col.type === 'status'">
                  <span :class="['badge', row[col.statusField || 'is_active'] ? 'bg-success' : 'bg-warning']">
                    {{ row[col.statusField || 'is_active'] ? 'Active' : 'Inactive' }}
                  </span>
                </template>
                <template v-else-if="col.type === 'actions'">
                  <div class="d-flex gap-2 justify-content-center flex-wrap">
                    <slot name="actions" :row="row" :index="index"></slot>
                  </div>
                </template>
                <template v-else>
                  {{ getNestedValue(row, col.key) || col.default || '-' }}
                </template>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer with count -->
    <div v-if="showFooter && data && data.length > 0" class="d-flex justify-content-between align-items-center mt-3 px-2">
      <p class="text-muted small mb-0">
        Showing {{ data.length }} {{ data.length === 1 ? 'record' : 'records' }}
      </p>
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { formatDate as formatDateUtil } from '@/utils/formatters'

const props = defineProps({
  columns: {
    type: Array,
    required: true
    // Example: [{ key: 'name', label: 'Name', type: 'avatar' }, { key: 'email', label: 'Email' }]
  },
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Loading data...'
  },
  emptyIcon: {
    type: String,
    default: 'bi bi-inbox'
  },
  emptyTitle: {
    type: String,
    default: 'No data found'
  },
  emptySubtitle: {
    type: String,
    default: 'Try adjusting your filters'
  },
  rowKey: {
    type: String,
    default: 'id'
  },
  showFooter: {
    type: Boolean,
    default: true
  }
})

// Get nested value from object (e.g., 'user.name')
const getNestedValue = (obj, path) => {
  if (!path) return ''
  return path.split('.').reduce((acc, part) => acc && acc[part], obj)
}

// Get avatar letter
const getAvatarLetter = (row, col) => {
  const value = getNestedValue(row, col.avatarField || col.key)
  return value ? value.charAt(0).toUpperCase() : '?'
}

// Format date using shared utility
const formatDate = (dateString) => formatDateUtil(dateString)

// Get badge class based on value
const getBadgeClass = (row, col) => {
  if (col.badgeClass) {
    if (typeof col.badgeClass === 'function') {
      return col.badgeClass(row)
    }
    return col.badgeClass
  }
  return 'bg-light text-dark'
}
</script>


