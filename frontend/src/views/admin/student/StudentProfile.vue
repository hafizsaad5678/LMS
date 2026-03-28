<template>
  <AdminPageTemplate
    title="Student Profile"
    subtitle="View student details and academic information"
    icon="bi bi-person-badge"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No ID provided -->
    <div v-if="!studentId" class="text-center py-5">
      <i class="bi bi-person-badge display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Please Select a Student</h4>
      <p class="text-muted">Choose a student from the list to view their profile.</p>
      <button @click="router.push(ADMIN_ROUTES.STUDENT_LIST.path)" class="btn btn-admin-primary mt-3">
        <i class="bi bi-list-ul me-2"></i>Go to Student List
      </button>
    </div>

    <LoadingSpinner v-else-if="loading" text="Loading student profile..." theme="admin" />

    <div v-else-if="!student.id" class="text-center py-5">
      <i class="bi bi-person-x display-1 text-muted"></i>
      <h4 class="text-muted mt-3">Student Not Found</h4>
      <button @click="router.push(ADMIN_ROUTES.STUDENT_LIST.path)" class="btn btn-admin-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Students
      </button>
    </div>

    <div v-else>
      <!-- Profile Header -->
      <ProfileHeader
        :name="student.full_name"
        :identifier="student.enrollment_number"
        :is-active="student.is_active"
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

        <!-- Academic Information -->
        <div class="col-lg-6">
          <InfoCard
            title="Academic Information"
            icon="bi bi-mortarboard"
            icon-color="success"
            :items="academicInfoItems"
          />
        </div>

        <!-- Stats Cards -->
        <div class="col-12">
          <StatsGrid :stats="statsData" :columns="4" />
        </div>

        <!-- Enrolled Subjects -->
        <div class="col-12">
          <SubjectsTable
            title="Enrolled Subjects"
            :subjects="enrolledSubjects"
            empty-message="No subjects enrolled yet"
            :show-teacher="true"
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
import { studentService } from '@/services/shared'
import { formatDate } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const studentId = computed(() => route.params.id)

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Students', href: ADMIN_ROUTES.STUDENT_LIST.path },
  { name: 'Profile' }
]

const actions = [
  { 
    label: 'Back to List', 
    icon: 'bi bi-arrow-left', 
    variant: 'btn-admin-outline', 
    onClick: () => router.push(ADMIN_ROUTES.STUDENT_LIST.path) 
  }
]

const loading = ref(true)
const student = ref({})
const enrolledSubjects = ref([])

// Profile badges
const profileBadges = computed(() => {
  const badges = []
  if (student.value.program_name) {
    badges.push({ text: student.value.program_name, class: 'bg-info' })
  }
  return badges
})

// Personal information items for InfoCard
const personalInfoItems = computed(() => [
  { label: 'Email', value: student.value.email, href: `mailto:${student.value.email}` },
  { label: 'Phone', value: student.value.phone },
  { label: 'Gender', value: student.value.gender, capitalize: true },
  { label: 'Date of Birth', value: formatDate(student.value.date_of_birth) },
  { label: 'CNIC', value: student.value.cnic },
  { label: 'Address', value: student.value.address }
])

// Academic information items for InfoCard
const academicInfoItems = computed(() => [
  { label: 'Program', value: student.value.program_name || 'Not Assigned' },
  { label: 'Department', value: student.value.department_name },
  { label: 'Session/Batch', value: student.value.session_name },
  { label: 'Current Semester', value: student.value.current_semester_name },
  { label: 'Enrollment Date', value: formatDate(student.value.created_at) },
  { label: 'Blood Group', value: student.value.blood_group }
])

// Stats data for StatsGrid
const statsData = computed(() => [
  {
    value: enrolledSubjects.value.length,
    label: 'Enrolled Subjects',
    icon: 'bi bi-book',
    bgClass: 'bg-admin-light',
    iconColor: 'text-admin'
  },
  {
    value: student.value.completed_assignments || 0,
    label: 'Completed Assignments',
    icon: 'bi bi-check-circle',
    bgClass: 'bg-success-light',
    iconColor: 'text-success'
  },
  {
    value: student.value.pending_assignments || 0,
    label: 'Pending Assignments',
    icon: 'bi bi-hourglass-split',
    bgClass: 'bg-warning-light',
    iconColor: 'text-warning'
  },
  {
    value: `${student.value.attendance_rate || 0}%`,
    label: 'Attendance Rate',
    icon: 'bi bi-graph-up',
    bgClass: 'bg-info-light',
    iconColor: 'text-info'
  }
])

const navigateToEdit = () => {
  router.push({ name: ADMIN_ROUTES.STUDENT_EDIT.name, params: { id: student.value.id } })
}

const viewSubject = (subject) => {
  router.push({ name: ADMIN_ROUTES.SUBJECT_PROFILE.name, params: { id: subject.subject || subject.id } })
}

const loadStudent = async () => {
  if (!studentId.value || studentId.value === 'profile') {
    loading.value = false
    return
  }
  
  loading.value = true
  try {
    student.value = await studentService.getStudent(studentId.value)
    
    // Try to load enrolled subjects
    try {
      const subjects = await studentService.getStudentSubjects(studentId.value)
      enrolledSubjects.value = Array.isArray(subjects) ? subjects : (subjects.results || [])
    } catch (e) {
      console.warn('Could not load subjects:', e)
    }
  } catch (error) {
    console.error('Error loading student:', error)
  } finally {
    loading.value = false
  }
}

// Watch for route param changes
watch(() => route.params.id, (newId) => {
  if (newId && newId !== 'profile') {
    loadStudent()
  }
}, { immediate: false })

onMounted(() => {
  loadStudent()
})
</script>

