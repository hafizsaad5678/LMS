<template>
  <component
    :is="pageTemplate"
    :title="pageTitle"
    :subtitle="pageSubtitle"
    icon="bi bi-person-circle"
    :breadcrumbs="breadcrumbs"
    :actions="headerActions"
    :show-content-card="false"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :title="alert.title"
      :message="alert.message"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="alert.show = false"
    />

    <LoadingSpinner v-if="loading" text="Loading account details..." :theme="theme" />

    <div v-else-if="!canUseProfile" class="card border-0 shadow-sm">
      <div class="card-body text-center py-5">
        <i class="bi bi-person-x fs-1 text-muted"></i>
        <h5 class="mt-3 mb-2">Profile is not available</h5>
        <p class="text-muted mb-0">Your account record could not be loaded. Please login again.</p>
      </div>
    </div>

    <div v-else class="row g-4">
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body d-flex flex-column align-items-center text-center">
            <div class="avatar-circle profile-hero-avatar" :class="theme">
              {{ initials }}
            </div>
            <h5 class="fw-bold mt-3 mb-1">{{ profile.full_name || profile.name || authStore.displayName }}</h5>
            <p class="text-muted mb-2">{{ roleLabel }}</p>
            <span class="badge" :class="badgeClass">{{ profile.is_active === false ? 'Inactive' : 'Active' }}</span>
            <hr class="w-100 my-3" />
            <div class="w-100 text-start small">
              <div class="d-flex justify-content-between py-1">
                <span class="text-muted">Email</span>
                <span class="fw-medium text-break ms-2">{{ profile.email || '-' }}</span>
              </div>
              <div class="d-flex justify-content-between py-1">
                <span class="text-muted">Phone</span>
                <span class="fw-medium ms-2">{{ profile.phone || '-' }}</span>
              </div>
              <div class="d-flex justify-content-between py-1">
                <span class="text-muted">Identifier</span>
                <span class="fw-medium ms-2">{{ profileIdentifier }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-8">
        <div v-if="!canEditProfile" class="alert alert-info d-flex align-items-start gap-2" role="alert">
          <i class="bi bi-info-circle-fill mt-1"></i>
          <div>
            <div class="fw-semibold">Profile editing is managed by admin</div>
            <div class="small mb-0">You can view your account details here, but updates are restricted by system permissions.</div>
          </div>
        </div>

        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
            <h6 class="mb-0 fw-bold">Account Details</h6>
            <button
              v-if="canEditProfile"
              type="button"
              class="btn btn-sm"
              :class="editing ? 'btn-outline-secondary' : primaryButtonClass"
              @click="toggleEdit"
              :disabled="saving"
            >
              <i :class="editing ? 'bi bi-x-lg me-1' : 'bi bi-pencil-square me-1'"></i>
              {{ editing ? 'Cancel' : 'Edit Details' }}
            </button>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSave">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Full Name</label>
                  <input
                    v-model.trim="form.full_name"
                    type="text"
                    class="form-control"
                    :disabled="!canEditProfile || !editing || saving"
                    required
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email</label>
                  <input
                    :value="profile.email || ''"
                    type="email"
                    class="form-control"
                    disabled
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Phone</label>
                  <input
                    v-model.trim="form.phone"
                    type="text"
                    class="form-control"
                    :disabled="!canEditProfile || !editing || saving"
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label">City</label>
                  <input
                    v-model.trim="form.city"
                    type="text"
                    class="form-control"
                    :disabled="!canEditProfile || !editing || saving"
                  />
                </div>
                <div class="col-12">
                  <label class="form-label">Address</label>
                  <textarea
                    v-model.trim="form.address"
                    rows="3"
                    class="form-control"
                    :disabled="!canEditProfile || !editing || saving"
                  ></textarea>
                </div>
              </div>

              <div v-if="canEditProfile && editing" class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-outline-secondary" @click="resetForm" :disabled="saving">
                  Reset
                </button>
                <button type="submit" class="btn" :class="primaryButtonClass" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>

      </div>

      <div v-if="isStudentRole" class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-0 py-3">
            <h6 class="mb-0 fw-bold">Academic Snapshot</h6>
          </div>
          <div class="card-body">
            <div class="row g-3 mb-3">
              <div class="col-md-4">
                <div class="bg-light rounded-3 p-3 h-100">
                  <div class="small text-muted mb-1">Degree / Program</div>
                  <div class="fw-semibold text-truncate" :title="studentAcademic.program">{{ studentAcademic.program }}</div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="bg-light rounded-3 p-3 h-100">
                  <div class="small text-muted mb-1">Session</div>
                  <div class="fw-semibold text-truncate" :title="studentAcademic.session">{{ studentAcademic.session }}</div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="bg-light rounded-3 p-3 h-100">
                  <div class="small text-muted mb-1">Current Semester</div>
                  <div class="fw-semibold">{{ studentAcademic.currentSemester }}</div>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="mb-0">Enrolled Subjects</h6>
              <span class="badge bg-secondary-subtle text-dark">{{ enrolledSubjects.length }}</span>
            </div>

            <div v-if="enrolledSubjects.length > 0" class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Teacher</th>
                    <th>Semester</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subject in enrolledSubjects" :key="subject.id || `${subject.subject_code}-${subject.subject_name}`">
                    <td>
                      <div class="fw-medium">{{ subject.subject_name || '-' }}</div>
                      <div class="text-muted extra-tiny">{{ subject.subject_code || '' }}</div>
                    </td>
                    <td>{{ subject.teacher_name || 'Not Assigned' }}</td>
                    <td>{{ subject.semester_name || studentAcademic.currentSemester }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-muted small">
              No enrolled subjects found.
            </div>
          </div>
        </div>
      </div>
    </div>
  </component>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/store/auth'
import { teacherService, studentService } from '@/services/shared'
import { AlertMessage, LoadingSpinner } from '@/components/shared/common'
import { TeacherPageTemplate, StudentPageTemplate } from '@/components/shared/panels'
import { USER_ROLES } from '@/utils/constants/config'
import { TEACHER_ROUTES, STUDENT_ROUTES } from '@/utils/constants/routes'
import { safeStorage } from '@/utils/security'
import { STORAGE_KEYS } from '@/utils/constants/storage'

const authStore = useAuth()
const route = useRoute()

const loading = ref(true)
const saving = ref(false)
const editing = ref(false)
const profile = ref({})
const enrolledSubjects = ref([])

const form = reactive({
  full_name: '',
  phone: '',
  city: '',
  address: ''
})

const alert = reactive({
  show: false,
  type: 'info',
  title: '',
  message: ''
})

const role = computed(() => authStore.userRole || safeStorage.get(STORAGE_KEYS.USER_ROLE) || route.meta.role)
const userId = computed(() => authStore.userId || safeStorage.get(STORAGE_KEYS.USER_ID))

const canUseProfile = computed(() => Boolean(userId.value && (role.value === USER_ROLES.TEACHER || role.value === USER_ROLES.STUDENT)))
const isStudentRole = computed(() => role.value === USER_ROLES.STUDENT)
const theme = computed(() => role.value === USER_ROLES.TEACHER ? 'teacher' : 'student')
const pageTemplate = computed(() => role.value === USER_ROLES.TEACHER ? TeacherPageTemplate : StudentPageTemplate)
const pageTitle = computed(() => role.value === USER_ROLES.TEACHER ? 'My Teacher Account' : 'My Student Account')
const pageSubtitle = computed(() => role.value === USER_ROLES.TEACHER
  ? 'View and update your account details'
  : 'View your account details')
const roleLabel = computed(() => role.value === USER_ROLES.TEACHER ? 'Teacher' : 'Student')
const badgeClass = computed(() => role.value === USER_ROLES.TEACHER ? 'bg-primary-subtle text-primary' : 'bg-success-subtle text-success')
const primaryButtonClass = computed(() => role.value === USER_ROLES.TEACHER ? 'btn-teacher-primary' : 'btn-student-primary')
const canEditProfile = computed(() => role.value === USER_ROLES.TEACHER)
const studentAcademic = computed(() => ({
  program: profile.value?.program_name || 'Not Assigned',
  session: profile.value?.session_name || 'Not Assigned',
  currentSemester: profile.value?.current_semester_name || 'Not Assigned'
}))

const breadcrumbs = computed(() => {
  if (role.value === USER_ROLES.TEACHER) {
    return [
      { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
      { name: 'My Account' }
    ]
  }
  return [
    { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
    { name: 'My Account' }
  ]
})

const headerActions = computed(() => [])

const profileIdentifier = computed(() => {
  if (role.value === USER_ROLES.TEACHER) return profile.value.employee_id || '-'
  return profile.value.enrollment_number || '-'
})

const initials = computed(() => {
  const label = profile.value.full_name || profile.value.name || authStore.displayName || ''
  return label.trim().charAt(0).toUpperCase() || 'U'
})

const showAlert = (type, title, message) => {
  alert.type = type
  alert.title = title
  alert.message = message
  alert.show = true
}

const mapToForm = (data) => {
  form.full_name = data?.full_name || data?.name || ''
  form.phone = data?.phone || ''
  form.city = data?.city || ''
  form.address = data?.address || ''
}

const refreshDisplayName = async () => {
  const resolvedName = profile.value?.full_name || profile.value?.name
  if (resolvedName) {
    authStore.userName = resolvedName
    safeStorage.set(STORAGE_KEYS.USERNAME, resolvedName)
  }
}

const loadProfile = async () => {
  loading.value = true
  try {
    if (!canUseProfile.value) return

    if (role.value === USER_ROLES.TEACHER) {
      profile.value = await teacherService.getTeacher(userId.value)
      enrolledSubjects.value = []
    } else {
      profile.value = await studentService.getStudent(userId.value)
      const subjectsRes = await studentService.getStudentSubjects(userId.value)
      enrolledSubjects.value = Array.isArray(subjectsRes) ? subjectsRes : (subjectsRes?.results || [])
    }

    mapToForm(profile.value)
    await refreshDisplayName()
  } catch (error) {
    console.error('Failed to load account profile', error)
    showAlert('error', 'Error', 'Unable to load account details right now.')
  } finally {
    loading.value = false
  }
}

const toggleEdit = () => {
  editing.value = !editing.value
  if (!editing.value) {
    mapToForm(profile.value)
  }
}

const resetForm = () => {
  mapToForm(profile.value)
}

const handleSave = async () => {
  if (!canUseProfile.value || !editing.value) return
  if (!canEditProfile.value) {
    showAlert('warning', 'Not Allowed', 'Profile updates are managed by admin for your role.')
    return
  }

  saving.value = true
  try {
    const payload = {
      full_name: form.full_name,
      phone: form.phone || null,
      city: form.city || null,
      address: form.address || null
    }

    if (role.value === USER_ROLES.TEACHER) {
      await teacherService.patchTeacher(userId.value, payload)
      profile.value = await teacherService.getTeacher(userId.value)
    } else {
      await studentService.patchStudent(userId.value, payload)
      profile.value = await studentService.getStudent(userId.value)
    }

    mapToForm(profile.value)
    await refreshDisplayName()
    editing.value = false
    showAlert('success', 'Saved', 'Your details were updated successfully.')
  } catch (error) {
    console.error('Failed to update account profile', error)
    const message = error?.response?.data?.detail || 'Failed to save your details. Please try again.'
    showAlert('error', 'Save Failed', message)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>
