<template>
  <AdminPageTemplate
    title="Delete Teacher"
    subtitle="Permanently remove teacher record"
    icon="bi bi-person-x-fill"
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

    <LoadingSpinner v-if="loading" text="Loading teacher details..." theme="admin" />

    <div v-else-if="!entityId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-person-x display-4"></i>
      </div>
      <h4 class="text-muted">No Teacher Selected</h4>
      <p class="text-muted mb-4">Please select a teacher from the list to delete.</p>
      <button @click="handleCancel" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Teacher List
      </button>
    </div>

    <DeleteConfirmation
      v-else
      title="Delete Teacher Account?"
      message="This action cannot be undone. This will permanently delete the teacher account and remove all associated data."
      :info-items="infoItems"
      confirm-button-text="Delete Teacher"
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
import { teacherService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Teachers', href: ADMIN_ROUTES.TEACHER_LIST.path },
  { name: 'Delete Teacher' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.TEACHER_LIST.path) }
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
  entityName: 'Teacher',
  service: {
    get: teacherService.getTeacher,
    delete: teacherService.deleteTeacher
  },
  listRoute: ADMIN_ROUTES.TEACHER_LIST.path,
  cacheKeys: ['teachers_list', 'teacher*'],
  getInfoItems: (teacher) => [
    { label: 'Employee ID', value: teacher.employee_id },
    { label: 'Name', value: teacher.full_name },
    { label: 'Department', value: teacher.department_name },
    { label: 'Email', value: teacher.email }
  ]
})
</script>

