<template>
  <AdminPageTemplate
    title="Edit Department"
    subtitle="Update department information"
    icon="bi bi-building-gear"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <ConfirmDialog
      v-model="confirmDialog.show"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      :type="confirmDialog.type"
      theme="admin"
      confirm-text="Discard"
      cancel-text="Keep Editing"
      @confirm="() => confirmDialog.onConfirm?.()"
      @cancel="confirmDialog.show = false"
    />

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

    <div v-else-if="!departmentId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-building display-4"></i>
      </div>
      <h4 class="text-muted">No Department Selected</h4>
      <p class="text-muted mb-4">Please select a department from the list to edit.</p>
      <button @click="router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name })" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Department List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <DepartmentForm
          v-model="form"
          :institutions="institutions"
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
import { AlertMessage, ConfirmDialog, LoadingSpinner } from '@/components/shared/common'
import { DepartmentForm } from '@/components/shared/forms'
import { useEntityForm, useCascadingDropdowns } from '@/composables/shared'
import { departmentService } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const departmentId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Departments', href: ADMIN_ROUTES.DEPARTMENT_LIST.path },
  { name: 'Edit Department' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name }) }
]

const { alert, confirmDialog, loading, submitting, showAlert, handleCancel } = useEntityForm({
  entityName: 'Department',
  listRoute: ADMIN_ROUTES.DEPARTMENT_LIST.path,
  cacheKeys: ['departments_list', 'departments_dropdown']
})

// Use cascading dropdowns composable
const { institutions, loadInstitutions } = useCascadingDropdowns()

loading.value = true

const form = ref({
  name: '', code: '', institution: '', head_of_department: '', email: '', phone: '', description: '', is_active: true
})

const loadDepartment = async () => {
  const id = departmentId.value
  if (!id) { loading.value = false; return }
  loading.value = true
  try {
    const dept = await departmentService.getDepartmentById(id)
    let instId = ''
    if (dept.institution) {
      instId = typeof dept.institution === 'object' ? String(dept.institution.id) : String(dept.institution)
    }
    Object.assign(form.value, {
      name: dept.name || '', code: dept.code || '', institution: instId,
      head_of_department: dept.head_of_department || '', email: dept.email || '',
      phone: dept.phone || '', description: dept.description || '', is_active: dept.is_active !== false
    })
  } catch (error) {
    showAlert('error', 'Failed to load department', 'Error')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name }), 2000)
  } finally { loading.value = false }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.institution) delete data.institution
    await departmentService.updateDepartment(departmentId.value, data)
    cacheService.clear('departments_list')
    cacheService.clear('departments_dropdown')
    cacheService.clearPattern('department')
    showAlert('success', 'Department updated successfully!', 'Success!')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name }), 1500)
  } catch (error) {
    showAlert('error', error.response?.data?.detail || 'Failed to update department.', 'Error!')
  } finally { submitting.value = false }
}

watch(() => route.params.id, (newId) => { if (newId) loadDepartment() }, { immediate: false })

onMounted(async () => {
  await loadInstitutions()
  await loadDepartment()
})
</script>


