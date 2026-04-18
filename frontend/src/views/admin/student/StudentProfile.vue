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
            title="Current Semester Subjects"
            :subjects="currentSemesterSubjects"
            empty-message="No subjects enrolled in current semester"
            :show-teacher="true"
            @view-subject="viewSubject"
          />
        </div>

        <!-- Semester Academic Record -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h5 class="mb-0 fw-semibold">
                <i class="bi bi-journal-text text-admin me-2"></i>
                Semester Academic Record
              </h5>
              <span class="badge bg-admin-light text-admin">{{ semesterSubjectRecords.length }} Semesters</span>
            </div>
            <div class="card-body p-0">
              <div v-if="semesterSubjectRecords.length === 0" class="p-4 text-muted">No semester records available.</div>
              <div v-else class="table-responsive">
                <table class="table align-middle mb-0">
                  <thead class="table-light">
                    <tr>
                      <th class="ps-3">Semester</th>
                      <th>Status</th>
                      <th>Subjects</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="record in semesterSubjectRecords" :key="record.key">
                      <td class="ps-3 fw-semibold">{{ record.semesterLabel }}</td>
                      <td>
                        <span :class="['badge', record.statusClass]">{{ record.statusLabel }}</span>
                      </td>
                      <td>
                        <div class="small text-muted fw-bold">Total subjects in this semester: {{ record.subjectCount }}</div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
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
const allEnrolledSubjects = ref([])

const currentSemesterNumber = computed(() => Number(student.value.current_semester || 0))

const getFallbackSemesterNumber = (semesterName) => {
  const match = String(semesterName || '').match(/Semester\s+(\d+)/i)
  return match ? Number(match[1]) : 0
}

const currentSemesterSubjects = computed(() => {
  const target = currentSemesterNumber.value
  return allEnrolledSubjects.value.filter((item) => {
    const number = Number(item.semester_number || getFallbackSemesterNumber(item.semester_name))
    return target > 0 && number === target
  })
})

const semesterSubjectRecords = computed(() => {
  const map = new Map()
  const current = currentSemesterNumber.value

  for (const item of allEnrolledSubjects.value) {
    const number = Number(item.semester_number || getFallbackSemesterNumber(item.semester_name))
    const semesterLabel = item.semester_name || (number ? `Semester ${number}` : 'Unknown Semester')
    const key = `${number || 0}-${semesterLabel}`

    if (!map.has(key)) {
      map.set(key, {
        key,
        semesterNumber: number,
        semesterLabel,
        subjects: []
      })
    }

    map.get(key).subjects.push(item)
  }

  return Array.from(map.values())
    .sort((a, b) => a.semesterNumber - b.semesterNumber)
    .map((entry) => {
      const statusLabel = entry.semesterNumber < current
        ? 'Completed'
        : (entry.semesterNumber === current ? 'Current' : 'Future')

      const statusClass = entry.semesterNumber < current
        ? 'bg-success'
        : (entry.semesterNumber === current ? 'bg-admin' : 'bg-secondary')

      return {
        key: entry.key,
        semesterLabel: entry.semesterLabel,
        statusLabel,
        statusClass,
        subjectCount: entry.subjects.length
      }
    })
})

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
  { label: 'Status', value: student.value.profile_status || (student.value.is_active ? 'Active' : 'Inactive') },
  { label: 'Program', value: student.value.program_name || 'Not Assigned' },
  { label: 'Department', value: student.value.department_name },
  { label: 'Session/Batch', value: student.value.session_name },
  { label: 'Current Semester', value: student.value.current_semester_name },
  { label: 'Enrollment Date', value: formatDate(student.value.created_at) },
  { label: 'Blood Group', value: formatBloodGroup(student.value.blood_group) }
])

const formatBloodGroup = (value) => {
  const normalized = String(value || 'unknown').trim().toLowerCase()
  if (normalized === 'unknown') return 'Unknown'
  return normalized.toUpperCase()
}

// Stats data for StatsGrid
const statsData = computed(() => [
  {
    value: currentSemesterSubjects.value.length,
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
      allEnrolledSubjects.value = Array.isArray(subjects) ? subjects : (subjects.results || [])
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

