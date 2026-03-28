<template>
  <AdminPageTemplate
    title="Delete Course"
    subtitle="Permanently remove course/program record"
    icon="bi bi-book-x"
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

    <LoadingSpinner v-if="loading" text="Loading course details..." theme="admin" />

    <div v-else-if="!entityId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-book-x display-4"></i>
      </div>
      <h4 class="text-muted">No Course Selected</h4>
      <p class="text-muted mb-4">Please select a course from the list to delete.</p>
      <button @click="handleCancel" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Course List
      </button>
    </div>

    <DeleteConfirmation
      v-else
      title="Delete Course?"
      message="This action cannot be undone. This will permanently delete the course and may affect associated students and subjects."
      :info-items="infoItems"
      confirm-button-text="Delete Course"
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
import { programService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Courses', href: ADMIN_ROUTES.COURSE_LIST.path },
  { name: 'Delete Course' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.COURSE_LIST.path) }
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
  entityName: 'Course',
  service: {
    get: programService.getProgramById,
    delete: programService.deleteProgram
  },
  listRoute: ADMIN_ROUTES.COURSE_LIST.path,
  cacheKeys: ['courses_list', 'programs_list', 'course*', 'program*'],
  getInfoItems: (course) => [
    { label: 'Code', value: course.code },
    { label: 'Name', value: course.name },
    { label: 'Department', value: course.department_name || 'N/A' },
    { label: 'Duration', value: course.duration_years ? `${course.duration_years} Years` : 'N/A' }
  ]
})
</script>

