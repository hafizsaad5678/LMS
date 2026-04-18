<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
      <h6 class="mb-0 fw-semibold">
        <i :class="[icon, 'me-2 text-info']"></i>{{ title }}
      </h6>
      <span class="badge bg-admin">{{ displayRows.length }} {{ displayRows.length === 1 ? countLabelSingular : countLabelPlural }}</span>
    </div>
    <div class="card-body p-0">
      <div v-if="displayRows.length === 0" class="text-center py-4 text-muted">
        <i class="bi bi-inbox display-6"></i>
        <p class="mt-2">{{ emptyMessage }}</p>
      </div>
      <div v-else class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th v-for="column in resolvedColumns" :key="column.key">{{ column.label }}</th>
              <th v-if="showActions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in displayRows" :key="row.id">
              <td v-for="column in resolvedColumns" :key="`${row.id}-${column.key}`">
                <span v-if="column.badge" :class="column.badgeClass || 'badge bg-dark'">
                  {{ getColumnValue(row, column) }}
                </span>
                <span v-else>{{ getColumnValue(row, column) }}</span>
              </td>
              <td v-if="showActions">
                <button
                  @click="$emit('view-subject', row)"
                  class="btn btn-sm btn-outline-primary"
                  title="View"
                >
                  <i class="bi bi-eye"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Subjects'
  },
  icon: {
    type: String,
    default: 'bi bi-journals'
  },
  subjects: {
    type: Array,
    required: true
  },
  columns: {
    type: Array,
    default: () => []
  },
  limit: {
    type: Number,
    default: 0
  },
  emptyMessage: {
    type: String,
    default: 'No subjects available'
  },
  showTeacher: {
    type: Boolean,
    default: false
  },
  showStudentCount: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: true
  },
  countLabelSingular: {
    type: String,
    default: 'Subject'
  },
  countLabelPlural: {
    type: String,
    default: 'Subjects'
  }
})

defineEmits(['view-subject'])

const defaultColumns = computed(() => {
  const columns = [
    { key: 'subject_code', label: 'Subject Code', fallbackKey: 'code', badge: true, badgeClass: 'badge bg-dark' },
    { key: 'subject_name', label: 'Subject Name', fallbackKey: 'name' },
    { key: 'semester_name', label: 'Semester' },
    { key: 'credit_hours', label: 'Credits' }
  ]

  if (props.showTeacher) {
    columns.push({ key: 'teacher_name', label: 'Teacher' })
  }
  if (props.showStudentCount) {
    columns.push({ key: 'student_count', label: 'Students', badge: true, badgeClass: 'badge bg-info' })
  }

  return columns
})

const resolvedColumns = computed(() => {
  if (Array.isArray(props.columns) && props.columns.length > 0) {
    return props.columns
  }
  return defaultColumns.value
})

const displayRows = computed(() => {
  const list = Array.isArray(props.subjects) ? props.subjects : []
  return props.limit > 0 ? list.slice(0, props.limit) : list
})

const getColumnValue = (row, column) => {
  if (!row || !column) return 'N/A'

  let value = row[column.key]
  if ((value === undefined || value === null || value === '') && column.fallbackKey) {
    value = row[column.fallbackKey]
  }

  if (typeof column.formatter === 'function') {
    return column.formatter(value, row)
  }

  if (value === undefined || value === null || value === '') {
    return 'N/A'
  }

  return value
}
</script>
