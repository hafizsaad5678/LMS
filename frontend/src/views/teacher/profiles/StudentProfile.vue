<template>
  <TeacherPageTemplate
    title="Student Profile"
    subtitle="View student details and academic information"
    icon="bi bi-person-badge"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <EmptyState v-if="!studentId" icon="bi bi-person-badge" title="Please Select a Specific Student"
      message="Choose a student from your class to view their detailed profile."
    >
      <div class="d-flex gap-3 justify-content-center mt-4">
        <button @click="router.push({ name: TEACHER_ROUTES.STUDENT_LIST.name })" class="btn btn-teacher-primary">
          <i class="bi bi-list-ul me-2"></i>Go to Student List
        </button>
        <button @click="router.push({ name: TEACHER_ROUTES.CLASS_LIST.name })" class="btn btn-teacher-outline">
          <i class="bi bi-book me-2"></i>Go to Classes
        </button>
      </div>
    </EmptyState>

    <LoadingSpinner v-else-if="loading" message="Loading student profile..." />

    <EmptyState v-else-if="!student.id" icon="bi bi-person-x" title="Student Not Found">
      <button @click="router.push({ name: TEACHER_ROUTES.STUDENT_LIST.name })" class="btn btn-teacher-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Students
      </button>
    </EmptyState>

    <div v-else>
      <ProfileHeader
        :name="student.name || 'N/A'"
        :identifier="student.roll_no || 'N/A'"
        theme="teacher"
        :show-edit-button="false"
        :badges="profileBadges"
      />

      <div class="row g-4">
        <div class="col-12 col-lg-6">
          <InfoCard title="Personal Information" icon="bi bi-person-lines-fill" iconColor="teacher" :items="personalInfoItems" />
        </div>
        <div class="col-12 col-lg-6">
          <InfoCard title="Academic Information" icon="bi bi-mortarboard" iconColor="teacher" :items="academicInfoItems" />
        </div>

        <div class="col-12">
          <StatsGrid :stats="statsData" :columns="4" />
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { ProfileHeader, InfoCard, StatsGrid } from '@/components/shared/profile'
import { LoadingSpinner, EmptyState } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()

const studentId = computed(() => route.params.id)
const loading = ref(false)
const student = ref({})

const breadcrumbs = computed(() => [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Students', href: TEACHER_ROUTES.STUDENT_LIST.path },
  { name: student.value.name || 'Student Profile' }
])

const actions = computed(() => [
  { label: 'Back to Students', icon: 'bi bi-arrow-left', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.STUDENT_LIST.name }) }
])

const displaySemester = computed(() => {
  const value = student.value.current_semester || student.value.semester_number || student.value.semester
  return value ? `Semester ${value}` : 'N/A'
})

const displaySubject = computed(() => {
  if (student.value.subject_name && student.value.subject_code && student.value.subject_name !== 'N/A') {
    return `${student.value.subject_name} (${student.value.subject_code})`
  }
  return null
})

const profileBadges = computed(() => [
  ...(student.value.program_name && student.value.program_name !== 'N/A' ? [{ text: student.value.program_name, class: 'bg-info' }] : []),
  ...(student.value.department_name && student.value.department_name !== 'N/A' ? [{ text: student.value.department_name, class: 'bg-secondary' }] : []),
  ...(displaySemester.value !== 'N/A' ? [{ text: displaySemester.value, class: 'bg-warning text-dark' }] : []),
  ...(displaySubject.value ? [{ text: displaySubject.value, class: 'bg-success' }] : [])
])

const personalInfoItems = computed(() => [
  { label: 'Full Name', value: student.value.name },
  { label: 'Roll Number', value: student.value.roll_no },
  { label: 'Email', value: student.value.email },
  { label: 'Phone', value: student.value.phone }
])

const academicInfoItems = computed(() => [
  { label: 'Department', value: student.value.department_name },
  { label: 'Program', value: student.value.program_name },
  { label: 'Current Semester', value: displaySemester.value },
  { label: 'Current Subject', value: displaySubject.value }
])

const statsData = computed(() => {
  const stats = [
    { value: `${student.value.attendance_percentage || 0}%`, label: 'Attendance', icon: 'bi bi-calendar-check', bgClass: 'bg-teacher-light', iconColor: 'text-teacher' },
    { value: student.value.assignments_completed || 0, label: 'Assignments', icon: 'bi bi-file-earmark-text', bgClass: 'bg-success-light', iconColor: 'text-success' },
    { value: student.value.average_grade || 'N/A', label: 'Avg Grade', icon: 'bi bi-graph-up', bgClass: 'bg-info-light', iconColor: 'text-info' },
    { value: student.value.participation_score || 'Good', label: 'Participation', icon: 'bi bi-chat-dots', bgClass: 'bg-warning-light', iconColor: 'text-warning' }
  ]
  return stats
})

const loadStudent = async () => {
  if (!studentId.value) return
  loading.value = true
  try {
    const response = await teacherPanelService.getStudentDetail(studentId.value)
    if (response) {
      // API returns the student object directly for a retrieve call
      const studentData = response
      
      student.value = {
        ...studentData,
        name: studentData.full_name || studentData.name || 'N/A',
        roll_no: studentData.enrollment_number || studentData.roll_no || 'N/A',
        department_name: studentData.department_name || studentData.program?.department?.name || 'N/A',
        program_name: studentData.program_name || studentData.program?.name || 'N/A',
        semester_number: studentData.current_semester || studentData.semester_number,
        // The detailed view might not have the specific subject context from class students
        // but we keep the structure
        subject_name: studentData.subject_name || 'N/A',
        subject_code: studentData.subject_code || 'N/A'
      }
    } else {
      student.value = {}
    }
  } catch (err) {
    console.error('Error loading student:', err)
    student.value = {}
  } finally {
    loading.value = false
  }
}

onMounted(loadStudent)
watch(studentId, loadStudent)
</script>

