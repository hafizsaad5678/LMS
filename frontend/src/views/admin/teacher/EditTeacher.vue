<template>
  <AdminPageTemplate
    title="Edit Teacher"
    subtitle="Update teacher information"
    icon="bi bi-person-gear"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- Confirm Dialog -->
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

    <LoadingSpinner v-if="loading" text="Loading teacher details..." theme="admin" />

    <div v-else-if="!teacherId" class="text-center py-5">
      <div class="mb-4">
        <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
          <i class="bi bi-person-gear display-4"></i>
        </div>
        <h4 class="text-muted">No Teacher Selected</h4>
        <p class="text-muted mb-4">Please select a teacher from the list to edit.</p>
        <button @click="router.push(ADMIN_ROUTES.TEACHER_LIST.path)" class="btn btn-admin-primary">
          <i class="bi bi-list-ul me-2"></i>Go to Teacher List
        </button>
      </div>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-10">
        <TeacherForm
          v-model="form"
          :is-edit-mode="true"
          :submitting="submitting"
          :employee-id="employeeId"
          :current-department-name="currentDepartmentName"
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
import { TeacherForm } from '@/components/shared/forms'
import { useEntityForm, syncTeacherSubjects, getTeacherSubjectIds } from '@/composables/shared'
import { teacherService, toFormData } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const teacherId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Teachers', href: ADMIN_ROUTES.TEACHER_LIST.path },
  { name: 'Edit Teacher' }
]

const actions = [
  { 
    label: 'Back to List', 
    icon: 'bi bi-arrow-left', 
    variant: 'btn-admin-outline', 
    onClick: () => router.push(ADMIN_ROUTES.TEACHER_LIST.path) 
  }
]

// Use composable for form logic
const {
  alert,
  confirmDialog,
  loading,
  submitting,
  showAlert,
  validateCNICField,
  handleCancel
} = useEntityForm({
  entityName: 'Teacher',
  listRoute: ADMIN_ROUTES.TEACHER_LIST.path,
  cacheKeys: ['teachers_list']
})

// Initialize loading to true since we'll be fetching data
loading.value = true

// Read-only display values
const employeeId = ref('')
const currentDepartmentName = ref('')

const form = ref({
  full_name: '',
  email: '',
  phone: '',
  date_of_birth: '',
  gender: '',
  cnic: '',
  department: '',
  designation: '',
  qualification: '',
  specialization: '',
  joining_date: '',
  experience_years: 0,
  teaching_subjects: [],
  address: '',
  city: '',
  profile_image: null
})

const loadTeacher = async () => {
  const id = teacherId.value
  if (!id) {
    loading.value = false
    return
  }
  loading.value = true
  try {
    const teacher = await teacherService.getTeacher(id)
    employeeId.value = teacher.employee_id
    currentDepartmentName.value = teacher.department_name || (teacher.department?.name) || ''
    
    // Assign each field individually to ensure reactivity
    form.value.full_name = teacher.full_name || ''
    form.value.email = teacher.email || ''
    form.value.phone = teacher.phone || ''
    form.value.date_of_birth = teacher.date_of_birth || ''
    form.value.gender = teacher.gender || ''
    form.value.cnic = teacher.cnic || ''
    form.value.department = teacher.department ? (typeof teacher.department === 'object' ? String(teacher.department.id) : String(teacher.department)) : ''
    form.value.designation = teacher.designation || ''
    form.value.qualification = teacher.qualification || ''
    form.value.specialization = teacher.specialization || ''
    form.value.joining_date = teacher.joining_date || ''
    form.value.experience_years = teacher.experience_years || 0
    form.value.address = teacher.address || ''
    form.value.city = teacher.city || ''
    form.value.profile_image = teacher.profile_image || null
    
    // Load teaching subjects using composable
    form.value.teaching_subjects = await getTeacherSubjectIds(id)
    
  } catch (error) {
    console.error('Error loading teacher:', error)
    showAlert('error', 'Failed to load teacher details', 'Error')
    setTimeout(() => router.push(ADMIN_ROUTES.TEACHER_LIST.path), 2000)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  // Validate CNIC if provided
  if (form.value.cnic && form.value.cnic.trim()) {
    if (!validateCNICField(form.value.cnic)) {
      return
    }
  }

  submitting.value = true
  try {
    const teacherData = {
      full_name: form.value.full_name,
      email: form.value.email,
      phone: form.value.phone,
      date_of_birth: form.value.date_of_birth || null,
      gender: form.value.gender,
      cnic: form.value.cnic && form.value.cnic.trim() ? form.value.cnic : null,
      department: form.value.department || null,
      designation: form.value.designation || null,
      qualification: form.value.qualification || null,
      specialization: form.value.specialization || null,
      joining_date: form.value.joining_date || null,
      experience_years: form.value.experience_years || 0,
      address: form.value.address || null,
      city: form.value.city || null,
      profile_image: form.value.profile_image || null,
      is_active: form.value.is_active
    }

    const payload = teacherData.profile_image instanceof File ? toFormData(teacherData) : teacherData
    await teacherService.patchTeacher(teacherId.value, payload)
    
    // Sync subject assignments using composable
    await syncTeacherSubjects(teacherId.value, form.value.teaching_subjects)
    
    // Clear cache
    cacheService.clear('teachers_list')
    cacheService.clearPattern('teacher')
    
    showAlert('success', 'Teacher updated successfully!', 'Success!')
    setTimeout(() => router.push(ADMIN_ROUTES.TEACHER_LIST.path), 1500)
  } catch (error) {
    console.error('Error updating teacher:', error)
    const msg = error.response?.data?.detail || 
                error.response?.data?.cnic?.[0] || 
                error.response?.data?.email?.[0] || 
                'Failed to update teacher.'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

// Watch for route param changes
watch(() => route.params.id, (newId) => {
  if (newId) loadTeacher()
}, { immediate: false })

onMounted(async () => {
  await loadTeacher()
})
</script>


