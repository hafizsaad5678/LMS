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
import { departmentService, toFormData } from '@/services/shared'
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
  name: '', code: '', institution: '', head_of_department: '', email: '', phone: '', description: '', is_active: true, image: null
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
      phone: dept.phone || '', description: dept.description || '', is_active: dept.is_active !== false,
      image: dept.image || null
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
    
    // Explicitly handle image field
    // If it's a string (URL) and not a File, we don't want to send it back as a string
    // because DRF ImageField expects a file or null for clearing.
    // If we want to keep the existing image, we can just omit it from the payload
    // in a PATCH request, but here we are using PUT.
    
    const payload = data.image instanceof File ? toFormData(data) : { ...data }
    
    // If using PUT and image is a URL string, DRF might complain if it's not a file.
    // Let's remove it if it's just the URL string to avoid validation errors.
    if (!(data.image instanceof File) && typeof data.image === 'string') {
        delete payload.image
    }
    
    if (data.image instanceof File) {
        await departmentService.updateDepartment(departmentId.value, payload)
    } else {
        // Use patch if no new image to be safer with PUT constraints
        await departmentService.patchDepartment(departmentId.value, payload)
    }
    
    cacheService.clear('departments_list')
    cacheService.clear('departments_dropdown')
    cacheService.clearPattern('department')
    showAlert('success', 'Department updated successfully!', 'Success!')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name }), 1500)
  } catch (error) {
    const errorData = error.response?.data
    let errorMessage = 'Failed to update department.'
    
    if (errorData && typeof errorData === 'object') {
      const messages = []
      for (const [field, errors] of Object.entries(errorData)) {
        const fieldName = field.charAt(0).toUpperCase() + field.slice(1)
        const fieldErrors = Array.isArray(errors) ? errors.join(', ') : errors
        messages.push(`${fieldName}: ${fieldErrors}`)
      }
      if (messages.length > 0) errorMessage = messages.join('\n')
    }
    
    showAlert('error', errorMessage, 'Error!')
  } finally { submitting.value = false }
}

watch(() => route.params.id, (newId) => { if (newId) loadDepartment() }, { immediate: false })

onMounted(async () => {
  await loadInstitutions()
  await loadDepartment()
})
</script>


