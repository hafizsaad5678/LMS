<template>
  <AdminPageTemplate
    title="Delete Assignment"
    subtitle="Permanently remove assignment"
    icon="bi bi-trash-fill"
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

    <LoadingSpinner v-if="loading" text="Loading assignment details..." theme="admin" />

    <div v-else-if="!entityId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-trash display-4"></i>
      </div>
      <h4 class="text-muted">No Assignment Selected</h4>
      <p class="text-muted mb-4">Please select an assignment from the list to delete.</p>
      <button @click="handleCancel" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Assignment List
      </button>
    </div>

    <DeleteConfirmation
      v-else
      title="Delete Assignment?"
      message="This action cannot be undone. This will permanently delete the assignment and all associated submissions/grades."
      :info-items="infoItems"
      confirm-button-text="Delete Assignment"
      :loading="submitting"
      @confirm="handleDelete"
      @cancel="handleCancel"
    />
  </AdminPageTemplate>
</template>

<script setup>
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, DeleteConfirmation, LoadingSpinner } from '@/components/shared/common'
import { useEntityDelete } from '@/composables/shared'
import { assignmentService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { formatDate } from '@/utils/formatters'

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: ADMIN_ROUTES.ASSIGNMENTS.path },
  { name: 'Delete Assignment' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => handleCancel() }
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
  entityName: 'Assignment',
  service: {
    get: assignmentService.getAssignmentById,
    delete: assignmentService.deleteAssignment
  },
  listRoute: ADMIN_ROUTES.ASSIGNMENTS.path,
  cacheKeys: ['assignments_list', 'assignment*'],
  getInfoItems: (assignment) => [
    { label: 'Title', value: assignment.title },
    { label: 'Subject', value: assignment.subject_name || assignment.subject?.name || 'N/A' },
    { label: 'Due Date', value: assignment.due_date ? formatDate(assignment.due_date) : 'N/A' }
  ]
})
</script>
