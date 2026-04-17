<template>
  <AdminPageTemplate
    title="Department Profile"
    subtitle="View department details and statistics"
    icon="bi bi-building"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <EmptyState v-if="!entityId" icon="bi bi-building" title="Please Select a Department"
      subtitle="Choose a department from the list to view its details."
      button-text="Go to Department List" button-icon="bi bi-list-ul"
      @action="router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name })" />

    <LoadingSpinner v-else-if="loading" text="Loading department details..." theme="admin" />

    <EmptyState v-else-if="!entity.id" icon="bi bi-x-circle" title="Department Not Found"
      button-text="Back to Departments" button-icon="bi bi-arrow-left"
      @action="router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name })" />

    <div v-else>
      <ProfileHeader
        :name="entity.name"
        :identifier="entity.code"
        :is-active="entity.is_active"
        :badges="profileBadges"
        theme="admin"
        @edit="router.push({ name: ADMIN_ROUTES.DEPARTMENT_EDIT.name, params: { id: entity.id } })"
      />

      <div class="row g-4">
        <div class="col-lg-6">
          <InfoCard title="Department Information" icon="bi bi-info-circle" icon-color="admin" :items="deptInfoItems" />
        </div>

        <div class="col-lg-6">
          <InfoCard title="Description" icon="bi bi-text-paragraph" icon-color="success"
            :items="[{ label: 'Description', value: entity.description || 'No description available', multiline: true }]" />
        </div>

        <div class="col-12">
          <StatsGrid :stats="statsData" :columns="3" />
        </div>

        <!-- Programs/Courses -->
        <div class="col-12" id="programs">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-mortarboard me-2 text-admin"></i>Programs/Courses</h6>
              <div>
                <span class="badge bg-admin me-2">{{ programs.length }} Programs</span>
                <button @click="router.push({ name: ADMIN_ROUTES.COURSE_ADD.name, query: { department: entity.id } })" class="btn btn-sm btn-outline-primary py-0" title="Add Course">
                  <i class="bi bi-plus-lg"></i>
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <EmptyState v-if="programs.length === 0" icon="bi bi-inbox" title="No programs in this department" />
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Code</th>
                      <th>Program Name</th>
                      <th>Duration</th>
                      <th>Semesters</th>
                      <th>Students</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="prog in programs" :key="prog.id">
                      <td><span class="badge bg-dark">{{ prog.code }}</span></td>
                      <td>{{ prog.name }}</td>
                      <td>{{ prog.duration_years }} Years</td>
                      <td><span class="badge bg-info">{{ prog.semester_count || 0 }}</span></td>
                      <td><span class="badge bg-success">{{ prog.student_count || 0 }}</span></td>
                      <td>
                        <button @click="router.push({ name: ADMIN_ROUTES.COURSE_PROFILE.name, params: { id: prog.id } })" class="btn btn-sm btn-outline-primary">
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

        <!-- Teachers -->
        <div class="col-12" id="teachers">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-person-workspace me-2 text-success"></i>Teachers</h6>
              <div>
                <span class="badge bg-success me-2">{{ teachers.length }} Teachers</span>
                <button @click="router.push({ name: ADMIN_ROUTES.TEACHER_ADD.name, query: { department: entity.id } })" class="btn btn-sm btn-outline-success py-0" title="Add Teacher">
                  <i class="bi bi-plus-lg"></i>
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <EmptyState v-if="teachers.length === 0" icon="bi bi-inbox" title="No teachers in this department" />
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Name</th>
                      <th>Designation</th>
                      <th>Email</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="t in teachers" :key="t.id">
                      <td class="fw-semibold">{{ t.full_name }}</td>
                      <td><span class="badge bg-info">{{ t.designation || 'N/A' }}</span></td>
                      <td>{{ t.email }}</td>
                      <td>
                        <button @click="router.push({ name: ADMIN_ROUTES.TEACHER_PROFILE.name, params: { id: t.id } })" class="btn btn-sm btn-outline-primary">
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
import { departmentService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Departments', href: ADMIN_ROUTES.DEPARTMENT_LIST.path },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.DEPARTMENT_LIST.name }) }
]

const { entityId, loading, entity } = useProfileLoader({
  fetchMain: (id) => departmentService.getDepartmentById(id)
})

const programs = computed(() => Array.isArray(entity.value.programs) ? entity.value.programs : [])
const teachers = computed(() => Array.isArray(entity.value.teachers) ? entity.value.teachers : [])

const profileBadges = computed(() => {
  const badges = []
  if (entity.value.institution_name) badges.push({ text: entity.value.institution_name, class: 'bg-info' })
  return badges
})

const deptInfoItems = computed(() => [
  { label: 'Name', value: entity.value.name },
  { label: 'Code', value: entity.value.code },
  { label: 'Head of Department', value: entity.value.head_of_department || 'Not Assigned' },
  { label: 'Institution', value: entity.value.institution_name || 'N/A' },
  { label: 'Email', value: entity.value.email, href: entity.value.email ? `mailto:${entity.value.email}` : null },
  { label: 'Phone', value: entity.value.phone }
])

const statsData = computed(() => {
  const totalStudents = programs.value.reduce((sum, p) => sum + (p.student_count || 0), 0)
  return [
    { value: programs.value.length, label: 'Programs/Courses', icon: 'bi bi-mortarboard', bgClass: 'bg-admin-light', iconColor: 'text-admin' },
    { value: teachers.value.length, label: 'Teachers', icon: 'bi bi-person-workspace', bgClass: 'bg-success-light', iconColor: 'text-success' },
    { value: totalStudents, label: 'Total Students', icon: 'bi bi-people', bgClass: 'bg-info-light', iconColor: 'text-info' }
  ]
})

const scrollTo = (id) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

