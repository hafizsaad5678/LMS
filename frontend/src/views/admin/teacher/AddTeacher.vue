<template>
  <AdminPageTemplate
    title="Add New Teacher"
    subtitle="Register a new teacher in the system"
    icon="bi bi-person-plus-fill"
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

    <div class="row justify-content-center">
      <div class="col-lg-10">
        <TeacherForm
          v-model="form"
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { TeacherForm } from '@/components/shared/forms'
import { useEntityForm, assignSubjectsToTeacher } from '@/composables/shared'
import { teacherService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getErrorMessage } from '@/utils/errorMap'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Teachers', href: ADMIN_ROUTES.TEACHER_LIST.path },
  { name: 'Add Teacher' }
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
  submitting,
  showAlert,
  validateCNICField,
  handleCancel,
  clearCaches
} = useEntityForm({
  entityName: 'Teacher',
  listRoute: ADMIN_ROUTES.TEACHER_LIST.path,
  cacheKeys: ['teachers_list']
})

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
  city: ''
})

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
      email: form.value.email.trim(),
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
      city: form.value.city || null
    }

    const createdTeacher = await teacherService.createTeacher(teacherData)
    
    // Assign subjects using composable
    if (form.value.teaching_subjects.length > 0) {
      await assignSubjectsToTeacher(createdTeacher.id, form.value.teaching_subjects)
    }

    // Clear caches to update list view
    clearCaches()
    
    showAlert('success', 'Teacher has been added successfully!', 'Success!')
    setTimeout(() => router.push(ADMIN_ROUTES.TEACHER_LIST.path), 1500)
  } catch (error) {
    console.error('Error adding teacher:', error)
    const msg = getErrorMessage(error, 'teacher', 'create')
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}
</script>

