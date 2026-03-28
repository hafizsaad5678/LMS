<template>
  <div class="card border-0 shadow-sm h-100">
    <div class="card-header bg-white border-bottom-0 pt-4 px-3 d-flex justify-content-between align-items-center">
      <h6 class="mb-0 fw-bold">{{ title }}</h6>
      <button @click="$emit('create')" class="btn btn-sm btn-teacher-light rounded-pill px-3">
        <i class="bi bi-plus-lg me-1"></i> New
      </button>
    </div>
    <div class="card-body p-2 overflow-auto max-h-70vh">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
      </div>
      <div v-else-if="items.length === 0" class="text-center py-5 text-muted px-3">
        <i :class="emptyIcon + ' display-6 mb-2 d-block'"></i>
        <p class="small">{{ emptyMessage }}</p>
      </div>
      <div v-else class="d-flex flex-column gap-2">
        <div 
          v-for="item in items" 
          :key="item.id"
          class="assessment-item p-3 rounded-4 border transition-all cursor-pointer position-relative"
          :class="{ 'active-assessment border-teacher shadow-sm': selectedId === item.id }"
          @click="$emit('select', item)"
        >
          <div class="d-flex justify-content-between align-items-start mb-2">
            <span class="badge badge-soft-primary small">{{ getTypeName(item.component_type) }}</span>
            <div class="dropdown" @click.stop>
              <button class="btn btn-sm p-0 text-muted" type="button" data-bs-toggle="dropdown">
                <i class="bi bi-three-dots"></i>
              </button>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0">
                <li><a class="dropdown-item small" href="#" @click.prevent="$emit('edit', item)"><i class="bi bi-pencil me-2"></i>Edit</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item small text-danger" href="#" @click.prevent="$emit('delete', item.id)"><i class="bi bi-trash me-2"></i>Delete</a></li>
              </ul>
            </div>
          </div>
          <h6 class="fw-bold mb-1 text-truncate">{{ item.name }}</h6>
          <div class="d-flex justify-content-between align-items-center small text-muted">
            <span>Weight: <strong>{{ item.weightage }}%</strong></span>
            <span>Max: <strong>{{ item.max_marks }}</strong></span>
          </div>
          <div class="progress mt-2 progress-h-4">
            <div class="progress-bar bg-teacher" :style="{ width: getProgress(item) + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ASSESSMENT_TYPES } from '@/utils/constants/options'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  selectedId: {
    type: [String, Number],
    default: null
  },
  title: {
    type: String,
    default: 'Assessments'
  },
  emptyIcon: {
    type: String,
    default: 'bi bi-clipboard-x'
  },
  emptyMessage: {
    type: String,
    default: 'No assessments created yet.'
  }
})

defineEmits(['create', 'select', 'edit', 'delete'])

const getTypeName = (type) => {
  if (!type) return 'N/A'
  const option = ASSESSMENT_TYPES.find(opt => opt.value === type)
  return option ? option.label : type.charAt(0).toUpperCase() + type.slice(1)
}

const getProgress = (item) => {
  return item.total_students > 0 
    ? (item.students_graded / item.total_students) * 100 
    : 0
}
</script>
