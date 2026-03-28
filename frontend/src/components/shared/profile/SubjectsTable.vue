<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
      <h6 class="mb-0 fw-semibold">
        <i :class="[icon, 'me-2 text-info']"></i>{{ title }}
      </h6>
      <span class="badge bg-admin">{{ subjects.length }} {{ subjects.length === 1 ? 'Subject' : 'Subjects' }}</span>
    </div>
    <div class="card-body p-0">
      <div v-if="subjects.length === 0" class="text-center py-4 text-muted">
        <i class="bi bi-inbox display-6"></i>
        <p class="mt-2">{{ emptyMessage }}</p>
      </div>
      <div v-else class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Subject Code</th>
              <th>Subject Name</th>
              <th>Semester</th>
              <th>Credits</th>
              <th v-if="showTeacher">Teacher</th>
              <th v-if="showStudentCount">Students</th>
              <th v-if="showActions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="subject in subjects" :key="subject.id">
              <td><span class="badge bg-dark">{{ subject.subject_code || subject.code }}</span></td>
              <td>{{ subject.subject_name || subject.name }}</td>
              <td>{{ subject.semester_name || 'N/A' }}</td>
              <td>{{ subject.credit_hours || 'N/A' }}</td>
              <td v-if="showTeacher">{{ subject.teacher_name || 'N/A' }}</td>
              <td v-if="showStudentCount">
                <span class="badge bg-info">{{ subject.student_count || 0 }}</span>
              </td>
              <td v-if="showActions">
                <button 
                  @click="$emit('view-subject', subject)" 
                  class="btn btn-sm btn-outline-primary" 
                  title="View Subject"
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
defineProps({
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
  }
})

defineEmits(['view-subject'])
</script>
