<template>
  <TeacherPageTemplate
    title="Delete Assignment"
    subtitle="Permanently remove an assignment"
    icon="bi bi-trash"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
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

    <LoadingSpinner v-if="loading" text="Loading assignment details..." theme="admin" />

    <div v-else-if="assignment" class="row justify-content-center">
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm border-top border-danger border-4">
          <div class="card-body p-4 text-center">
            <div class="mb-4">
              <i class="bi bi-exclamation-triangle text-danger display-1"></i>
            </div>
            <h3 class="fw-bold text-dark mb-3">Are you sure?</h3>
            <p class="text-muted mb-4">
              You are about to delete the assignment <strong>"{{ assignment.title }}"</strong>.
              This action is permanent and will delete all student submissions, grades, and feedback associated with it.
            </p>
            
            <div class="d-flex gap-3 justify-content-center">
              <button @click="router.push({ name: TEACHER_ROUTES.ASSIGNMENT_LIST.name })" class="btn btn-light px-4">
                <i class="bi bi-x-circle me-1"></i>Cancel
              </button>
              <button @click="handleDelete" class="btn btn-danger px-4" :disabled="deleting">
                <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-trash me-1"></i>Delete Permanently
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { AlertMessage, LoadingSpinner } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const assignmentId = route.params.id

const loading = ref(true)
const deleting = ref(false)
const assignment = ref(null)
const { alert, showAlert } = useAlert()

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Assignments', href: TEACHER_ROUTES.ASSIGNMENT_LIST.path },
  { name: 'Delete' }
]

const actions = [
  { 
    label: 'Back to List', 
    icon: 'bi bi-arrow-left', 
    variant: 'btn-teacher-outline', 
    onClick: () => router.push({ name: TEACHER_ROUTES.ASSIGNMENT_LIST.name }) 
  }
]

const handleDelete = async () => {
  deleting.value = true
  try {
    await teacherPanelService.deleteAssignment(assignmentId)
    router.push({ name: TEACHER_ROUTES.ASSIGNMENT_LIST.name })
  } catch (error) {
    showAlert('error', 'Failed to delete assignment. Please try again.', 'Error!')
    deleting.value = false
  }
}

const loadAssignment = async () => {
  if (!assignmentId) return
  try {
    const data = await teacherPanelService.getAssignment(assignmentId)
    assignment.value = data
  } catch (error) {
    console.error('Error loading assignment:', error)
    router.push({ name: TEACHER_ROUTES.ASSIGNMENT_LIST.name })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAssignment()
})
</script>
