<template>
  <AdminPageTemplate
    title="Add New Course"
    subtitle="Create a new academic program/course"
    icon="bi bi-mortarboard-fill"
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
      <div class="col-lg-8">
        <CourseForm
          v-model="form"
          :departments="departments"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { CourseForm } from '@/components/shared/forms'
import { useEntityForm, useCascadingDropdowns } from '@/composables/shared'
import { programService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Courses', href: ADMIN_ROUTES.COURSE_LIST.path },
  { name: 'Add Course' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.COURSE_LIST.path) }
]

const { alert, confirmDialog, submitting, showAlert, handleCancel, clearCaches } = useEntityForm({
  entityName: 'Course',
  listRoute: ADMIN_ROUTES.COURSE_LIST.path,
  cacheKeys: ['courses_list', 'programs_dropdown']
})

// Use cascading dropdowns composable
const { departments, loadDepartments } = useCascadingDropdowns()

const form = ref({ name: '', code: '', department: '', duration_years: 4, description: '' })

const handleSubmit = async () => {
  if (!form.value.department) {
    showAlert('error', 'Department missing.', 'Error!')
    return
  }

  submitting.value = true
  try {
    const data = { ...form.value }
    await programService.createProgram(data)
    clearCaches()
    showAlert('success', 'Course has been added successfully!', 'Success!')
    setTimeout(() => router.push({ path: ADMIN_ROUTES.COURSE_LIST.path, query: { refresh: Date.now() } }), 1500)
  } catch (error) {
    const departmentError = error.response?.data?.department
    const firstDepartmentError = Array.isArray(departmentError) ? departmentError[0] : departmentError
    const fallbackMessage = error.response?.data?.detail || error.response?.data?.code?.[0] || 'Failed to add course.'
    showAlert('error', firstDepartmentError || fallbackMessage, 'Error!')
  } finally { submitting.value = false }
}

onMounted(loadDepartments)
</script>

