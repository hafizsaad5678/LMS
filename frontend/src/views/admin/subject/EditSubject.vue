<template>
  <AdminPageTemplate
    title="Edit Subject"
    subtitle="Update subject information"
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

    <LoadingSpinner v-if="loading" text="Loading subject details..." theme="admin" />

    <div v-else-if="!subjectId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-book display-4"></i>
      </div>
      <h4 class="text-muted">No Subject Selected</h4>
      <p class="text-muted mb-4">Please select a subject from the list to edit.</p>
      <button @click="router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name })" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Subject List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <SubjectForm
          v-model="form"
          :departments="departments"
          :programs="programs"
          :semesters="semesters"
          :selected-department="selectedDepartment"
          :selected-program="selectedProgram"
          :loading-semesters="loadingSemesters"
          :is-edit-mode="true"
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, LoadingSpinner } from '@/components/shared/common'
import { SubjectForm } from '@/components/shared/forms'
import { useEntityForm, useCascadingDropdowns } from '@/composables/shared'
import { subjectService } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { api } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const subjectId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Subjects', href: ADMIN_ROUTES.SUBJECT_LIST.path },
  { name: 'Edit Subject' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name }) }
]

const { alert, loading, submitting, showAlert, goToList } = useEntityForm({
  entityName: 'Subject',
  listRoute: ADMIN_ROUTES.SUBJECT_LIST.path,
  cacheKeys: ['subjects_list']
})

// Use cascading dropdowns composable
const { 
  departments, programs, semesters,
  selectedDepartment, selectedProgram,
  loadingSemesters,
  loadDepartments, loadPrograms, loadSemesters,
  onDepartmentChange, onProgramChange
} = useCascadingDropdowns()

loading.value = true

const form = ref({ name: '', code: '', semester: '', credit_hours: 3, description: '' })

const loadSubject = async () => {
  const id = subjectId.value
  if (!id) { loading.value = false; return }
  loading.value = true
  try {
    const subject = await subjectService.getSubjectById(id)
    const semesterId = subject.semester ? (typeof subject.semester === 'object' ? subject.semester.id : subject.semester) : ''
    Object.assign(form.value, {
      name: subject.name || '', code: subject.code || '',
      semester: semesterId ? String(semesterId) : '',
      credit_hours: subject.credit_hours || 3, description: subject.description || ''
    })
    
    // Load semester details to set department and program
    if (semesterId) {
      try {
        const semResponse = await api.get(`/semesters/${semesterId}/`)
        if (semResponse.data?.program) {
          const programId = typeof semResponse.data.program === 'object' ? semResponse.data.program.id : semResponse.data.program
          selectedProgram.value = String(programId)
          const prog = programs.value.find(p => String(p.id) === String(programId))
          if (prog) selectedDepartment.value = prog.department
          await loadSemesters(programId)
        }
      } catch (e) { console.warn('Could not load semester details:', e) }
    }
  } catch (error) {
    showAlert('error', 'Failed to load subject', 'Error')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name }), 2000)
  } finally { loading.value = false }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.semester) delete data.semester
    await subjectService.updateSubject(subjectId.value, data)
    cacheService.clear('subjects_list')
    cacheService.clearPattern('subject')
    showAlert('success', 'Subject updated successfully!', 'Success!')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name }), 1500)
  } catch (error) {
    showAlert('error', error.response?.data?.detail || 'Failed to update subject.', 'Error!')
  } finally { submitting.value = false }
}

const handleCancel = () => goToList()

watch(() => route.params.id, (newId) => { if (newId) loadSubject() }, { immediate: false })

onMounted(async () => {
  await Promise.all([loadDepartments(), loadPrograms()])
  await loadSubject()
})
</script>


