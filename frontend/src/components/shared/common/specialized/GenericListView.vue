<template>
  <div class="generic-list-view">
    <!-- Page Header -->
    <div class="page-header d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
      <div class="d-flex align-items-center gap-3">
        <div :class="['page-icon', `bg-${theme}`]">
          <i :class="icon"></i>
        </div>
        <div class="header-content">
          <h1 class="page-title">{{ title }}</h1>
          <p v-if="subtitle" class="page-subtitle mb-0">{{ subtitle }}</p>
        </div>
      </div>
      <div class="header-actions d-flex gap-2">
        <slot name="header-actions">
          <button v-if="addRoute" @click="$router.push(addRoute)" :class="['btn', `btn-${theme}-primary`]">
            <i class="bi bi-plus-lg me-2"></i>{{ addButtonText }}
          </button>
        </slot>
      </div>
    </div>

    <!-- Stats Cards (optional) -->
    <div v-if="showStats" class="row g-3 mb-4">
      <div class="col-md-4 col-6">
        <div class="stat-card bg-gradient-primary text-white">
          <div class="stat-content">
            <h4>{{ stats.total }}</h4>
            <p>Total {{ entityName }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 col-6">
        <div class="stat-card bg-gradient-success text-white">
          <div class="stat-content">
            <h4>{{ stats.active }}</h4>
            <p>Active</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 col-12">
        <div class="stat-card bg-gradient-warning text-white">
          <div class="stat-content">
            <h4>{{ stats.inactive }}</h4>
            <p>Inactive</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Search & Filters -->
    <SearchFilter
      v-model="filters.search"
      v-model:statusValue="filters.status"
      :search-placeholder="searchPlaceholder"
      :show-status-filter="showStatusFilter"
      :theme="theme"
      :loading="loading"
      @refresh="$emit('refresh')"
      @reset="resetFilters"
    >
      <template #filters>
        <slot name="filters"></slot>
      </template>
    </SearchFilter>

    <!-- Data Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body p-0">
        <DataTable
          :columns="columns"
          :data="filteredData"
          :loading="loading"
          :empty-title="emptyTitle"
          :empty-subtitle="emptySubtitle"
          :empty-icon="emptyIcon"
        >
          <!-- Pass through all cell slots -->
          <template v-for="col in columns" :key="col.key" #[`cell-${col.key}`]="slotProps">
            <slot :name="`cell-${col.key}`" v-bind="slotProps">
              <!-- Default rendering handled by DataTable -->
            </slot>
          </template>
          
          <!-- Actions slot -->
          <template #actions="{ row, index }">
            <slot name="actions" :row="row" :index="index">
              <ActionButtons
                :theme="theme"
                :show-view="showViewAction"
                :show-edit="showEditAction"
                :show-delete="showDeleteAction"
                :show-toggle="showToggleAction"
                :is-active="row.is_active"
                @view="$emit('view', row)"
                @edit="$emit('edit', row)"
                @delete="$emit('delete', row)"
                @toggle="$emit('toggle', row)"
              />
            </slot>
          </template>
          
          <template #empty-action>
            <slot name="empty-action">
              <button v-if="addRoute" @click="$router.push(addRoute)" :class="['btn', `btn-${theme}-primary`]">
                <i class="bi bi-plus-lg me-2"></i>{{ addButtonText }}
              </button>
            </slot>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmDialog
      v-if="showDeleteModal"
      :model-value="deleteModalVisible"
      @update:model-value="$emit('update:deleteModalVisible', $event)"
      type="danger"
      :theme="theme"
      :title="`Delete ${entityNameSingular}`"
      :message="deleteMessage"
      :loading="deleteLoading"
      confirm-text="Delete"
      @confirm="$emit('confirm-delete')"
      @cancel="$emit('cancel-delete')"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { SearchFilter, DataTable, ActionButtons, ConfirmDialog } from '@/components/shared/common'


const props = defineProps({
  // Header
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: 'bi bi-list' },
  theme: { type: String, default: 'admin' },
  
  // Entity
  entityName: { type: String, default: 'Items' },
  entityNameSingular: { type: String, default: 'Item' },
  
  // Data
  columns: { type: Array, required: true },
  filteredData: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  filters: { type: Object, default: () => ({ search: '', status: '' }) },
  stats: { type: Object, default: () => ({ total: 0, active: 0, inactive: 0 }) },
  
  // Search & Filter
  searchPlaceholder: { type: String, default: 'Search...' },
  showStatusFilter: { type: Boolean, default: true },
  showStats: { type: Boolean, default: true },
  
  // Actions
  addRoute: { type: [String, Object], default: null },
  addButtonText: { type: String, default: 'Add New' },
  showViewAction: { type: Boolean, default: true },
  showEditAction: { type: Boolean, default: true },
  showDeleteAction: { type: Boolean, default: true },
  showToggleAction: { type: Boolean, default: false },
  
  // Empty State
  emptyTitle: { type: String, default: 'No data found' },
  emptySubtitle: { type: String, default: 'Try adjusting your filters or add a new item' },
  emptyIcon: { type: String, default: 'bi bi-inbox' },
  
  // Delete Modal
  showDeleteModal: { type: Boolean, default: true },
  deleteModalVisible: { type: Boolean, default: false },
  deleteMessage: { type: String, default: 'Are you sure you want to delete this item?' },
  deleteLoading: { type: Boolean, default: false }
})

const emit = defineEmits([
  'refresh', 'reset-filters', 'view', 'edit', 'delete', 'toggle',
  'confirm-delete', 'cancel-delete', 'update:filters', 'update:deleteModalVisible'
])

const resetFilters = () => {
  emit('reset-filters')
  emit('update:filters', { search: '', status: '' })
}
</script>
