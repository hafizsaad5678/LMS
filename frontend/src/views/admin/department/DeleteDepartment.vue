<template>
  <AdminPageTemplate
    title="Delete Department"
    subtitle="Permanently remove department record"
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

    <LoadingSpinner v-if="loading" text="Loading department details..." theme="admin" />

    <div v-else-if="!entityId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-building-x display-4"></i>
      </div>
      <h4 class="text-muted">No Department Selected</h4>
      <p class="text-muted mb-4">Please select a department from the list to delete.</p>
      <button @click="handleCancel" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Department List
      </button>
    </div>

    <DeleteConfirmation
      v-else
      title="Delete Department?"
      message="This action cannot be undone. This will permanently delete the department and may affect associated programs and teachers."
      :info-items="infoItems"
      confirm-button-text="Delete Department"
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
import { departmentService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Departments', href: ADMIN_ROUTES.DEPARTMENT_LIST.path },
  { name: 'Delete Department' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.DEPARTMENT_LIST.path) }
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
  entityName: 'Department',
  service: {
    get: departmentService.getDepartmentById,
    delete: departmentService.deleteDepartment
  },
  listRoute: ADMIN_ROUTES.DEPARTMENT_LIST.path,
  cacheKeys: ['departments_list', 'department*'],
  getInfoItems: (dept) => [
    { label: 'Code', value: dept.code },
    { label: 'Name', value: dept.name },
    { label: 'Head', value: dept.head_of_department || 'Not Assigned' }
  ]
})
</script>

