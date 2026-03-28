<template>
  <AdminPageTemplate
    title="Delete Institution"
    subtitle="Permanently remove institution record"
    icon="bi bi-building-x"
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

    <div v-else-if="!entityId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-building-x display-4"></i>
      </div>
      <h4 class="text-muted">No Institution Selected</h4>
      <p class="text-muted mb-4">Please select an institution from the list to delete.</p>
      <button @click="handleCancel" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Institution List
      </button>
    </div>

    <DeleteConfirmation
      v-else
      title="Delete Institution?"
      message="This action cannot be undone. This will permanently delete the institution and may affect all associated departments."
      :info-items="infoItems"
      confirm-button-text="Delete Institution"
      :loading="submitting"
      @confirm="handleDelete"
      @cancel="handleCancel"
    />
  </AdminPageTemplate>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, DeleteConfirmation, LoadingSpinner } from '@/components/shared/common'
import { useEntityDelete } from '@/composables/shared'
import { institutionService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Institutions', href: ADMIN_ROUTES.INSTITUTION_LIST.path },
  { name: 'Delete Institution' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.INSTITUTION_LIST.path) }
]

const {
  entityId,
  loading,
  submitting,
  alert,
  infoItems,
  handleDelete,
  handleCancel
} = useEntityDelete({
  entityName: 'Institution',
  service: {
    get: institutionService.getInstitutionById,
    delete: institutionService.deleteInstitution
  },
  listRoute: ADMIN_ROUTES.INSTITUTION_LIST.path,
  cacheKeys: ['institutions_list', 'institution*'],
  getInfoItems: (inst) => [
    { label: 'Code', value: inst.code },
    { label: 'Name', value: inst.name },
    { label: 'Type', value: inst.type || 'N/A' },
    { label: 'Location', value: inst.city || 'N/A' }
  ]
})
</script>

