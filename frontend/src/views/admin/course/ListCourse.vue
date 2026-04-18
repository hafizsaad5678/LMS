<template>
  <AdminPageTemplate
    title="Course Management"
    subtitle="View and manage all academic programs/courses"
    icon="bi bi-mortarboard"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Course List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Courses" :value="stats.total" icon="bi bi-mortarboard" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Students" :value="stats.totalStudents" icon="bi bi-people" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Avg Duration" :value="stats.avgDuration + ' yrs'" icon="bi bi-calendar-range" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Semesters" :value="stats.totalSemesters" icon="bi bi-calendar3" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search by name or code..."
        preset="admin-list"
        :show-status-filter="false"
        :loading="loading"
        @refresh="handleRefresh"
        @reset="resetFilters"
      >
        <template #filters>
          <SelectInput
            v-model="filters.duration"
            label="Duration"
            placeholder="All Durations"
            :options="COURSE_DURATION_OPTIONS"
            col-class="col-md-4 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="filteredData"
      :loading="loading"
      loading-text="Loading courses..."
      empty-icon="bi bi-mortarboard"
      empty-title="No courses found"
      empty-subtitle="Try adjusting your filters or add a new course"
    >


      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-course me-2"><i class="bi bi-mortarboard"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
            <small class="text-muted d-none d-md-block">{{ row.code }}</small>
          </div>
        </div>
      </template>

      <template #cell-department_name="{ value }">
        <span class="badge bg-light text-dark border">{{ value || 'N/A' }}</span>
      </template>

      <template #cell-duration_years="{ value }">
        <span class="fw-semibold"><i class="bi bi-calendar-range text-muted me-1"></i>{{ value }} Years</span>
      </template>

      <template #cell-semester_count="{ value }">
        <span class="badge bg-info">{{ value || 0 }}</span>
      </template>

      <template #cell-student_count="{ value }">
        <span class="badge bg-success">{{ value || 0 }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="false"
          @view="router.push({ name: ADMIN_ROUTES.COURSE_PROFILE.name, params: { id: row.id } })"
          @edit="router.push({ name: ADMIN_ROUTES.COURSE_EDIT.name, params: { id: row.id } })"
          @delete="router.push({ name: ADMIN_ROUTES.COURSE_DELETE.name, params: { id: row.id } })"
        />
      </template>
    </DataTable>

    <template #footer>
      <div class="d-flex justify-content-between flex-wrap gap-2">
        <p class="text-muted small mb-0">Total: {{ filteredData.length }} courses</p>
        <p class="text-muted small mb-0">Students: {{ stats.totalStudents }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, SelectInput, ActionButtons } from '@/components/shared/common'
import { useEntityList, useListStats } from '@/composables/shared'
import { programService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { COURSE_DURATION_OPTIONS } from '@/utils/constants/options'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Courses' }
]

const actions = [
  { label: 'Add Course', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.COURSE_ADD.name }) }
]

const tableColumns = [
  { key: 'name', label: 'Course' },
  { key: 'department_name', label: 'Department', hideOnMobile: true },
  { key: 'duration_years', label: 'Duration', hideOnMobile: true },
  { key: 'semester_count', label: 'Semesters', center: true },
  { key: 'student_count', label: 'Students', hideOnMobile: true, center: true },
  { key: 'actions', label: 'Actions', center: true }
]

// Use composable for list logic
const {
  loading,
  filteredData,
  filters,
  loadData,
  refresh,
  resetFilters: baseResetFilters
} = useEntityList({
  cacheKey: 'courses_list',
  searchFields: ['name', 'code'],
  defaultFilters: { duration: '' },
  filterSchema: [
    {
      key: 'duration',
      itemValue: 'duration_years',
      normalize: value => Number(value || 0)
    }
  ]
})

const listStats = useListStats(filteredData)

const stats = listStats.summary({
  total: list => list.length,
  totalStudents: list => list.reduce((sum, course) => sum + (course.student_count || 0), 0),
  avgDuration: list => {
    if (!list.length) return 0
    const totalDuration = list.reduce((sum, course) => sum + (course.duration_years || 0), 0)
    return (totalDuration / list.length).toFixed(1)
  },
  totalSemesters: list => list.reduce((sum, course) => sum + (course.semester_count || 0), 0)
})

const fetchCourses = () => programService.getAllPrograms()

const loadCourses = () => loadData(fetchCourses)

const handleRefresh = () => refresh(fetchCourses)

const resetFilters = () => baseResetFilters()

onMounted(loadCourses)
</script>

