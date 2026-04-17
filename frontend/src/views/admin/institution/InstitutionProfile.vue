<template>
  <AdminPageTemplate
    title="Institution Profile"
    subtitle="View institution details and statistics"
    icon="bi bi-bank2"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <EmptyState v-if="!entityId" icon="bi bi-bank2" title="Please Select an Institution"
      subtitle="Choose an institution from the list to view its details."
      button-text="Go to Institution List" button-icon="bi bi-list-ul"
      @action="router.push({ name: ADMIN_ROUTES.INSTITUTION_LIST.name })" />

    <LoadingSpinner v-else-if="loading" text="Loading institution details..." theme="admin" />

    <EmptyState v-else-if="!entity.id" icon="bi bi-x-circle" title="Institution Not Found"
      button-text="Back to Institutions" button-icon="bi bi-arrow-left"
      @action="router.push({ name: ADMIN_ROUTES.INSTITUTION_LIST.name })" />

    <div v-else>
      <ProfileHeader
        :name="entity.name"
        :identifier="entity.code"
        :is-active="entity.is_active"
        :badges="profileBadges"
        theme="admin"
        @edit="router.push({ name: ADMIN_ROUTES.INSTITUTION_EDIT.name, params: { id: entity.id } })"
      />

      <div class="row g-4">
        <div class="col-lg-6">
          <InfoCard title="Institution Information" icon="bi bi-info-circle" icon-color="admin" :items="institutionInfoItems" />
        </div>

        <div class="col-lg-6">
          <InfoCard title="Description & Vision" icon="bi bi-text-paragraph" icon-color="success"
            :items="[{ label: 'Description', value: entity.description || 'No description available', multiline: true }]" />
        </div>

        <div class="col-12">
          <StatsGrid :stats="statsData" :columns="4" />
        </div>

        <!-- Departments List -->
        <div class="col-12" id="departments">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-building me-2 text-admin"></i>Departments</h6>
              <div>
                <span class="badge bg-admin me-2">{{ departments.length }} Departments</span>
                <button @click="router.push({ name: ADMIN_ROUTES.DEPARTMENT_ADD.name, query: { institution: entity.id, source: 'institution-profile' } })" 
                        class="btn btn-sm btn-outline-primary py-0" title="Add Department">
                  <i class="bi bi-plus-lg"></i>
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <EmptyState v-if="departments.length === 0" icon="bi bi-inbox" title="No departments in this institution" />
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Code</th>
                      <th>Department Name</th>
                      <th>Programs</th>
                      <th>Teachers</th>
                      <th>Students</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="dept in departments" :key="dept.id">
                      <td><span class="badge bg-dark">{{ dept.code }}</span></td>
                      <td>{{ dept.name }}</td>
                      <td><span class="badge bg-info">{{ dept.program_count || 0 }}</span></td>
                      <td><span class="badge bg-warning text-dark">{{ dept.teacher_count || 0 }}</span></td>
                      <td><span class="badge bg-success">{{ dept.student_count || 0 }}</span></td>
                      <td>
                        <button @click="router.push({ name: ADMIN_ROUTES.DEPARTMENT_PROFILE.name, params: { id: dept.id } })" 
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
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { ProfileHeader, InfoCard, StatsGrid } from '@/components/shared/profile'
import { LoadingSpinner, EmptyState } from '@/components/shared/common'
import { useProfileLoader } from '@/composables/shared'
import { institutionService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const route = useRoute()
const rawId = route.params.id
const institutionIdFromParams = rawId && rawId !== 'profile' ? rawId : null

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Institutions', href: ADMIN_ROUTES.INSTITUTION_LIST.path },
  { name: 'Profile' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push({ name: ADMIN_ROUTES.INSTITUTION_LIST.name }) }
]

const { entityId, loading, entity, subData } = useProfileLoader({
  fetchMain: (id) => institutionService.getInstitutionById(id),
  subResources: [
    { key: 'departments', fetch: (id) => institutionService.getDepartments(id) }
  ],
  idParam: 'id'
})

const departments = computed(() => subData.value.departments || [])

const profileBadges = computed(() => {
  const badges = []
  if (entity.value.short_name) badges.push({ text: entity.value.short_name, class: 'bg-info' })
  if (entity.value.established_year) badges.push({ text: `Est. ${entity.value.established_year}`, class: 'bg-secondary' })
  return badges
})

const institutionInfoItems = computed(() => [
  { label: 'Name', value: entity.value.name },
  { label: 'Code', value: entity.value.code },
  { label: 'Email', value: entity.value.email, href: entity.value.email ? `mailto:${entity.value.email}` : null },
  { label: 'Phone', value: entity.value.phone },
  { label: 'Website', value: entity.value.website, href: entity.value.website },
  { label: 'City', value: entity.value.city },
  { label: 'Address', value: [entity.value.address, entity.value.state].filter(Boolean).join(', ') }
])

const statsData = computed(() => {
  const totalPrograms = departments.value.reduce((sum, d) => sum + (d.program_count || 0), 0)
  const totalTeachers = departments.value.reduce((sum, d) => sum + (d.teacher_count || 0), 0)
  const totalStudents = departments.value.reduce((sum, d) => sum + (d.student_count || 0), 0)
  
  return [
    { value: departments.value.length, label: 'Departments', icon: 'bi bi-building', bgClass: 'bg-admin-light', iconColor: 'text-admin' },
    { value: totalPrograms, label: 'Programs', icon: 'bi bi-mortarboard', bgClass: 'bg-success-light', iconColor: 'text-success' },
    { value: totalTeachers, label: 'Teachers', icon: 'bi bi-person-workspace', bgClass: 'bg-warning-light', iconColor: 'text-warning' },
    { value: totalStudents, label: 'Students', icon: 'bi bi-people', bgClass: 'bg-info-light', iconColor: 'text-info' }
  ]
})
</script>



