<template>
  <AdminPageTemplate
    title="Edit Institution"
    subtitle="Update institution information"
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

    <LoadingSpinner v-if="loading" text="Loading institution details..." theme="admin" />

    <div v-else-if="!institutionId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-bank2 display-4"></i>
      </div>
      <h4 class="text-muted">No Institution Selected</h4>
      <p class="text-muted mb-4">Please select an institution from the list to edit.</p>
      <button @click="router.push(ADMIN_ROUTES.INSTITUTION_LIST.path)" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Institution List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-10">
        <InstitutionForm
          v-model="form"
          :is-edit-mode="true"
          :submitting="submitting"
          @submit="handleSubmit"
          @cancel="handleCancel"
        />
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, LoadingSpinner } from '@/components/shared/common'
import { InstitutionForm } from '@/components/shared/forms'
import { useEntityForm } from '@/composables/shared'
import { institutionService } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const institutionId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Institutions', href: ADMIN_ROUTES.INSTITUTION_LIST.path },
  { name: 'Edit Institution' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-outline-secondary', onClick: () => router.push(ADMIN_ROUTES.INSTITUTION_LIST.path) }
]

const { alert, loading, submitting, showAlert, goToList } = useEntityForm({
  entityName: 'Institution',
  listRoute: ADMIN_ROUTES.INSTITUTION_LIST.path,
  cacheKeys: ['institutions_list']
})

loading.value = true

const form = ref({
  name: '', short_name: '', code: '', established_year: null, website: '',
  email: '', phone: '', address: '', city: '', state: '', postal_code: '',
  country: 'Pakistan', description: '', is_active: true
})

const loadInstitution = async () => {
  const id = institutionId.value
  if (!id) { loading.value = false; return }
  loading.value = true
  try {
    const inst = await institutionService.getInstitutionById(id)
    Object.assign(form.value, {
      name: inst.name || '', short_name: inst.short_name || '', code: inst.code || '',
      established_year: inst.established_year || null, website: inst.website || '',
      email: inst.email || '', phone: inst.phone || '', address: inst.address || '',
      city: inst.city || '', state: inst.state || '', postal_code: inst.postal_code || '',
      country: inst.country || 'Pakistan', description: inst.description || '',
      is_active: inst.is_active !== false
    })
  } catch (error) {
    showAlert('error', 'Failed to load institution', 'Error')
    setTimeout(() => router.push(ADMIN_ROUTES.INSTITUTION_LIST.path), 2000)
  } finally { loading.value = false }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    Object.keys(data).forEach(key => {
      if ((data[key] === '' || data[key] === null) && key !== 'is_active') delete data[key]
    })
    await institutionService.updateInstitution(institutionId.value, data)
    cacheService.clear('institutions_list')
    cacheService.clearPattern('institution')
    showAlert('success', 'Institution updated successfully!', 'Success!')
    setTimeout(() => router.push(ADMIN_ROUTES.INSTITUTION_LIST.path), 1500)
  } catch (error) {
    showAlert('error', error.response?.data?.detail || 'Failed to update institution.', 'Error!')
  } finally { submitting.value = false }
}

const handleCancel = () => goToList()

watch(() => route.params.id, (newId) => { if (newId) loadInstitution() }, { immediate: false })
onMounted(loadInstitution)
</script>


