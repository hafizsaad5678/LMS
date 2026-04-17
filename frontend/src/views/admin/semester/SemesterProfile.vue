<template>
  <AdminPageTemplate
    title="Semester Profile"
    subtitle="View detailed semester information"
    icon="bi bi-calendar3"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <EmptyState v-if="!entityId" icon="bi bi-calendar3" title="Please Select a Semester"
      subtitle="Choose a semester from the list to view its profile."
      button-text="Go to Semester List" button-icon="bi bi-list-ul"
      @action="router.push({ name: ADMIN_ROUTES.SEMESTER_LIST.name })" />

    <LoadingSpinner v-else-if="loading" text="Loading semester details..." theme="admin" />

    <EmptyState v-else-if="!entity.id" icon="bi bi-calendar-x" title="Semester Not Found"
      button-text="Back to Semesters" button-icon="bi bi-arrow-left"
      @action="router.push({ name: ADMIN_ROUTES.SEMESTER_LIST.name })" />

    <div v-else>
      <ProfileHeader
        :name="entity.name"
        :identifier="`Semester ${entity.number}`"
        :is-active="semesterIsActive"
        :badges="profileBadges"
        theme="admin"
        @edit="router.push({ name: ADMIN_ROUTES.SEMESTER_EDIT.name, params: { id: entity.id } })"
      />

      <div class="row g-4">
        <div class="col-lg-6">
          <InfoCard title="Semester Information" icon="bi bi-info-circle" icon-color="admin" :items="basicInfoItems" />
        </div>

        <div class="col-lg-6">
          <InfoCard title="Timeline & Schedule" icon="bi bi-clock-history" icon-color="primary" :items="timelineItems" />
        </div>

        <div class="col-12">
          <StatsGrid :stats="statsData" :columns="3" />
        </div>

        <!-- Subjects -->
        <div class="col-12" id="subjects">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-book me-2 text-admin"></i>Subjects</h6>
              <div>
                <span class="badge bg-admin me-2">{{ subjects.length }} Subjects</span>
                <button @click="router.push({ name: ADMIN_ROUTES.SUBJECT_ADD.name, query: { semester: entity.id } })" 
                        class="btn btn-sm btn-outline-primary py-0" title="Add Subject">
                  <i class="bi bi-plus-lg"></i>
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <EmptyState v-if="subjects.length === 0" icon="bi bi-inbox" title="No subjects in this semester" />
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Code</th>
                      <th>Subject Name</th>
                      <th>Type</th>
                      <th>Credits</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="sub in subjects" :key="sub.id">
                      <td><span class="badge bg-dark">{{ sub.code }}</span></td>
                      <td>{{ sub.name }}</td>
                      <td><span class="badge bg-secondary">{{ sub.type || 'Theory' }}</span></td>
                      <td><span class="badge bg-info">{{ sub.credit_hours }}</span></td>
                      <td>
                        <button @click="router.push({ name: ADMIN_ROUTES.SUBJECT_PROFILE.name, params: { id: sub.id } })" 
                                class="btn btn-sm btn-outline-primary">
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
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { ProfileHeader, InfoCard, StatsGrid } from '@/components/shared/profile'
import { LoadingSpinner, EmptyState } from '@/components/shared/common'
import { useProfileLoader } from '@/composables/shared'
import { semesterService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { formatDate as formatDateUtil } from '@/utils/formatters'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Semesters', href: ADMIN_ROUTES.SEMESTER_LIST.path },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.SEMESTER_LIST.name }) }
]

const { entityId, loading, entity, subData } = useProfileLoader({
  fetchMain: semesterService.getById,
  subResources: [
    { key: 'subjects', fetch: (id) => semesterService.getSubjects(id) }
  ],
  idParam: 'id'
})

const subjects = computed(() => subData.value.subjects || [])

const formatDate = (d) => formatDateUtil(d, { year: 'numeric', month: 'long', day: 'numeric' })

const getDuration = (start, end) => {
  if (!start || !end) return '-'
  const diff = new Date(end) - new Date(start)
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const months = Math.floor(days / 30)
  return months > 0 ? `${months} Months` : `${days} Days`
}

const profileBadges = computed(() => {
  const badges = []
  if (entity.value.program_name) badges.push({ text: entity.value.program_name, class: 'bg-info' })
  if (entity.value.session_name) badges.push({ text: entity.value.session_name, class: 'bg-secondary' })
  return badges
})

const semesterIsActive = computed(() => String(entity.value.status || '').toLowerCase() === 'active')

const basicInfoItems = computed(() => [
  { label: 'Name', value: entity.value.name },
  { label: 'Semester Number', value: entity.value.number?.toString() },
  { label: 'Program', value: entity.value.program_name },
  { label: 'Session', value: entity.value.session_name },
  { label: 'Status', value: entity.value.status || 'Active', capitalize: true }
])

const timelineItems = computed(() => [
  { label: 'Start Date', value: formatDate(entity.value.start_date) },
  { label: 'End Date', value: formatDate(entity.value.end_date) },
  { label: 'Duration', value: getDuration(entity.value.start_date, entity.value.end_date) },
  { label: 'Is Active', value: semesterIsActive.value ? 'Yes' : 'No' }
])

const statsData = computed(() => [
  { value: subjects.value.length, label: 'Total Subjects', icon: 'bi bi-book', bgClass: 'bg-admin-light', iconColor: 'text-admin' },
  { value: entity.value.number, label: 'Semester Rank', icon: 'bi bi-hash', bgClass: 'bg-info-light', iconColor: 'text-info' },
  { value: getDuration(entity.value.start_date, entity.value.end_date), label: 'Total Duration', icon: 'bi bi-clock', bgClass: 'bg-success-light', iconColor: 'text-success' }
])
</script>



