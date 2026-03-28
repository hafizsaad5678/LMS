<template>
  <AdminPageTemplate
    title="Edit Course"
    subtitle="Update course information"
    icon="bi bi-mortarboard-fill"
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

    <LoadingSpinner v-if="loading" text="Loading course details..." theme="admin" />

    <div v-else-if="!courseId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-mortarboard display-4"></i>
      </div>
      <h4 class="text-muted">No Course Selected</h4>
      <p class="text-muted mb-4">Please select a course from the list to edit.</p>
      <button @click="router.push(ADMIN_ROUTES.COURSE_LIST.path)" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Course List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <CourseForm
          v-model="form"
          :departments="departments"
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
import { AlertMessage, LoadingSpinner } from '@/components/shared/common'
import { CourseForm } from '@/components/shared/forms'
import { useEntityForm, useCascadingDropdowns } from '@/composables/shared'
import { programService } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const courseId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Courses', href: ADMIN_ROUTES.COURSE_LIST.path },
  { name: 'Edit Course' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.COURSE_LIST.path) }
]

const { alert, loading, submitting, showAlert, goToList } = useEntityForm({
  entityName: 'Course',
  listRoute: ADMIN_ROUTES.COURSE_LIST.path,
  cacheKeys: ['courses_list', 'programs_dropdown']
})

// Use cascading dropdowns composable
const { departments, loadDepartments } = useCascadingDropdowns()

loading.value = true

const form = ref({ name: '', code: '', department: '', duration_years: 4, description: '' })

const loadCourse = async () => {
  const id = courseId.value
  if (!id) { loading.value = false; return }
  loading.value = true
  try {
    const course = await programService.getProgramById(id)
    Object.assign(form.value, {
      name: course.name || '', code: course.code || '',
      department: course.department ? (typeof course.department === 'object' ? String(course.department.id) : String(course.department)) : '',
      duration_years: course.duration_years || 4, description: course.description || ''
    })
  } catch (error) {
    showAlert('error', 'Failed to load course', 'Error')
    setTimeout(() => router.push(ADMIN_ROUTES.COURSE_LIST.path), 2000)
  } finally { loading.value = false }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.department) delete data.department
    await programService.updateProgram(courseId.value, data)
    cacheService.clear('courses_list')
    cacheService.clear('programs_dropdown')
    cacheService.clearPattern('course')
    cacheService.clearPattern('program')
    showAlert('success', 'Course updated successfully!', 'Success!')
    setTimeout(() => router.push(ADMIN_ROUTES.COURSE_LIST.path), 1500)
  } catch (error) {
    showAlert('error', error.response?.data?.detail || 'Failed to update course.', 'Error!')
  } finally { submitting.value = false }
}

const handleCancel = () => goToList()

watch(() => route.params.id, (newId) => { if (newId) loadCourse() }, { immediate: false })

onMounted(async () => {
  await loadDepartments()
  await loadCourse()
})
</script>


