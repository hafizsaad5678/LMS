<template>
  <AdminPageTemplate
    title="Add New Student"
    subtitle="Register a new student in the system"
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
        <StudentForm
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
import { StudentForm } from '@/components/shared/forms'
import { useEntityForm, enrollStudentInSubjects } from '@/composables/shared'
import { studentService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getErrorMessage } from '@/utils/errorMap'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Students', href: ADMIN_ROUTES.STUDENT_LIST.path },
  { name: 'Add Student' }
]

const actions = [
  { 
    label: 'Back to List', 
    icon: 'bi bi-arrow-left', 
    variant: 'btn-admin-outline', 
    onClick: () => router.push(ADMIN_ROUTES.STUDENT_LIST.path) 
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
  entityName: 'Student',
  listRoute: ADMIN_ROUTES.STUDENT_LIST.path,
  cacheKeys: ['students_list']
})

const form = ref({
  full_name: '',
  email: '',
  phone: '',
  date_of_birth: '',
  gender: '',
  cnic: '',
  program: '',
  session: '',
  enrollment_year: new Date().getFullYear(),
  current_semester: 1,
  enrolled_subjects: [],
  father_name: '',
  guardian_phone: '',
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
    const studentData = {
      full_name: form.value.full_name,
      email: form.value.email.trim(),
      phone: form.value.phone || null,
      date_of_birth: form.value.date_of_birth || null,
      gender: form.value.gender,
      cnic: form.value.cnic && form.value.cnic.trim() ? form.value.cnic : null,
      program: form.value.program || null,
      session: form.value.session || null,
      enrollment_year: form.value.enrollment_year,
      current_semester: form.value.current_semester,
      father_name: form.value.father_name || null,
      guardian_phone: form.value.guardian_phone || null,
      address: form.value.address || null,
      city: form.value.city || null
    }

    const createdStudent = await studentService.createStudent(studentData)
    
    // Enroll in subjects using composable
    if (form.value.enrolled_subjects.length > 0) {
      await enrollStudentInSubjects(createdStudent.id, form.value.enrolled_subjects)
    }

    // Clear caches to update list view
    clearCaches()
    
    showAlert('success', 'Student has been added successfully!', 'Success!')
    setTimeout(() => router.push(ADMIN_ROUTES.STUDENT_LIST.path), 1500)
  } catch (error) {
    console.error('Error adding student:', error)
    const msg = getErrorMessage(error, 'student', 'create')
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}
</script>

