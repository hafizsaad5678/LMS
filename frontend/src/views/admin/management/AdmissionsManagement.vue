<template>
  <AdminPageTemplate 
    title="Admissions Management" 
    subtitle="Monitor open and closed admissions and promotional cards" 
    icon="bi bi-megaphone-fill" 
    :breadcrumbs="breadcrumbs"
  >
    <div class="row g-4">
      <!-- Institution Selector -->
      <div v-if="institutions.length > 0" class="col-12">
        <div class="card border-0 shadow-sm mb-2">
          <div class="card-body p-3">
            <div class="d-flex align-items-center gap-3">
              <label class="form-label mb-0 fw-semibold text-muted">Select Institution:</label>
              <select v-model="selectedInstitutionId" class="form-select w-auto min-w-200" @change="loadInstitutionData">
                <option v-for="inst in institutions" :key="inst.id" :value="inst.id">
                  {{ inst.name }} ({{ inst.code }})
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12">
        <!-- Dashboard Tabs / Actions -->
        <div class="d-flex flex-wrap gap-2 mb-4" id="admissionsTab" role="tablist">
          <button class="btn-admin-primary active" id="academic-tab" data-bs-toggle="tab" data-bs-target="#academic" type="button" role="tab">Program Admissions</button>
          <button class="btn-admin-primary" id="promo-tab" data-bs-toggle="tab" data-bs-target="#promo" type="button" role="tab">Promotional Ads</button>
          <router-link :to="{ name: 'InstitutionSettings' }" class="btn-admin-primary text-decoration-none">
            <i class="bi bi-gear-fill me-1"></i> Manage Settings
          </router-link>
        </div>

        <div class="tab-content" id="admissionsTabContent">
          <!-- Academic Sessions Tab -->
          <div class="tab-pane fade show active" id="academic" role="tabpanel">
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Academic Sessions</h5>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Program</th>
                        <th>Session Name</th>
                        <th>Status</th>
                        <th>Admissions Start</th>
                        <th>Admissions End</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="session in filteredSessions" :key="session.id">
                        <td>
                          <div class="fw-medium">{{ session.program_name }}</div>
                          <small class="text-muted">{{ session.department_name }}</small>
                        </td>
                        <td>{{ session.session_name || session.start_year }}</td>
                        <td>
                           <span class="badge" :class="getAdmissionStatusColor(session)">
                            {{ getAdmissionStatus(session) }}
                          </span>
                        </td>
                        <td>{{ session.admission_start_date || 'N/A' }}</td>
                        <td>{{ session.admission_end_date || 'N/A' }}</td>
                      </tr>
                      <tr v-if="filteredSessions.length === 0 && !loadingSessions">
                        <td colspan="5" class="text-center py-4 text-muted">No academic sessions found</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- Promotional Ads Tab -->
          <div class="tab-pane fade" id="promo" role="tabpanel">
            <div class="card border-0 shadow-sm">
               <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Featured Promotional Cards</h5>
                <div class="d-flex gap-2">
                  <router-link :to="ADMIN_ROUTES.SESSION_ADD.path" class="btn btn-sm btn-admin-primary">
                    Manage Sessions
                  </router-link>
                  <router-link :to="ADMIN_ROUTES.INSTITUTION_SETTINGS.path" class="btn btn-sm btn-admin-primary">
                    Manage Settings
                  </router-link>
                </div>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Title / Image</th>
                        <th>Badge Text</th>
                        <th>Status</th>
                        <th>Start Date</th>
                        <th>End Date</th>
                        <th class="text-end">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="card in promotionalCards" :key="card.id">
                        <td>
                          <div class="d-flex align-items-center">
                            <img v-if="card.image" :src="card.image" class="rounded me-3 object-fit-cover shadow-sm" width="48" height="36" alt="Ad">
                            <div class="bg-light rounded me-3 d-flex align-items-center justify-content-center border" v-else style="width: 48px; height: 36px;">
                              <i class="bi bi-image text-muted"></i>
                            </div>
                            <div class="fw-medium text-dark">{{ card.title }}</div>
                          </div>
                        </td>
                        <td><span class="badge bg-light text-dark border">{{ card.badge_text || 'N/A' }}</span></td>
                        <td>
                           <span class="badge" :class="getPromoCardClosedStatus(card) ? 'bg-danger' : 'bg-success'">
                            {{ getPromoCardClosedStatus(card) ? 'Closed' : 'Open' }}
                          </span>
                        </td>
                        <td>{{ card.admission_start_date || 'N/A' }}</td>
                        <td>{{ card.admission_end_date || 'N/A' }}</td>
                        <td class="text-end">
                          <button class="btn btn-sm btn-admin-outline rounded-pill" @click="handlePreview(card.image)" :disabled="!card.image">
                            <i class="bi bi-eye me-1"></i> Preview Ad
                          </button>
                        </td>
                      </tr>
                      <tr v-if="promotionalCards.length === 0 && !loadingInstitutions">
                        <td colspan="6" class="text-center py-5">
                          <i class="bi bi-card-image display-4 text-muted mb-3 d-block"></i>
                          <h5 class="text-muted">No Promotional Cards</h5>
                          <p class="mb-0">Go to Institution Settings to add promotional admission cards.</p>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Preview Modal -->
    <Teleport to="body">
      <div class="modal fade" id="adminPreviewModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered">
          <div class="modal-content border-0 bg-transparent shadow-none">
            <div class="modal-header border-0 pb-0 justify-content-end position-relative z-3">
              <button type="button" class="btn btn-dark rounded-circle p-0 d-flex align-items-center justify-content-center opacity-75 shadow" data-bs-dismiss="modal" aria-label="Close" style="width: 40px; height: 40px; position: absolute; right: 0px; top: 0px;">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div class="modal-body text-center p-0 mt-2">
              <img :src="previewImageUrl" class="img-fluid rounded-3 shadow-lg" alt="Promotional Ad" style="max-height: 85vh; object-fit: contain;">
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Modal } from 'bootstrap'
import { AdminPageTemplate } from '@/components/shared/panels'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { sessionService, institutionService } from '@/services/shared'
import { useAlert } from '@/composables/shared'
import AdmissionCard from '@/components/shared/cards/AdmissionCard.vue'

const { alert, showAlert } = useAlert()
const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Management' },
  { name: 'Admissions' }
]

const sessions = ref([])
const loadingSessions = ref(true)

const previewImageUrl = ref('')

const handlePreview = (image) => {
  if (image) {
    previewImageUrl.value = image;
    const modalEl = document.getElementById('adminPreviewModal')
    if (modalEl) {
      const modal = Modal.getInstance(modalEl) || new Modal(modalEl)
      modal.show()
    }
  }
}

const handleApply = () => {
  showAlert('info', 'This is a preview of the admission card. Students can apply via the public admissions portal.', 'Admin Preview')
}

const institutions = ref([])
const selectedInstitutionId = ref(null)
const promotionalCards = ref([])
const loadingInstitutions = ref(true)

const filteredSessions = computed(() => {
  if (!selectedInstitutionId.value) return sessions.value
  // Filter sessions based on selected institution's department
  return sessions.value.filter(session => session.institution_id === selectedInstitutionId.value)
})

const loadInstitutions = async () => {
  loadingInstitutions.value = true
  try {
    const instRes = await institutionService.getAllInstitutions()
    institutions.value = instRes.results || instRes || []
    
    if (institutions.value.length > 0) {
      const defaultInst = institutions.value.find(i => i.name.toLowerCase().includes('govt graduate')) || institutions.value[0]
      selectedInstitutionId.value = defaultInst.id
      await loadInstitutionData()
    }
  } catch (error) {
    console.error('Error loading institutions:', error)
    showAlert('error', 'Failed to load institutions', 'Error')
  } finally {
    loadingInstitutions.value = false
  }
}

const loadInstitutionData = async () => {
  if (!selectedInstitutionId.value) return
  loadingInstitutions.value = true
  try {
    const instDetails = await institutionService.getInstitutionById(selectedInstitutionId.value)
    promotionalCards.value = instDetails.featured_admissions || []
  } catch (error) {
    console.error('Error loading institution details:', error)
  } finally {
    loadingInstitutions.value = false
  }
}

const loadData = async () => {
  loadingSessions.value = true
  try {
    // Load sessions
    const sessionRes = await sessionService.getSessions()
    sessions.value = sessionRes.results || sessionRes || []
  } catch (error) {
    console.error('Error loading data:', error)
    showAlert('error', 'Failed to load admissions data', 'Error')
  } finally {
    loadingSessions.value = false
  }
  
  await loadInstitutions()
}

const getAdmissionStatus = (session) => {
  const today = new Date().toISOString().split('T')[0];
  const start = session.admission_start_date;
  const end = session.admission_end_date;

  if (start && end) {
    if (today < start) return 'Upcoming';
    if (today > end) return 'Closed';
    return 'Open';
  }
  if (start && !end) {
    if (today < start) return 'Upcoming';
    return 'Open';
  }
  if (end && !start) {
    if (today > end) return 'Closed';
    return 'Open';
  }
  return 'Not Configured';
}

const getPromoCardClosedStatus = (card) => {
  if (card.is_active === false) return true;
  
  const today = new Date().toISOString().split('T')[0];
  if (card.admission_start_date && today < card.admission_start_date) return true;
  if (card.admission_end_date && today > card.admission_end_date) return true;
  
  return false;
}

const getAdmissionStatusColor = (session) => {
  const status = getAdmissionStatus(session);
  switch (status) {
    case 'Open': return 'bg-success';
    case 'Closed': return 'bg-danger';
    case 'Upcoming': return 'bg-info text-dark';
    default: return 'bg-secondary';
  }
}

onMounted(() => {
  loadData()
})
</script>
