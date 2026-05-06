<template>
  <AdminPageTemplate 
    title="Institution Profile Settings" 
    subtitle="Configure branding, principal information, and public profile details" 
    icon="bi bi-gear-fill" 
    :breadcrumbs="breadcrumbs"
  >
    <AlertMessage 
      v-if="alert.show" 
      :type="alert.type" 
      :message="alert.message" 
      :title="alert.title" 
      :auto-close="true" 
      @close="alert.show = false" 
    />

    <div class="row g-4">
      <!-- Institution Selector (If multiple) -->
      <div v-if="institutions.length > 1" class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body p-3">
            <div class="d-flex align-items-center gap-3">
              <label class="form-label mb-0 fw-semibold text-muted">Active Institution:</label>
              <select v-model="selectedInstitutionId" class="form-select w-auto min-w-200">
                <option v-for="inst in institutions" :key="inst.id" :value="inst.id">
                  {{ inst.name }} ({{ inst.code }})
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Settings Form -->
      <div class="col-lg-12">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-admin" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading institution data...</p>
        </div>

        <InstitutionSettingsForm 
          v-else-if="selectedInstitution"
          v-model="selectedInstitution"
          :submitting="submitting"
          @submit="handleUpdate"
          @cancel="resetData"
        />

        <div v-else class="text-center py-5 card border-0 shadow-sm">
          <div class="card-body">
            <i class="bi bi-bank2 display-1 text-muted"></i>
            <h5 class="mt-3 text-muted">No Institution Selected</h5>
            <p>Please select an institution to configure its profile.</p>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage } from '@/components/shared/common'
import { InstitutionSettingsForm } from '@/components/shared/forms'
import { institutionService, toFormData } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { useAlert } from '@/composables/shared'

const router = useRouter()
const { alert, showAlert } = useAlert()
const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Management' },
  { name: 'Profile Settings' }
]

const loading = ref(true)
const submitting = ref(false)
const institutions = ref([])
const selectedInstitutionId = ref(null)
const selectedInstitution = ref(null)

// For tracking changes and resetting
const originalData = ref(null)

const loadInstitutions = async () => {
  loading.value = true
  try {
    const response = await institutionService.getAllInstitutions()
    institutions.value = Array.isArray(response) ? response : (response.results || [])
    
    if (institutions.value.length > 0) {
      // Default to Govt Graduate College if it exists, else first institution
      const defaultInst = institutions.value.find(i => i.name.toLowerCase().includes('govt graduate')) || institutions.value[0]
      selectedInstitutionId.value = defaultInst.id
    }
  } catch (error) {
    console.error('Error loading institutions:', error)
    showAlert('error', 'Failed to load institutions', 'Error')
  } finally {
    loading.value = false
  }
}

const loadInstitutionDetails = async (id, { silent = false } = {}) => {
  if (!id) return
  if (!silent) loading.value = true
  try {
    const data = await institutionService.getInstitutionById(id)
    selectedInstitution.value = { ...data }
    originalData.value = JSON.parse(JSON.stringify(data))
  } catch (error) {
    console.error('Error loading institution details:', error)
    showAlert('error', 'Failed to load institution details', 'Error')
  } finally {
    if (!silent) loading.value = false
  }
}

const handleUpdate = async () => {
  if (!selectedInstitution.value) return
  
  submitting.value = true
  try {
    const data = { ...selectedInstitution.value }
    
    // Don't send existing image URLs as strings - DRF expects Files or null
    // If it's a string, it means the image hasn't changed.
    if (typeof data.logo === 'string') delete data.logo
    if (typeof data.cover_image === 'string') delete data.cover_image
    if (typeof data.principal_image === 'string') delete data.principal_image
    
    // Clean up featured admissions images if they are still strings (existing URLs)
    if (Array.isArray(data.featured_admissions)) {
      data.featured_admissions = data.featured_admissions.map(card => {
        const cleanedCard = { ...card }
        if (typeof cleanedCard.image === 'string') {
          delete cleanedCard.image
        }
        return cleanedCard
      })
    }
    
    // Convert to FormData for image handling
    const formData = toFormData(data)
    
    await institutionService.updateInstitution(selectedInstitution.value.id, formData)
    
    // Navigate back to Admissions Management after successful save
    router.push(ADMIN_ROUTES.ADMISSIONS_MANAGEMENT.path)
  } catch (error) {
    console.error('Error updating institution:', error)
    showAlert('error', 'Failed to update institution settings. Please check all fields.', 'Update Error')
  } finally {
    submitting.value = false
  }
}

const resetData = () => {
  if (originalData.value) {
    selectedInstitution.value = JSON.parse(JSON.stringify(originalData.value))
    showAlert('info', 'Changes discarded', 'Reset')
  }
}

watch(selectedInstitutionId, (newId) => {
  if (newId) {
    loadInstitutionDetails(newId)
  }
})

onMounted(loadInstitutions)
</script>

<style scoped>
.min-w-200 {
  min-width: 200px;
}
</style>
