<template>
  <AdminPageTemplate
    title="Add New Institution"
    subtitle="Register a new institution in the system"
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

    <ConfirmDialog
      v-model="confirmDialog.show"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      :type="confirmDialog.type"
      theme="admin"
      confirm-text="Discard"
      @confirm="() => confirmDialog.onConfirm?.()"
      @cancel="confirmDialog.show = false"
    />

    <div class="row justify-content-center">
      <div class="col-lg-10">
        <InstitutionForm
          v-model="form"
          :is-edit-mode="false"
          :submitting="submitting"
          @submit="handleSubmit"
          @cancel="handleCancel"
        />
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { InstitutionForm } from '@/components/shared/forms'
import { useEntityForm } from '@/composables/shared'
import { institutionService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Institutions', href: ADMIN_ROUTES.INSTITUTION_LIST.path },
  { name: 'Add Institution' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-outline-secondary', onClick: () => router.push(ADMIN_ROUTES.INSTITUTION_LIST.path) }
]

const { alert, confirmDialog, submitting, showAlert, handleCancel, clearCaches } = useEntityForm({
  entityName: 'Institution',
  listRoute: ADMIN_ROUTES.INSTITUTION_LIST.path,
  cacheKeys: ['institutions_list']
})

const form = ref({
  name: '', short_name: '', code: '', established_year: null, website: '',
  email: '', phone: '', address: '', city: '', state: '', postal_code: '',
  country: 'Pakistan', description: '', is_active: true
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    Object.keys(data).forEach(key => {
      if (data[key] === '' || data[key] === null) {
        if (key !== 'is_active') delete data[key]
      }
    })
    await institutionService.createInstitution(data)
    clearCaches()
    showAlert('success', 'Institution has been added successfully!', 'Success!')
    setTimeout(() => router.push({ path: ADMIN_ROUTES.INSTITUTION_LIST.path, query: { refresh: Date.now() } }), 1500)
  } catch (error) {
    const msg = error.response?.data?.detail || error.response?.data?.code?.[0] || 'Failed to add institution.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}
</script>

