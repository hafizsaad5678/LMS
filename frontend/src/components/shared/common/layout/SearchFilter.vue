<template>
  <component :is="showCard ? 'div' : 'div'" :class="showCard ? 'card border-0 shadow-sm mb-4' : ''">
    <div :class="showCard ? 'card-body' : ''">
      <div class="row g-3 align-items-end">
        <!-- Search Input -->
        <div :class="searchColClass">
          <label v-if="showLabels" class="form-label small fw-semibold text-dark">
            {{ searchLabel }}
          </label>
          <div class="input-group">
            <span class="input-group-text bg-white border-end-0">
              <i class="bi bi-search text-muted"></i>
            </span>
            <input 
              :value="modelValue"
              @input="handleSearchInput"
              type="text" 
              class="form-control border-start-0 border-end-0" 
              :placeholder="searchPlaceholder"
            >
            <button 
              v-if="modelValue && showClearButton"
              @click="clearSearch"
              class="btn btn-link border-start-0 text-muted px-2"
              type="button"
              style="border: 1px solid #dee2e6; border-left: 0; background: white;"
              title="Clear search"
            >
              <i class="bi bi-x-circle"></i>
            </button>
          </div>
        </div>

        <!-- Custom Filter Slots -->
        <slot name="filters"></slot>

        <!-- Status Filter (optional) -->
        <div v-if="showStatusFilter" class="col-md-3 col-6">
          <label v-if="showLabels" class="form-label small fw-semibold text-dark">Status</label>
          <select 
            :value="statusValue"
            @change="$emit('update:statusValue', $event.target.value)"
            class="form-select"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>

        <!-- Action Buttons -->
        <div :class="actionsColClass">
          <div class="d-flex gap-2">
            <button 
              v-if="showRefresh"
              @click="$emit('refresh')" 
              :class="['btn', 'flex-grow-1', refreshButtonClass]"
              :disabled="loading"
            >
              <i class="bi bi-arrow-clockwise me-1 me-sm-2"></i>
              <span class="d-none d-sm-inline">Refresh</span>
            </button>
            <button 
              v-if="showReset"
              @click="$emit('reset')" 
              class="btn btn-outline-secondary flex-grow-1"
            >
              <i class="bi bi-x-circle me-1 me-sm-2"></i>
              <span class="d-none d-sm-inline">Reset</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { sanitizeSearchQuery } from '@/utils/security'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  statusValue: {
    type: String,
    default: ''
  },
  searchPlaceholder: {
    type: String,
    default: 'Search...'
  },
  searchLabel: {
    type: String,
    default: 'Search'
  },
  showLabels: {
    type: Boolean,
    default: true
  },
  showStatusFilter: {
    type: Boolean,
    default: true
  },
  showRefresh: {
    type: Boolean,
    default: true
  },
  showReset: {
    type: Boolean,
    default: true
  },
  showClearButton: {
    type: Boolean,
    default: true
  },
  showCard: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  searchColSize: {
    type: String,
    default: 'col-md-5 col-12'
  },
  actionsColSize: {
    type: String,
    default: 'col-md-4 col-12'
  },
  theme: {
    type: String,
    default: 'admin' // admin, teacher, student
  }
})

const emit = defineEmits(['update:modelValue', 'update:statusValue', 'refresh', 'reset', 'search'])

const searchColClass = computed(() => props.searchColSize)
const actionsColClass = computed(() => props.actionsColSize)

const refreshButtonClass = computed(() => {
  const classes = {
    admin: 'btn-admin-outline',
    teacher: 'btn-teacher-outline',
    student: 'btn-student-outline'
  }
  return classes[props.theme] || 'btn-admin-outline'
})

// Sanitize search input before emitting
const handleSearchInput = (event) => {
  const sanitized = sanitizeSearchQuery(event.target.value)
  emit('update:modelValue', sanitized)
  emit('search', sanitized)
}

// Clear search input
const clearSearch = () => {
  emit('update:modelValue', '')
  emit('search', '')
}
</script>


