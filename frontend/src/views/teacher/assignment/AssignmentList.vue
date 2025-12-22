<template>
  <TeacherPageTemplate
    title="Assignments"
    subtitle="Manage and review student assignments"
    icon="bi bi-clipboard-check"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <template #stats>
      <div class="row g-3 mb-4">
        <div class="col-md-3 col-6">
          <div class="stat-card bg-gradient-primary text-white">
            <i class="bi bi-file-earmark-text stat-icon"></i>
            <div class="stat-content">
              <h3>{{ assignments.length }}</h3>
              <p>Total Assignments</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card bg-gradient-warning text-white">
            <i class="bi bi-hourglass-split stat-icon"></i>
            <div class="stat-content">
              <h3>{{ pendingReviews }}</h3>
              <p>Pending Reviews</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card bg-gradient-success text-white">
            <i class="bi bi-check-circle stat-icon"></i>
            <div class="stat-content">
              <h3>{{ gradedCount }}</h3>
              <p>Graded</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card bg-gradient-info text-white">
            <i class="bi bi-calendar-event stat-icon"></i>
            <div class="stat-content">
              <h3>{{ upcomingDeadlines }}</h3>
              <p>Due This Week</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #filters>
      <SearchFilter
        v-model="searchQuery"
        :show-status-filter="false"
        search-placeholder="Search assignments..."
        @refresh="loadAssignments"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3">
            <label class="form-label small fw-semibold">Class</label>
            <select v-model="filters.class" class="form-select">
              <option value="">All Classes</option>
              <option value="1">Data Structures</option>
              <option value="2">Database Systems</option>
              <option value="3">Web Development</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-semibold">Status</label>
            <select v-model="filters.status" class="form-select">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="closed">Closed</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <DataTable
      :columns="columns"
      :data="filteredAssignments"
      :loading="loading"
      empty-title="No Assignments Found"
      empty-subtitle="Create your first assignment to get started"
    >
      <template #cell-title="{ row }">
        <div>
          <div class="fw-semibold">{{ row.title }}</div>
          <small class="text-muted">{{ row.class_name }}</small>
        </div>
      </template>

      <template #cell-due_date="{ row }">
        <div>
          <div>{{ formatDate(row.due_date) }}</div>
          <small :class="getDueDateClass(row.due_date)">
            {{ getDueDateLabel(row.due_date) }}
          </small>
        </div>
      </template>

      <template #cell-submissions="{ row }">
        <div class="text-center">
          <div class="fw-semibold">{{ row.submitted }}/{{ row.total_students }}</div>
          <div class="progress mt-1" style="height: 4px;">
            <div 
              class="progress-bar bg-teacher" 
              :style="{ width: `${(row.submitted / row.total_students) * 100}%` }"
            ></div>
          </div>
        </div>
      </template>

      <template #cell-status="{ row }">
        <span :class="['badge', getStatusClass(row.status)]">
          {{ row.status }}
        </span>
      </template>

      <template #actions="{ row }">
        <button @click="viewAssignment(row)" class="btn btn-sm btn-outline-info" title="View">
          <i class="bi bi-eye"></i>
        </button>
        <button @click="viewSubmissions(row)" class="btn btn-sm btn-outline-success" title="Submissions">
          <i class="bi bi-file-earmark-check"></i>
        </button>
        <button @click="editAssignment(row)" class="btn btn-sm btn-outline-primary" title="Edit">
          <i class="bi bi-pencil"></i>
        </button>
      </template>
    </DataTable>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TeacherPageTemplate from '@/components/navbar/TeacherPageTemplate.vue'
import SearchFilter from '@/components/common/SearchFilter.vue'
import DataTable from '@/components/common/DataTable.vue'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/teacher-dashboard' },
  { name: 'Assignments' }
]

const actions = [
  { label: 'Create Assignment', icon: 'bi bi-plus-circle', variant: 'btn-teacher-primary', onClick: () => router.push('/teacher-dashboard/assignments/create') }
]

const columns = [
  { key: 'title', label: 'Assignment', type: 'custom' },
  { key: 'due_date', label: 'Due Date', type: 'custom' },
  { key: 'submissions', label: 'Submissions', type: 'custom', center: true },
  { key: 'total_marks', label: 'Marks', center: true },
  { key: 'status', label: 'Status', type: 'custom', center: true },
  { key: 'actions', label: 'Actions', type: 'actions', center: true }
]

const loading = ref(false)
const searchQuery = ref('')
const filters = ref({ class: '', status: '' })

const assignments = ref([
  { id: 1, title: 'Binary Search Trees', class_name: 'Data Structures', due_date: '2025-12-25', submitted: 35, total_students: 45, total_marks: 100, status: 'active' },
  { id: 2, title: 'SQL Queries Practice', class_name: 'Database Systems', due_date: '2025-12-20', submitted: 28, total_students: 38, total_marks: 50, status: 'active' },
  { id: 3, title: 'React Components', class_name: 'Web Development', due_date: '2025-12-15', submitted: 42, total_students: 42, total_marks: 75, status: 'closed' },
  { id: 4, title: 'Process Scheduling', class_name: 'Operating Systems', due_date: '2025-12-30', submitted: 0, total_students: 35, total_marks: 100, status: 'draft' }
])

const pendingReviews = computed(() => assignments.value.reduce((sum, a) => sum + (a.total_students - a.submitted), 0))
const gradedCount = computed(() => assignments.value.filter(a => a.status === 'closed').length)
const upcomingDeadlines = computed(() => assignments.value.filter(a => {
  const dueDate = new Date(a.due_date)
  const today = new Date()
  const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
  return dueDate >= today && dueDate <= weekFromNow
}).length)

const filteredAssignments = computed(() => {
  let result = assignments.value

  if (searchQuery.value) {
    result = result.filter(a =>
      a.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      a.class_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (filters.value.status) {
    result = result.filter(a => a.status === filters.value.status)
  }

  return result
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const getDueDateLabel = (dateString) => {
  const dueDate = new Date(dateString)
  const today = new Date()
  const diffTime = dueDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'Overdue'
  if (diffDays === 0) return 'Due Today'
  if (diffDays === 1) return 'Due Tomorrow'
  if (diffDays <= 7) return `${diffDays} days left`
  return ''
}

const getDueDateClass = (dateString) => {
  const dueDate = new Date(dateString)
  const today = new Date()
  const diffDays = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'text-danger'
  if (diffDays <= 3) return 'text-warning'
  return 'text-success'
}

const getStatusClass = (status) => {
  const classes = {
    active: 'bg-success',
    closed: 'bg-secondary',
    draft: 'bg-warning text-dark'
  }
  return classes[status] || 'bg-light text-dark'
}

const loadAssignments = () => {
  loading.value = true
  setTimeout(() => loading.value = false, 500)
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = { class: '', status: '' }
}

const viewAssignment = (assignment) => {
  router.push(`/teacher-dashboard/assignments/${assignment.id}`)
}

const viewSubmissions = (assignment) => {
  router.push(`/teacher-dashboard/assignments/${assignment.id}/submissions`)
}

const editAssignment = (assignment) => {
  router.push(`/teacher-dashboard/assignments/edit/${assignment.id}`)
}

onMounted(() => {
  loadAssignments()
})
</script>
