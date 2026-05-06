<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header border-0" :class="headerClass">
      <h5 class="mb-0" :class="headerTextClass">
        <i :class="icon + ' me-2'"></i>{{ title }}
      </h5>
    </div>
    <div class="card-body">
      <div v-if="loading" class="text-center py-3">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <span class="ms-2">Loading students...</span>
      </div>
      <div v-else-if="students.length === 0" class="text-center py-3">
        <i class="bi bi-people text-muted icon-size-2rem"></i>
        <p class="text-muted mt-2 mb-0">{{ emptyMessage }}</p>
      </div>
      <div v-else class="row g-3">
        <div v-for="student in students" :key="student.id" :class="cardColClass">
          <div class="card border-0 shadow-sm h-100 hover-card" :class="{ 'border-teacher': isCurrentStudent(student) }">
            <div class="card-body">
              <div class="d-flex align-items-start mb-3">
                <div class="rounded-circle d-flex align-items-center justify-content-center me-3 avatar-40 avatar-circle-teacher-bg">
                  <span class="fw-bold text-teacher">{{ student.name.charAt(0).toUpperCase() }}</span>
                </div>
                <div class="flex-grow-1">
                  <h6 class="fw-bold mb-1">{{ student.name }}</h6>
                  <p class="text-muted small mb-1">{{ student.roll_no }}</p>
                  <p class="text-muted small mb-0">{{ student.email }}</p>
                </div>
                <div v-if="isCurrentStudent(student)" class="badge bg-teacher-light text-teacher">
                  Current
                </div>
              </div>
              
              <div class="mb-3">
                <div class="d-flex align-items-center gap-2 mb-1">
                  <i class="bi bi-building text-muted small"></i>
                  <small class="text-muted">{{ student.department_name }}</small>
                </div>
                <div class="d-flex align-items-center gap-2 mb-1">
                  <i class="bi bi-mortarboard text-muted small"></i>
                  <small class="text-muted">{{ student.program_name }}</small>
                </div>
              </div>
              
              <div class="d-flex gap-2">
                <slot name="actions" :student="student">
                  <button 
                    @click="$emit('view', student)" 
                    class="btn btn-sm flex-grow-1"
                    :class="isCurrentStudent(student) ? 'btn-teacher-primary' : 'btn-teacher-outline'"
                    :disabled="isCurrentStudent(student)"
                  >
                    <i class="bi bi-eye me-1"></i>
                    {{ isCurrentStudent(student) ? 'Current Student' : 'View' }}
                  </button>
                </slot>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  students: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Students'
  },
  icon: {
    type: String,
    default: 'bi bi-people'
  },
  headerClass: {
    type: String,
    default: 'bg-gradient-blue'
  },
  headerTextClass: {
    type: String,
    default: ''
  },
  emptyMessage: {
    type: String,
    default: 'No students found'
  },
  currentStudentId: {
    type: [String, Number],
    default: null
  },
  cardColClass: {
    type: String,
    default: 'col-md-6 col-lg-4'
  }
})

defineEmits(['view'])

const isCurrentStudent = (student) => {
  return props.currentStudentId && student.id.toString() === props.currentStudentId.toString()
}
</script>
