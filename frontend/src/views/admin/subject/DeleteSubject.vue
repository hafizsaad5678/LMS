<template>
  <AdminPageTemplate
    title="Delete Subject"
    subtitle="Permanently remove subject record"
    icon="bi bi-journal-x"
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

    <LoadingSpinner v-if="loading" text="Loading subject details..." theme="admin" />

    <div v-else-if="!entityId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-journal-x display-4"></i>
      </div>
      <h4 class="text-muted">No Subject Selected</h4>
      <p class="text-muted mb-4">Please select a subject from the list to delete.</p>
      <button @click="handleCancel" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Subject List
      </button>
    </div>

    <DeleteConfirmation
      v-else
      title="Delete Subject?"
      message="This action cannot be undone. This will permanently delete the subject and may affect enrolled students and assigned teachers."
      :info-items="infoItems"
      confirm-button-text="Delete Subject"
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
import { subjectService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Subjects', href: ADMIN_ROUTES.SUBJECT_LIST.path },
  { name: 'Delete Subject' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.SUBJECT_LIST.path) }
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
  entityName: 'Subject',
  service: {
    get: subjectService.getSubjectById,
    delete: subjectService.deleteSubject
  },
  listRoute: ADMIN_ROUTES.SUBJECT_LIST.path,
  cacheKeys: ['subjects_list', 'subject*'],
  getInfoItems: (subject) => [
    { label: 'Code', value: subject.code },
    { label: 'Name', value: subject.name },
    { label: 'Credit Hours', value: subject.credit_hours || 'N/A' },
    { label: 'Semester', value: subject.semester_name || 'N/A' }
  ]
})
</script>

