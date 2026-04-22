<template>
  <AdminPageTemplate
    title="Course Profile"
    subtitle="View course details and academic information"
    icon="bi bi-mortarboard"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <EmptyState v-if="!entityId" icon="bi bi-mortarboard" title="Please Select a Course"
      subtitle="Choose a course from the list to view its details."
      button-text="Go to Course List" button-icon="bi bi-list-ul"
      @action="router.push(ADMIN_ROUTES.COURSE_LIST.path)" />

    <LoadingSpinner v-else-if="loading" text="Loading course details..." theme="admin" />

    <EmptyState v-else-if="!entity.id" icon="bi bi-x-circle" title="Course Not Found"
      button-text="Back to Courses" button-icon="bi bi-arrow-left"
      @action="router.push(ADMIN_ROUTES.COURSE_LIST.path)" />

    <div v-else>
      <ProfileHeader
        :name="entity.name"
        :identifier="entity.code"
        :badges="profileBadges"
        theme="admin"
        @edit="router.push({ name: ADMIN_ROUTES.COURSE_EDIT.name, params: { id: entity.id } })"
      />

      <div class="row g-4">
        <div class="col-lg-6">
          <InfoCard title="Course Information" icon="bi bi-info-circle" icon-color="admin" :items="courseInfoItems" />
        </div>

        <div class="col-lg-6">
          <InfoCard title="Description" icon="bi bi-text-paragraph" icon-color="success"
            :items="[{ label: 'Description', value: entity.description || 'No description available' }]" />
        </div>

        <div class="col-12">
          <StatsGrid :stats="statsData" :columns="4" />
        </div>

        <!-- Semesters -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-calendar3 me-2 text-admin"></i>Semesters</h6>
              <span class="badge bg-admin">{{ semesters.length }} Semesters</span>
            </div>
            <div class="card-body p-0">
              <EmptyState v-if="semesters.length === 0" icon="bi bi-inbox" title="No semesters defined yet" />
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Semester</th>
                      <th>Number</th>
                      <th>Subjects</th>
                      <th>Start Date</th>
                      <th>End Date</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="sem in semesters" :key="sem.id">
                      <td class="fw-semibold">{{ sem.name }}</td>
                      <td><span class="badge bg-dark">{{ sem.number }}</span></td>
                      <td><span class="badge bg-info">{{ sem.subject_count || 0 }}</span></td>
                      <td>{{ formatDate(sem.start_date) }}</td>
                      <td>{{ formatDate(sem.end_date) }}</td>
                      <td>
                        <span :class="['badge', getActiveBadgeClass(isSemesterActive(sem))]">
                          {{ isSemesterActive(sem) ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <button @click="router.push({ name: ADMIN_ROUTES.SEMESTER_PROFILE.name, params: { id: sem.id } })" class="btn btn-sm btn-outline-primary" title="View Semester">
                          <i class="bi bi-eye"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Students -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-people me-2 text-info"></i>Enrolled Students</h6>
              <span class="badge bg-info">{{ students.length }} Students</span>
            </div>
            <div class="card-body p-0">
              <EmptyState v-if="students.length === 0" icon="bi bi-inbox" title="No students enrolled in this course" />
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Enrollment #</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Semester</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="s in students.slice(0, 10)" :key="s.id">
                      <td><span class="badge bg-light text-dark">{{ s.enrollment_number }}</span></td>
                      <td class="fw-semibold">{{ s.full_name }}</td>
                      <td>{{ s.email }}</td>
                      <td>{{ s.current_semester_name || 'N/A' }}</td>
                      <td>
                        <span :class="['badge', getActiveBadgeClass(s.is_active)]">
                          {{ getActiveStatusText(s.is_active) }}
                        </span>
                      </td>
                      <td>
                        <button @click="router.push({ name: ADMIN_ROUTES.STUDENT_PROFILE.name, params: { id: s.id } })" class="btn btn-sm btn-outline-primary">
                          <i class="bi bi-eye"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="students.length > 10" class="text-center py-3">
                  <small class="text-muted">Showing 10 of {{ students.length }} students</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { ProfileHeader, InfoCard, StatsGrid } from '@/components/shared/profile'
import { LoadingSpinner, EmptyState } from '@/components/shared/common'
import { useProfileLoader } from '@/composables/shared'
import { programService, subjectService } from '@/services/shared'
import { formatDate } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getActiveBadgeClass, getActiveStatusText } from '@/utils/badgeHelpers'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Courses', href: ADMIN_ROUTES.COURSE_LIST.path },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push(ADMIN_ROUTES.COURSE_LIST.path) }
]

const { entityId, loading, entity, subData } = useProfileLoader({
  fetchMain: (id) => programService.getProgramById(id),
  subResources: [
    { key: 'semesters', fetch: (id) => programService.getProgramSemesters(id) },
    { key: 'students', fetch: (id) => programService.getProgramStudents(id) }
  ]
})

const semesters = computed(() => subData.value.semesters)
const students = computed(() => subData.value.students)
const subjectCreditsTotal = ref(null)

const normalizeToArray = (payload) => {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload?.data?.results)) return payload.data.results
  return []
}

const fetchSubjectCreditsAcrossSemesters = async (semesterList) => {
  if (!Array.isArray(semesterList) || semesterList.length === 0) {
    subjectCreditsTotal.value = 0
    return
  }

  try {
    const results = await Promise.allSettled(
      semesterList.map((semester) => subjectService.getAllSubjects({ semester: semester.id }))
    )

    const total = results.reduce((sum, result) => {
      if (result.status !== 'fulfilled') return sum
      const subjects = normalizeToArray(result.value)
      return sum + subjects.reduce((subjectSum, subject) => {
        const credits = Number(subject.credit_hours)
        return subjectSum + (Number.isFinite(credits) ? credits : 0)
      }, 0)
    }, 0)

    subjectCreditsTotal.value = total
  } catch (error) {
    console.error('Failed to compute subject credits for program profile:', error)
    subjectCreditsTotal.value = null
  }
}

watch(
  semesters,
  (value) => {
    fetchSubjectCreditsAcrossSemesters(value)
  },
  { immediate: true }
)

const parseDateValue = (value) => {
  if (!value) return null
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

const activeSemesterId = computed(() => {
  const list = Array.isArray(semesters.value) ? semesters.value : []
  if (list.length === 0) return null

  const explicitlyActive = list.filter((sem) => String(sem.status || '').toLowerCase() === 'active')
  if (explicitlyActive.length > 0) {
    return explicitlyActive
      .slice()
      .sort((a, b) => Number(b.number || 0) - Number(a.number || 0))[0]?.id || null
  }

  const now = new Date()
  const dateActive = list.filter((sem) => {
    const start = parseDateValue(sem.start_date)
    const end = parseDateValue(sem.end_date)
    if (!start || !end) return false
    return start <= now && now <= end
  })

  if (dateActive.length > 0) {
    return dateActive
      .slice()
      .sort((a, b) => Number(b.number || 0) - Number(a.number || 0))[0]?.id || null
  }

  return null
})

const isSemesterActive = (semester) => {
  if (!semester?.id) return false
  return String(semester.id) === String(activeSemesterId.value)
}

const profileBadges = computed(() => {
  const badges = [{ text: `${entity.value.duration_years} Years`, class: 'bg-admin' }]
  if (entity.value.department_name) badges.push({ text: entity.value.department_name, class: 'bg-info' })
  return badges
})

const courseInfoItems = computed(() => [
  { label: 'Name', value: entity.value.name },
  { label: 'Code', value: entity.value.code },
  { label: 'Department', value: entity.value.department_name || 'Not Assigned' },
  { label: 'Duration', value: `${entity.value.duration_years} Years` },
  { label: 'Created', value: formatDate(entity.value.created_at) }
])

const statsData = computed(() => {
  const totalSubjects = semesters.value.reduce((sum, s) => sum + (s.subject_count || 0), 0)
  const creditsFromSubjects = Number(subjectCreditsTotal.value)
  const programCredits = Number(
    entity.value.total_credits
    ?? entity.value.total_credit_hours
    ?? entity.value.max_credit_hours
    ?? entity.value.min_credit_hours
  )

  const totalCredits = Number.isFinite(creditsFromSubjects) && creditsFromSubjects > 0
    ? creditsFromSubjects
    : (Number.isFinite(programCredits) && programCredits > 0 ? programCredits : 0)
  return [
    { value: semesters.value.length, label: 'Semesters', icon: 'bi bi-calendar3', bgClass: 'bg-admin-light', iconColor: 'text-admin' },
    { value: totalSubjects, label: 'Total Subjects', icon: 'bi bi-book', bgClass: 'bg-success-light', iconColor: 'text-success' },
    { value: students.value.length, label: 'Enrolled Students', icon: 'bi bi-people', bgClass: 'bg-info-light', iconColor: 'text-info' },
    { value: totalCredits, label: 'Total Credit Hours', icon: 'bi bi-clock', bgClass: 'bg-warning-light', iconColor: 'text-warning' }
  ]
})
</script>

