<template>
  <AdminPageTemplate
    title="Subject Profile"
    subtitle="View subject details and enrollment information"
    icon="bi bi-book"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <!-- No ID provided -->
    <EmptyState v-if="!entityId" icon="bi bi-book" title="Please Select a Subject"
      subtitle="Choose a subject from the list to view its profile."
      button-text="Go to Subject List" button-icon="bi bi-list-ul"
      @action="router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name })" />

    <LoadingSpinner v-else-if="loading" text="Loading subject details..." theme="admin" />

    <EmptyState v-else-if="!entity.id" icon="bi bi-book" title="Subject Not Found"
      button-text="Back to Subjects" button-icon="bi bi-arrow-left"
      @action="router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name })" />

    <div v-else>
      <!-- Subject Header -->
      <ProfileHeader
        :name="entity.name"
        :identifier="entity.code"
        :badges="profileBadges"
        :showStatusBadge="false"
        :showEditButton="false"
        theme="admin"
      />

      <div class="row g-4">
        <!-- Subject Information -->
        <div class="col-lg-6">
          <InfoCard title="Subject Information" icon="bi bi-info-circle" icon-color="admin" :items="subjectInfoItems" />
        </div>

        <!-- Description -->
        <div class="col-lg-6">
          <InfoCard title="Description" icon="bi bi-text-paragraph" icon-color="success"
            :items="[{ label: 'Description', value: entity.description || 'No description available' }]" />
        </div>

        <!-- Stats Cards -->
        <div class="col-12">
          <StatsGrid :stats="statsData" :columns="4" />
        </div>

        <!-- Assigned Teachers -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-person-workspace me-2 text-success"></i>Assigned Teachers</h6>
              <span class="badge bg-success">{{ assignedTeachers.length }}</span>
            </div>
            <div class="card-body p-0">
              <EmptyState v-if="assignedTeachers.length === 0" icon="bi bi-inbox" title="No teachers assigned" />
              <ul v-else class="list-group list-group-flush">
                <li v-for="t in assignedTeachers" :key="t.id" class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ t.teacher_name || t.full_name }}</strong>
                    <br><small class="text-muted">{{ t.designation || 'Teacher' }}</small>
                  </div>
                  <button @click="router.push({ name: ADMIN_ROUTES.TEACHER_PROFILE.name, params: { id: t.teacher } })" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-eye"></i>
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Assignments -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-file-earmark-text me-2 text-warning"></i>Assignments</h6>
              <span class="badge bg-warning text-dark">{{ assignments.length }}</span>
            </div>
            <div class="card-body p-0">
              <EmptyState v-if="assignments.length === 0" icon="bi bi-inbox" title="No assignments yet" />
              <ul v-else class="list-group list-group-flush">
                <li v-for="a in assignments.slice(0, 5)" :key="a.id" class="list-group-item">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{{ a.title }}</strong>
                      <br><small class="text-muted">Due: {{ formatDate(a.due_date) }}</small>
                    </div>
                    <span class="badge bg-admin">{{ a.total_marks }} marks</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Enrolled Students -->
        <div class="col-12">
          <SubjectsTable
            title="Enrolled Students"
            icon="bi bi-people"
            :subjects="enrolledStudents"
            empty-message="No students enrolled in this subject"
            :columns="studentColumns"
            :limit="10"
            @view-subject="(s) => router.push({ name: ADMIN_ROUTES.STUDENT_PROFILE.name, params: { id: s.student } })"
          />
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { ProfileHeader, InfoCard, StatsGrid, SubjectsTable } from '@/components/shared/profile'
import { LoadingSpinner, EmptyState } from '@/components/shared/common'
import { useProfileLoader } from '@/composables/shared'
import { subjectService } from '@/services/shared'
import { formatDate } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Subjects', href: ADMIN_ROUTES.SUBJECT_LIST.path },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.SUBJECT_LIST.name }) }
]

// Use shared profile loader — handles ID extraction, loading, fetching, route watching
const { entityId, loading, entity, subData } = useProfileLoader({
  fetchMain: (id) => subjectService.getSubjectById(id),
  subResources: [
    { key: 'students', fetch: (id) => subjectService.getEnrolledStudents(id) },
    { key: 'teachers', fetch: (id) => subjectService.getAssignedTeachers(id) },
    { key: 'assignments', fetch: (id) => subjectService.getSubjectAssignments(id) }
  ]
})

// Convenient aliases for sub-resource data
const enrolledStudents = computed(() => subData.value.students)
const assignedTeachers = computed(() => subData.value.teachers)
const assignments = computed(() => subData.value.assignments)

// Profile badges for ProfileHeader
const profileBadges = computed(() => {
  const badges = [{ text: `${entity.value.credit_hours} Credits`, class: 'bg-admin' }]
  if (entity.value.semester_name) badges.push({ text: entity.value.semester_name, class: 'bg-info' })
  if (entity.value.program_name) badges.push({ text: entity.value.program_name, class: 'bg-secondary' })
  return badges
})

// Subject info items for InfoCard
const subjectInfoItems = computed(() => [
  { label: 'Name', value: entity.value.name },
  { label: 'Code', value: entity.value.code },
  { label: 'Credit Hours', value: entity.value.credit_hours?.toString() },
  { label: 'Semester', value: entity.value.semester_name || 'Not Assigned' },
  { label: 'Program', value: entity.value.program_name || 'N/A' }
])

// Stats data for StatsGrid
const statsData = computed(() => [
  { value: enrolledStudents.value.length, label: 'Enrolled Students', icon: 'bi bi-people', bgClass: 'bg-admin-light', iconColor: 'text-admin' },
  { value: assignedTeachers.value.length, label: 'Teachers', icon: 'bi bi-person-workspace', bgClass: 'bg-success-light', iconColor: 'text-success' },
  { value: assignments.value.length, label: 'Assignments', icon: 'bi bi-file-earmark-text', bgClass: 'bg-warning-light', iconColor: 'text-warning' },
  { value: entity.value.credit_hours || 0, label: 'Credit Hours', icon: 'bi bi-clock', bgClass: 'bg-info-light', iconColor: 'text-info' }
])

const studentColumns = [
  { key: 'student_enrollment', label: 'Enrollment #' },
  { key: 'student_name', label: 'Name' },
  { key: 'student_email', label: 'Email' }
]
</script>

