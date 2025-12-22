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
              class="form-control border-start-0" 
              :placeholder="searchPlaceholder"
            >
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
              class="btn btn-admin-outline flex-grow-1"
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
  showCard: {
    type: Boolean,
    default: false // Set to false since AdminPageTemplate already provides card wrapper
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
  }
})

const emit = defineEmits(['update:modelValue', 'update:statusValue', 'refresh', 'reset', 'search'])

const searchColClass = computed(() => props.searchColSize)
const actionsColClass = computed(() => props.actionsColSize)

const handleSearchInput = (event) => {
  emit('update:modelValue', event.target.value)
  emit('search', event.target.value)
}
</script>


