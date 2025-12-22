<template>
  <AdminPageTemplate
    title="Institution Profile"
    :subtitle="institution.name || 'Loading...'"
    icon="bi bi-bank2"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="alert.show = false"
    />

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-admin" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading institution details...</p>
    </div>

    <!-- No ID provided -->
    <div v-else-if="!institutionId" class="text-center py-5">
      <i class="bi bi-bank2 display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select an Institution</h4>
      <p class="text-muted">Choose an institution from the list to view its profile.</p>
      <button @click="router.push('/admin-dashboard/institution')" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Institution List
      </button>
    </div>

    <div v-else>
      <!-- Header Card -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="avatar-xl bg-admin text-white rounded-circle d-flex align-items-center justify-content-center">
                <i class="bi bi-bank2 display-5"></i>
              </div>
            </div>
            <div class="col">
              <h2 class="mb-1 fw-bold">{{ institution.name }}</h2>
              <div class="d-flex flex-wrap gap-3 text-muted">
                <span><i class="bi bi-hash me-1"></i>{{ institution.code }}</span>
                <span v-if="institution.short_name"><i class="bi bi-type me-1"></i>{{ institution.short_name }}</span>
                <span v-if="institution.city"><i class="bi bi-geo-alt me-1"></i>{{ institution.city }}</span>
                <span v-if="institution.established_year"><i class="bi bi-calendar me-1"></i>Est. {{ institution.established_year }}</span>
              </div>
            </div>
            <div class="col-auto">
              <span :class="['badge fs-6', institution.is_active ? 'bg-success' : 'bg-secondary']">
                {{ institution.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Row -->
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="stat-icon bg-admin-light text-admin rounded-circle mx-auto mb-3">
                <i class="bi bi-building"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ departments.length }}</h3>
              <small class="text-muted">Departments</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="stat-icon bg-success-light text-success rounded-circle mx-auto mb-3">
                <i class="bi bi-mortarboard"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ totalPrograms }}</h3>
              <small class="text-muted">Programs</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="stat-icon bg-info-light text-info rounded-circle mx-auto mb-3">
                <i class="bi bi-people"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ totalStudents }}</h3>
              <small class="text-muted">Students</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="stat-icon bg-warning-light text-warning rounded-circle mx-auto mb-3">
                <i class="bi bi-person-workspace"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ totalTeachers }}</h3>
              <small class="text-muted">Teachers</small>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Contact & Info -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom">
              <h5 class="card-title mb-0 fw-semibold">
                <i class="bi bi-info-circle me-2 text-admin"></i>Institution Details
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-6">
                  <label class="text-muted small">Email</label>
                  <p class="mb-0 fw-medium">{{ institution.email || '-' }}</p>
                </div>
                <div class="col-6">
                  <label class="text-muted small">Phone</label>
                  <p class="mb-0 fw-medium">{{ institution.phone || '-' }}</p>
                </div>
                <div class="col-6">
                  <label class="text-muted small">Website</label>
                  <p class="mb-0 fw-medium">
                    <a v-if="institution.website" :href="institution.website" target="_blank" class="text-admin">
                      {{ institution.website }}
                    </a>
                    <span v-else>-</span>
                  </p>
                </div>
                <div class="col-6">
                  <label class="text-muted small">Country</label>
                  <p class="mb-0 fw-medium">{{ institution.country || '-' }}</p>
                </div>
                <div class="col-12">
                  <label class="text-muted small">Full Address</label>
                  <p class="mb-0 fw-medium">{{ fullAddress || '-' }}</p>
                </div>
                <div class="col-12" v-if="institution.description">
                  <label class="text-muted small">Description</label>
                  <p class="mb-0">{{ institution.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Departments List -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0 fw-semibold">
                <i class="bi bi-building me-2 text-success"></i>Departments
              </h5>
              <button @click="router.push('/admin-dashboard/departments/add')" class="btn btn-sm btn-outline-success">
                <i class="bi bi-plus"></i> Add
              </button>
            </div>
            <div class="card-body p-0">
              <div v-if="departments.length === 0" class="text-center py-4 text-muted">
                <i class="bi bi-building display-4"></i>
                <p class="mt-2 mb-0">No departments yet</p>
              </div>
              <ul v-else class="list-group list-group-flush">
                <li v-for="dept in departments" :key="dept.id" class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-0">{{ dept.name }}</h6>
                    <small class="text-muted">{{ dept.code }}</small>
                  </div>
                  <button @click="router.push(`/admin-dashboard/departments/${dept.id}`)" class="btn btn-sm btn-outline-primary">
                    View
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { institutionService } from '@/services/institutionService'

const router = useRouter()
const route = useRoute()
const rawId = route.params.id
const institutionId = rawId && rawId !== 'profile' ? rawId : null

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Institutions', href: '/admin-dashboard/institution' },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-outline-secondary', onClick: () => router.push('/admin-dashboard/institution') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(true)
const institution = ref({})
const departments = ref([])

// Computed
const fullAddress = computed(() => {
  const parts = [institution.value.address, institution.value.city, institution.value.state, institution.value.postal_code]
  return parts.filter(Boolean).join(', ')
})

const totalPrograms = computed(() => departments.value.reduce((sum, d) => sum + (d.program_count || 0), 0))
const totalStudents = computed(() => departments.value.reduce((sum, d) => sum + (d.student_count || 0), 0))
const totalTeachers = computed(() => departments.value.reduce((sum, d) => sum + (d.teacher_count || 0), 0))

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadInstitution = async () => {
  loading.value = true
  try {
    institution.value = await institutionService.getInstitutionById(institutionId)
    
    // Load departments
    try {
      const deptData = await institutionService.getDepartments(institutionId)
      departments.value = Array.isArray(deptData) ? deptData : (deptData.results || [])
    } catch (e) {
      console.warn('Could not load departments:', e)
    }
  } catch (error) {
    console.error('Error loading institution:', error)
    showAlert('error', 'Failed to load institution', 'Error')
    setTimeout(() => router.push('/admin-dashboard/institution'), 2000)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (institutionId) loadInstitution()
  else loading.value = false
})
</script>


