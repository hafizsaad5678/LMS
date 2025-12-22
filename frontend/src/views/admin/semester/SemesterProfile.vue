<template>
  <AdminPageTemplate
    :title="semester?.name || 'Semester Profile'"
    subtitle="View detailed semester information"
    icon="bi bi-calendar3"
    :breadcrumbs="breadcrumbs"
  >
    <!-- No ID provided -->
    <div v-if="!semesterId" class="text-center py-5">
      <i class="bi bi-calendar3 display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Semester</h4>
      <p class="text-muted">Choose a semester from the list to view its profile.</p>
      <button @click="router.push('/admin-dashboard/semesters')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Semester List
      </button>
    </div>

    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-admin"></div>
      <p class="text-muted mt-3">Loading semester details...</p>
    </div>

    <div v-else-if="!semester" class="text-center py-5">
      <i class="bi bi-calendar-x display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Semester Not Found</h4>
      <button @click="router.push('/admin-dashboard/semesters')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Semesters
      </button>
    </div>
    <div v-else>
      <!-- Info Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Basic Info</h6>
              <div class="mb-3">
                <label class="small text-muted d-block">Program</label>
                <div class="fw-semibold">{{ semester.program_name || 'N/A' }}</div>
              </div>
              <div class="mb-3">
                <label class="small text-muted d-block">Semester Number</label>
                <div class="fw-semibold">{{ semester.number }}</div>
              </div>
              <div class="mb-3">
                <label class="small text-muted d-block">Session</label>
                <div class="fw-semibold">{{ semester.session_name || 'N/A' }}</div>
              </div>
              <div class="mb-3">
                <label class="small text-muted d-block">Status</label>
                <span :class="['badge', semester.status === 'active' ? 'bg-success' : semester.status === 'completed' ? 'bg-info' : 'bg-secondary']">
                  {{ semester.status ? semester.status.charAt(0).toUpperCase() + semester.status.slice(1) : 'Unknown' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Timeline</h6>
              <div class="mb-3">
                <label class="small text-muted d-block">Start Date</label>
                <div class="fw-semibold">{{ formatDate(semester.start_date) }}</div>
              </div>
              <div class="mb-3">
                <label class="small text-muted d-block">End Date</label>
                <div class="fw-semibold">{{ formatDate(semester.end_date) }}</div>
              </div>
              <div class="mb-3">
                <label class="small text-muted d-block">Duration</label>
                <div class="fw-semibold">{{ getDuration(semester.start_date, semester.end_date) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Statistics</h6>
              <div class="d-flex align-items-center mb-3">
                <div class="stat-icon bg-info-light text-info rounded-circle me-3"><i class="bi bi-book"></i></div>
                <div>
                  <h3 class="mb-0 fw-bold">{{ subjects.length }}</h3>
                  <small class="text-muted">Subjects</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Subjects List -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
          <h5 class="card-title mb-0">Subjects</h5>
          <button @click="router.push({ name: 'AddSubject', query: { semester: semester.id } })" class="btn btn-sm btn-outline-primary" title="Add Subject">
            <i class="bi bi-plus-lg"></i> Add
          </button>
        </div>
        <div class="card-body p-0">
          <div v-if="subjects.length === 0" class="text-center py-5">
            <p class="text-muted">No subjects found for this semester.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="bg-light">
                <tr>
                  <th class="ps-4">Code</th>
                  <th>Subject Name</th>
                  <th>Credits</th>
                  <th class="text-end pe-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sub in subjects" :key="sub.id">
                  <td class="ps-4"><code>{{ sub.code }}</code></td>
                  <td class="fw-semibold">{{ sub.name }}</td>
                  <td>{{ sub.credit_hours }}</td>
                  <td class="text-end pe-4">
                    <button @click="$router.push(`/admin-dashboard/subjects/${sub.id}`)" class="btn btn-sm btn-outline-info">
                      <i class="bi bi-eye"></i> View
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { semesterService } from '@/services/semesterService'

const route = useRoute()
const router = useRouter()
const rawId = route.params.id
const semesterId = rawId && rawId !== 'profile' ? rawId : null

const loading = ref(true)
const semester = ref(null)
const subjects = ref([])

const breadcrumbs = computed(() => [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Semesters', href: '/admin-dashboard/semesters' },
  { name: semester.value?.name || 'Profile' }
])

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '-'

const getDuration = (start, end) => {
  if (!start || !end) return '-'
  const diff = new Date(end) - new Date(start)
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const months = Math.floor(days / 30)
  return months > 0 ? `${months} Months` : `${days} Days`
}

onMounted(async () => {
  if (!semesterId) {
    loading.value = false
    return
  }
  try {
    const [semRes, subRes] = await Promise.all([
      semesterService.getById(semesterId),
      semesterService.getSubjects(semesterId)
    ])
    semester.value = semRes
    subjects.value = subRes.results || subRes.data || subRes
  } catch (error) {
    console.error('Error loading semester profile:', error)
  } finally {
    loading.value = false
  }
})
</script>


