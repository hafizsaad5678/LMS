<template>
  <AdminPageTemplate
    title="Add New Department"
    subtitle="Create a new academic department"
    icon="bi bi-building-add"
    :breadcrumbs="breadcrumbs"
    :actions="pageActions"
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
        <DepartmentForm
          v-model="form"
          :institutions="institutions"
          :is-edit-mode="false"
          :submitting="submitting"
          @submit="onSubmit"
          @cancel="handleCancel"
        />
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { DepartmentForm } from '@/components/shared/forms'
import { useEntityForm, useCascadingDropdowns } from '@/composables/shared'
import { departmentService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Departments', href: ADMIN_ROUTES.DEPARTMENT_LIST.path },
  { name: 'Add Department' }
]

const pageActions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name }) }
]

const { alert, confirmDialog, submitting, showAlert, handleCancel, clearCaches } = useEntityForm({
  entityName: 'Department',
  listRoute: ADMIN_ROUTES.DEPARTMENT_LIST.path,
  cacheKeys: ['departments_list', 'departments_dropdown', 'institutions_list']
})

// Use cascading dropdowns composable
const { institutions, loadInstitutions } = useCascadingDropdowns()

const form = ref({
  name: '', code: '', institution: '', head_of_department: '', email: '', phone: '', description: ''
})

const onSubmit = async () => {
  if (!form.value.institution) {
    showAlert('error', 'Institution missing.', 'Error!')
    return
  }

  submitting.value = true
  try {
    const data = { ...form.value }
    await departmentService.createDepartment(data)
    clearCaches()
    showAlert('success', 'Department has been added successfully!', 'Success!')

    const sourceInstitutionId = route.query.institution
    const cameFromInstitutionProfile = route.query.source === 'institution-profile'
    setTimeout(() => {
      if (cameFromInstitutionProfile && sourceInstitutionId) {
        router.push({
          name: ADMIN_ROUTES.INSTITUTION_PROFILE.name,
          params: { id: sourceInstitutionId },
          query: { refresh: Date.now() }
        })
        return
      }

      router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name, query: { refresh: Date.now() } })
    }, 1500)
  } catch (error) {
    const institutionError = error.response?.data?.institution
    const firstInstitutionError = Array.isArray(institutionError) ? institutionError[0] : institutionError
    const fallbackMessage = error.response?.data?.detail || 'Failed to add department.'
    showAlert('error', firstInstitutionError || fallbackMessage, 'Error!')
  } finally { submitting.value = false }
}

onMounted(async () => {
  await loadInstitutions()

  const institutionFromQuery = route.query.institution
  if (institutionFromQuery) {
    form.value.institution = String(institutionFromQuery)
  }
})
</script>

