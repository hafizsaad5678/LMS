<template>
  <div class="d-flex gap-1 gap-sm-2 justify-content-center">
    <!-- View Button -->
    <button 
      v-if="showView"
      @click="$emit('view', item)"
      class="btn btn-sm btn-outline-info btn-action"
      :title="viewTitle"
    >
      <i class="bi bi-eye"></i>
      <span v-if="showLabels" class="d-none d-lg-inline ms-1">View</span>
    </button>

    <!-- Edit Button -->
    <button 
      v-if="showEdit"
      @click="$emit('edit', item)"
      class="btn btn-sm btn-outline-primary btn-action"
      :title="editTitle"
    >
      <i class="bi bi-pencil"></i>
      <span v-if="showLabels" class="d-none d-lg-inline ms-1">Edit</span>
    </button>

    <!-- Toggle Status Button -->
    <button 
      v-if="showToggle"
      @click="$emit('toggle', item)"
      class="btn btn-sm btn-action"
      :class="item[statusField] ? 'btn-outline-warning' : 'btn-outline-success'"
      :title="item[statusField] ? 'Deactivate' : 'Activate'"
    >
      <i :class="item[statusField] ? 'bi bi-slash-circle' : 'bi bi-check-circle'"></i>
    </button>

    <!-- Delete Button -->
    <button 
      v-if="showDelete"
      @click="$emit('delete', item)"
      class="btn btn-sm btn-outline-danger btn-action"
      :title="deleteTitle"
    >
      <i class="bi bi-trash"></i>
      <span v-if="showLabels" class="d-none d-lg-inline ms-1">Delete</span>
    </button>

    <!-- Custom Actions Slot -->
    <slot :item="item"></slot>
  </div>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true
  },
  showView: {
    type: Boolean,
    default: true
  },
  showEdit: {
    type: Boolean,
    default: true
  },
  showDelete: {
    type: Boolean,
    default: true
  },
  showToggle: {
    type: Boolean,
    default: false
  },
  showLabels: {
    type: Boolean,
    default: false
  },
  statusField: {
    type: String,
    default: 'is_active'
  },
  viewTitle: {
    type: String,
    default: 'View Details'
  },
  editTitle: {
    type: String,
    default: 'Edit'
  },
  deleteTitle: {
    type: String,
    default: 'Delete'
  }
})

defineEmits(['view', 'edit', 'delete', 'toggle'])
</script>


