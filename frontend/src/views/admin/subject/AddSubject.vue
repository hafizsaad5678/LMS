<template>
  <AdminPageTemplate
    title="Add New Subject"
    subtitle="Create a new academic subject"
    icon="bi bi-book-half"
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
        <SubjectForm
          v-model="form"
          :departments="departments"
          :programs="programs"
          :semesters="semesters"
          :selected-department="selectedDepartment"
          :selected-program="selectedProgram"
          :loading-semesters="loadingSemesters"
          :is-edit-mode="false"
          :submitting="submitting"
          @submit="handleSubmit"
          @cancel="handleCancel"
          @department-change="onDepartmentChange"
          @program-change="onProgramChange"
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
import { SubjectForm } from '@/components/shared/forms'
import { useEntityForm, useCascadingDropdowns } from '@/composables/shared'
import { subjectService } from '@/services/shared'
import { api } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Subjects', href: ADMIN_ROUTES.SUBJECT_LIST.path },
  { name: 'Add Subject' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name }) }
]

const { alert, confirmDialog, submitting, showAlert, handleCancel, clearCaches } = useEntityForm({
  entityName: 'Subject',
  listRoute: ADMIN_ROUTES.SUBJECT_LIST.path,
  cacheKeys: ['subjects_list']
})

const {
  departments,
  programs,
  semesters,
  selectedDepartment,
  selectedProgram,
  loadingSemesters,
  loadDepartments,
  loadPrograms,
  loadSemesters,
  onDepartmentChange,
  onProgramChange
} = useCascadingDropdowns()

const form = ref({ name: '', code: '', semester: '', credit_hours: 3, description: '' })

const handleSubmit = async () => {
  if (!selectedDepartment.value) {
    showAlert('error', 'Department missing.', 'Error!')
    return
  }
  if (!selectedProgram.value) {
    showAlert('error', 'Course/Program missing.', 'Error!')
    return
  }
  if (!form.value.semester) {
    showAlert('error', 'Semester missing.', 'Error!')
    return
  }

  submitting.value = true
  try {
    await subjectService.createSubject({ ...form.value })
    clearCaches()
    showAlert('success', 'Subject has been added successfully!', 'Success!')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name, query: { refresh: Date.now() } }), 1500)
  } catch (error) {
    const semesterError = error.response?.data?.semester
    const firstSemesterError = Array.isArray(semesterError) ? semesterError[0] : semesterError
    const fallbackMessage = error.response?.data?.detail || error.response?.data?.code?.[0] || 'Failed to add subject.'
    showAlert('error', firstSemesterError || fallbackMessage, 'Error!')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadDepartments(), loadPrograms()])

  if (route.query.semester) {
    const semId = route.query.semester
    try {
      const semRes = await api.get(`/semesters/${semId}/`)
      const sem = semRes.data || semRes
      const progId = sem.program
      if (progId) {
        const progRes = await api.get(`/programs/${progId}/`)
        const prog = progRes.data || progRes
        const deptId = prog.department?.id || prog.department
        if (deptId) {
          selectedDepartment.value = deptId
          selectedProgram.value = progId
          await loadSemesters(progId)
          form.value.semester = semId
        }
      }
    } catch (e) {
      console.error('Error auto-filling from semester query:', e)
    }
  }
})
</script>
