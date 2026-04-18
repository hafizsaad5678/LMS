<template>
  <TeacherPageTemplate
    title="Subject Profile"
    subtitle="View subject details and class information"
    icon="bi bi-book"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <EmptyState v-if="!subjectId" icon="bi bi-book" title="Please Select a Specific Subject"
      message="Choose a subject from your class list to view its detailed profile."
    >
      <div class="d-flex gap-3 justify-content-center mt-4">
        <button @click="router.push({ name: TEACHER_ROUTES.CLASS_LIST.name })" class="btn btn-teacher-primary">
          <i class="bi bi-list-ul me-2"></i>Go to Class List
        </button>
        <button @click="router.push({ name: TEACHER_ROUTES.STUDENT_LIST.name })" class="btn btn-teacher-outline">
          <i class="bi bi-people me-2"></i>Go to Students
        </button>
      </div>
    </EmptyState>

    <LoadingSpinner v-else-if="loading" message="Loading subject details..." />

    <EmptyState v-else-if="!subject.id" icon="bi bi-book" title="Subject Not Found">
      <button @click="router.push({ name: TEACHER_ROUTES.CLASS_LIST.name })" class="btn btn-teacher-primary mt-3">
        <i class="bi bi-arrow-left me-2"></i>Back to Classes
      </button>
    </EmptyState>

    <div v-else>
      <ProfileHeader
        :name="subject.subject_name"
        :identifier="subject.subject_code"
        icon="bi bi-book"
        avatarClass="profile-avatar-subject"
        :badges="profileBadges"
        :showStatusBadge="false"
        :showEditButton="false"
        theme="teacher"
      />

      <div class="row g-4">
        <div class="col-12">
          <InfoCard title="Subject Information" icon="bi bi-info-circle" :items="subjectInfoItems" />
        </div>
        <div class="col-12">
          <InfoCard title="Academic Hierarchy" icon="bi bi-diagram-3" :items="academicInfoItems" />
        </div>
      </div>

      <StatsGrid :stats="statsData" title="Class Statistics" icon="bi bi-bar-chart" class="mt-4" />

      <div class="mt-4">
        <SubjectsTable
          title="Enrolled Students"
          icon="bi bi-people"
          :subjects="enrolledStudents"
          :columns="studentColumns"
          count-label-singular="Student"
          count-label-plural="Students"
          empty-message="No students are currently enrolled in this class"
          @view-subject="viewStudentProfile"
        />
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { ProfileHeader, InfoCard, StatsGrid, SubjectsTable } from '@/components/shared/profile'
import { LoadingSpinner, EmptyState } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()

const subjectId = computed(() => route.params.id)
const loading = ref(false)
const subject = ref({})
const enrolledStudents = ref([])
const assignmentCount = ref(0)
const attendanceRate = ref(0)
const averageGrade = ref('N/A')

const breadcrumbs = computed(() => [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Classes', href: TEACHER_ROUTES.CLASS_LIST.path },
  { name: subject.value.subject_name || 'Subject Profile' }
])

const actions = computed(() => [
  { label: 'Back to Classes', icon: 'bi bi-arrow-left', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.CLASS_LIST.name }) }
])

const profileBadges = computed(() => {
  const badges = []
  const totalStudents = Number(subject.value.student_count || 0)
  badges.push({ text: `${subject.value.credit_hours} Credit Hours`, class: 'bg-info' })
  badges.push({ text: `${totalStudents} Students`, class: 'bg-success' })
  if (subject.value.department_name) badges.push({ text: subject.value.department_name, class: 'bg-teacher' })
  if (subject.value.program_name) badges.push({ text: subject.value.program_name, class: 'bg-secondary' })
  if (subject.value.semester_number) badges.push({ text: `Semester ${subject.value.semester_number}`, class: 'bg-warning text-dark' })
  return badges
})

const subjectInfoItems = computed(() => [
  { label: 'Subject Name', value: subject.value.subject_name },
  { label: 'Subject Code', value: subject.value.subject_code },
  { label: 'Credit Hours', value: subject.value.credit_hours?.toString() },
  { label: 'Description', value: subject.value.description || 'No description available' }
])

const academicInfoItems = computed(() => [
  { label: 'Department', value: subject.value.department_name },
  { label: 'Program', value: subject.value.program_name },
  { label: 'Semester', value: subject.value.semester?.toString() },
  { label: 'Total Students', value: `${subject.value.student_count || 0} Students` }
])

const statsData = computed(() => [
  { value: subject.value.student_count || 0, label: 'Total Students', icon: 'bi bi-people', bgClass: 'bg-teacher-light', iconColor: 'text-teacher' },
  { value: assignmentCount.value, label: 'Assignments', icon: 'bi bi-file-text', bgClass: 'bg-success-light', iconColor: 'text-success' },
  { value: `${attendanceRate.value}%`, label: 'Attendance Rate', icon: 'bi bi-calendar-check', bgClass: 'bg-warning-light', iconColor: 'text-warning' },
  { value: averageGrade.value, label: 'Average Grade', icon: 'bi bi-award', bgClass: 'bg-info-light', iconColor: 'text-info' }
])

const studentColumns = [
  { key: 'roll_no', label: 'Enrollment #', badge: true, badgeClass: 'badge bg-dark' },
  { key: 'name', label: 'Student Name' },
  { key: 'email', label: 'Email' }
]

const viewStudentProfile = (student) => {
  if (!student?.id) return
  router.push({ name: TEACHER_ROUTES.STUDENT_PROFILE.name, params: { id: student.id } })
}

const loadSubject = async () => {
  if (!subjectId.value) return
  loading.value = true
  enrolledStudents.value = []
  assignmentCount.value = 0
  attendanceRate.value = 0
  averageGrade.value = 'N/A'

  try {
    const classes = await teacherPanelService.getMyClasses()
    const classList = classes.results || classes || []
    const foundSubject = classList.find(cls => cls.id.toString() === subjectId.value || cls.subject_id.toString() === subjectId.value)

    if (foundSubject) {
      subject.value = foundSubject
      const subjectIdToUse = foundSubject.subject_id || foundSubject.id
      const [stats, studentsResponse] = await Promise.all([
        teacherPanelService.getSubjectStatistics(subjectIdToUse),
        teacherPanelService.getClassStudents(foundSubject.id)
      ])

      assignmentCount.value = stats.assignmentCount
      attendanceRate.value = stats.attendanceRate
      averageGrade.value = stats.averageGrade

      const studentList = studentsResponse?.results || studentsResponse || []
      enrolledStudents.value = studentList.map(student => ({
        id: student.id,
        name: student.name,
        roll_no: student.roll_no,
        email: student.email
      }))
    } else {
      subject.value = {}
      enrolledStudents.value = []
    }
  } catch (err) {
    console.error('Error loading subject:', err)
    subject.value = {}
    enrolledStudents.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadSubject)
</script>

