<template>
  <AdminPageTemplate
    title="Teacher Profile"
    subtitle="View teacher details and teaching information"
    icon="bi bi-person-workspace"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No ID provided -->
    <div v-if="!teacherId" class="text-center py-5">
      <i class="bi bi-person-workspace display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Teacher</h4>
      <p class="text-muted">Choose a teacher from the list to view their profile.</p>
      <button @click="router.push(ADMIN_ROUTES.TEACHER_LIST.path)" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Teacher List
      </button>
    </div>

    <LoadingSpinner v-else-if="loading" text="Loading teacher profile..." theme="admin" />

    <div v-else-if="!teacher.id" class="text-center py-5">
      <i class="bi bi-person-x display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Teacher Not Found</h4>
      <button @click="router.push(ADMIN_ROUTES.TEACHER_LIST.path)" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Teachers
      </button>
    </div>

    <div v-else>
      <!-- Profile Header -->
      <ProfileHeader
        :name="teacher.full_name"
        :identifier="teacher.employee_id"
        :is-active="teacher.is_active"
        :badges="profileBadges"
        theme="admin"
        @edit="navigateToEdit"
      />

      <div class="row g-4">
        <!-- Personal Information -->
        <div class="col-lg-6">
          <InfoCard
            title="Personal Information"
            icon="bi bi-person"
            icon-color="admin"
            :items="personalInfoItems"
          />
        </div>

        <!-- Professional Information -->
        <div class="col-lg-6">
          <InfoCard
            title="Professional Information"
            icon="bi bi-briefcase"
            icon-color="success"
            :items="professionalInfoItems"
          />
        </div>

        <!-- Stats Cards -->
        <div class="col-12">
          <StatsGrid :stats="statsData" :columns="4" />
        </div>

        <!-- Teaching Subjects -->
        <div class="col-12">
          <SubjectsTable
            title="Subjects Currently Teaching"
            :subjects="teachingSubjects"
            empty-message="No subjects assigned yet"
            :show-student-count="true"
            @view-subject="viewSubject"
          />
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { ProfileHeader, InfoCard, StatsGrid, SubjectsTable } from '@/components/shared/profile'
import { LoadingSpinner } from '@/components/shared/common'
import { teacherService } from '@/services/shared'
import { formatDate } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const teacherId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Teachers', href: ADMIN_ROUTES.TEACHER_LIST.path },
  { name: 'Profile' }
]

const actions = [
  { 
    label: 'Back to List', 
    icon: 'bi bi-arrow-left', 
    variant: 'btn-admin-outline', 
    onClick: () => router.push(ADMIN_ROUTES.TEACHER_LIST.path) 
  }
]

const loading = ref(true)
const teacher = ref({})
const teachingSubjects = ref([])

// Profile badges
const profileBadges = computed(() => {
  const badges = []
  if (teacher.value.department_name) {
    badges.push({ text: teacher.value.department_name, class: 'bg-admin' })
  }
  if (teacher.value.designation) {
    badges.push({ text: teacher.value.designation, class: 'bg-info' })
  }
  return badges
})

// Personal information items for InfoCard
const personalInfoItems = computed(() => [
  { label: 'Email', value: teacher.value.email, href: `mailto:${teacher.value.email}` },
  { label: 'Phone', value: teacher.value.phone },
  { label: 'Gender', value: teacher.value.gender, capitalize: true },
  { label: 'Date of Birth', value: formatDate(teacher.value.date_of_birth) },
  { label: 'CNIC', value: teacher.value.cnic },
  { label: 'Address', value: teacher.value.address }
])

// Professional information items for InfoCard
const professionalInfoItems = computed(() => [
  { label: 'Department', value: teacher.value.department_name || 'Not Assigned' },
  { label: 'Designation', value: teacher.value.designation, capitalize: true },
  { label: 'Qualification', value: teacher.value.qualification },
  { label: 'Specialization', value: teacher.value.specialization },
  { label: 'Joining Date', value: formatDate(teacher.value.joining_date || teacher.value.created_at) }
])

// Stats data for StatsGrid
const statsData = computed(() => [
  {
    value: teachingSubjects.value.length,
    label: 'Subjects Teaching',
    icon: 'bi bi-book',
    bgClass: 'bg-admin-light',
    iconColor: 'text-admin'
  },
  {
    value: teachingSubjects.value.reduce((sum, s) => sum + (s.student_count || 0), 0),
    label: 'Total Students',
    icon: 'bi bi-people',
    bgClass: 'bg-success-light',
    iconColor: 'text-success'
  },
  {
    value: teacher.value.assignments_count || 0,
    label: 'Assignments Created',
    icon: 'bi bi-file-earmark-text',
    bgClass: 'bg-warning-light',
    iconColor: 'text-warning'
  },
  {
    value: teacher.value.classes_this_week || 0,
    label: 'Classes This Week',
    icon: 'bi bi-calendar-check',
    bgClass: 'bg-info-light',
    iconColor: 'text-info'
  }
])

const navigateToEdit = () => {
  router.push({ name: ADMIN_ROUTES.TEACHER_EDIT.name, params: { id: teacher.value.id } })
}

const viewSubject = (subject) => {
  router.push({ name: ADMIN_ROUTES.SUBJECT_PROFILE.name, params: { id: subject.subject || subject.id } })
}

const loadTeacher = async () => {
  if (!teacherId.value || teacherId.value === 'profile') return
  loading.value = true
  try {
    teacher.value = await teacherService.getTeacher(teacherId.value)
    
    // Try to load teaching subjects
    try {
      const subjects = await teacherService.getTeacherSubjects(teacherId.value)
      teachingSubjects.value = Array.isArray(subjects) ? subjects : (subjects.results || [])
    } catch (e) {
      console.warn('Could not load subjects:', e)
    }
  } catch (error) {
    console.error('Error loading teacher:', error)
  } finally {
    loading.value = false
  }
}

// Watch for route param changes
watch(() => route.params.id, (newId) => {
  if (newId && newId !== 'profile') loadTeacher()
}, { immediate: false })

onMounted(() => {
  if (teacherId.value && teacherId.value !== 'profile') {
    loadTeacher()
  } else {
    loading.value = false
  }
})
</script>

