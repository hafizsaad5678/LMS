<template>
  <AdminPageTemplate
    title="Edit Student"
    subtitle="Update student information"
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

    <LoadingSpinner v-if="loading" text="Loading student details..." theme="admin" />

    <div v-else-if="!studentId" class="text-center py-5">
      <div class="mb-4">
        <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
          <i class="bi bi-person-gear display-4"></i>
        </div>
        <h4 class="text-muted">No Student Selected</h4>
        <p class="text-muted mb-4">Please select a student from the list to edit.</p>
        <button @click="router.push(ADMIN_ROUTES.STUDENT_LIST.path)" class="btn btn-admin-primary">
          <i class="bi bi-list-ul me-2"></i>Go to Student List
        </button>
      </div>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-10">
        <StudentForm
          v-model="form"
          :is-edit-mode="true"
          :submitting="submitting"
          :enrollment-number="enrollmentNumber"
          :current-department-name="currentDepartmentName"
          :current-program-name="currentProgramName"
          :initial-department="initialDepartment"
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
import { StudentForm } from '@/components/shared/forms'
import { useEntityForm, enrollStudentInSubjects, getStudentEnrolledSubjectIds } from '@/composables/shared'
import { studentService } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getErrorMessage } from '@/utils/errorMap'

const router = useRouter()
const route = useRoute()
const studentId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Students', href: ADMIN_ROUTES.STUDENT_LIST.path },
  { name: 'Edit Student' }
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
  loading,
  submitting,
  showAlert,
  validateCNICField,
  handleCancel
} = useEntityForm({
  entityName: 'Student',
  listRoute: ADMIN_ROUTES.STUDENT_LIST.path,
  cacheKeys: ['students_list']
})

// Initialize loading to true since we'll be fetching data
loading.value = true

// Read-only display values
const enrollmentNumber = ref('')
const currentDepartmentName = ref('')
const currentProgramName = ref('')
const initialDepartment = ref('')

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

const loadStudent = async () => {
  const id = studentId.value
  if (!id) {
    loading.value = false
    return
  }
  loading.value = true
  try {
    const student = await studentService.getStudent(id)
    enrollmentNumber.value = student.enrollment_number
    currentProgramName.value = student.program_name || ''
    currentDepartmentName.value = student.department_name || ''
    
    // Assign each field individually to ensure reactivity
    form.value.full_name = student.full_name || ''
    form.value.email = student.email || ''
    form.value.phone = student.phone || ''
    form.value.date_of_birth = student.date_of_birth || ''
    form.value.gender = student.gender || ''
    form.value.cnic = student.cnic || ''
    form.value.program = student.program ? (typeof student.program === 'object' ? String(student.program.id) : String(student.program)) : ''
    form.value.session = student.session ? (typeof student.session === 'object' ? String(student.session.id) : String(student.session)) : ''
    form.value.enrollment_year = student.enrollment_year || new Date().getFullYear()
    form.value.current_semester = student.current_semester || 1
    form.value.father_name = student.father_name || ''
    form.value.guardian_phone = student.guardian_phone || ''
    form.value.address = student.address || ''
    form.value.city = student.city || ''
    
    // Set initial department
    if (student.department) {
      initialDepartment.value = typeof student.department === 'object' ? String(student.department.id) : String(student.department)
    }
    
    // Load enrolled subjects using composable
    form.value.enrolled_subjects = await getStudentEnrolledSubjectIds(id)
    
  } catch (error) {
    console.error('Error loading student:', error)
    const msg = getErrorMessage(error, 'student', 'fetch')
    showAlert('error', msg, 'Error')
    setTimeout(() => router.push(ADMIN_ROUTES.STUDENT_LIST.path), 2000)
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

    await studentService.updateStudent(studentId.value, studentData)
    
    // Update subject enrollments using composable
    if (form.value.enrolled_subjects.length > 0) {
      await enrollStudentInSubjects(studentId.value, form.value.enrolled_subjects)
    }
    
    // Clear cache
    cacheService.clear('students_list')
    cacheService.clearPattern('student')
    
    showAlert('success', 'Student updated successfully!', 'Success!')
    setTimeout(() => router.push(ADMIN_ROUTES.STUDENT_LIST.path), 1500)
  } catch (error) {
    console.error('Error updating student:', error)
    const msg = getErrorMessage(error, 'student', 'update')
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}

// Watch for route param changes
watch(() => route.params.id, (newId) => {
  if (newId) loadStudent()
}, { immediate: false })

onMounted(async () => {
  await loadStudent()
})
</script>


