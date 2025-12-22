<template>
  <TeacherPageTemplate
    title="My Classes"
    subtitle="Manage your assigned classes and subjects"
    icon="bi bi-book-half"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <template #stats>
      <div class="row g-3 mb-4">
        <div class="col-md-3 col-6">
          <div class="stat-card bg-gradient-primary text-white">
            <i class="bi bi-book stat-icon"></i>
            <div class="stat-content">
              <h3>{{ classes.length }}</h3>
              <p>Total Classes</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card bg-gradient-success text-white">
            <i class="bi bi-people stat-icon"></i>
            <div class="stat-content">
              <h3>{{ totalStudents }}</h3>
              <p>Total Students</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card bg-gradient-warning text-white">
            <i class="bi bi-calendar-event stat-icon"></i>
            <div class="stat-content">
              <h3>{{ todayClasses }}</h3>
              <p>Classes Today</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card bg-gradient-info text-white">
            <i class="bi bi-clipboard-check stat-icon"></i>
            <div class="stat-content">
              <h3>{{ pendingAssignments }}</h3>
              <p>Pending Reviews</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #filters>
      <SearchFilter
        v-model="searchQuery"
        :show-status-filter="false"
        search-placeholder="Search classes..."
        @refresh="loadClasses"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3">
            <label class="form-label small fw-semibold">Semester</label>
            <select v-model="filters.semester" class="form-select">
              <option value="">All Semesters</option>
              <option value="1">Semester 1</option>
              <option value="2">Semester 2</option>
              <option value="3">Semester 3</option>
              <option value="4">Semester 4</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="text-muted mt-3">Loading classes...</p>
    </div>

    <div v-else-if="filteredClasses.length === 0" class="text-center py-5">
      <i class="bi bi-book display-1 text-muted"></i>
      <h4 class="text-muted mt-3">No Classes Found</h4>
      <p class="text-muted">You don't have any classes assigned yet.</p>
    </div>

    <div v-else class="row g-4">
      <div v-for="cls in filteredClasses" :key="cls.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="avatar-subject rounded">
                <i class="bi bi-book-fill"></i>
              </div>
              <span class="badge bg-teacher-light text-teacher">{{ cls.semester }}</span>
            </div>
            
            <h5 class="fw-bold mb-2">{{ cls.subject_name }}</h5>
            <p class="text-muted small mb-3">{{ cls.subject_code }}</p>
            
            <div class="d-flex align-items-center gap-3 mb-3 text-muted small">
              <span><i class="bi bi-people me-1"></i>{{ cls.student_count }} Students</span>
              <span><i class="bi bi-clock me-1"></i>{{ cls.credit_hours }}h</span>
            </div>
            
            <div class="d-flex gap-2">
              <button @click="viewClass(cls)" class="btn btn-sm btn-teacher-primary flex-grow-1">
                <i class="bi bi-eye me-1"></i>View
              </button>
              <button @click="markAttendance(cls)" class="btn btn-sm btn-teacher-outline">
                <i class="bi bi-calendar-check"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TeacherPageTemplate from '@/components/navbar/TeacherPageTemplate.vue'
import SearchFilter from '@/components/common/SearchFilter.vue'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: '/teacher-dashboard' },
  { name: 'My Classes' }
]

const actions = [
  { label: 'View Schedule', icon: 'bi bi-calendar3', variant: 'btn-teacher-outline', onClick: () => router.push('/teacher-dashboard/schedule/class') }
]

const loading = ref(false)
const searchQuery = ref('')
const filters = ref({ semester: '' })

const classes = ref([
  { id: 1, subject_name: 'Data Structures', subject_code: 'CS-201', semester: 'Semester 3', student_count: 45, credit_hours: 3 },
  { id: 2, subject_name: 'Database Systems', subject_code: 'CS-301', semester: 'Semester 5', student_count: 38, credit_hours: 4 },
  { id: 3, subject_name: 'Web Development', subject_code: 'CS-202', semester: 'Semester 3', student_count: 42, credit_hours: 3 },
  { id: 4, subject_name: 'Operating Systems', subject_code: 'CS-302', semester: 'Semester 5', student_count: 35, credit_hours: 4 }
])

const totalStudents = computed(() => classes.value.reduce((sum, cls) => sum + cls.student_count, 0))
const todayClasses = computed(() => 3)
const pendingAssignments = computed(() => 12)

const filteredClasses = computed(() => {
  let result = classes.value

  if (searchQuery.value) {
    result = result.filter(cls =>
      cls.subject_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      cls.subject_code.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (filters.value.semester) {
    result = result.filter(cls => cls.semester.includes(filters.value.semester))
  }

  return result
})

const loadClasses = () => {
  loading.value = true
  setTimeout(() => loading.value = false, 500)
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value.semester = ''
}

const viewClass = (cls) => {
  router.push(`/teacher-dashboard/classes/${cls.id}`)
}

const markAttendance = (cls) => {
  router.push(`/teacher-dashboard/attendance/mark?class=${cls.id}`)
}

onMounted(() => {
  loadClasses()
})
</script>
