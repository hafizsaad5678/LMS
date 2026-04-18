<template>
  <AdminPageTemplate
    title="Subject Management"
    subtitle="View and manage all academic subjects"
    icon="bi bi-book"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Subject List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Subjects" :value="totalSubjects" icon="bi bi-book" type="course" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Credits" :value="totalCredits" icon="bi bi-clock" type="student" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Avg Credits" :value="avgCredits" icon="bi bi-bar-chart" type="course" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Semesters" :value="uniqueSemesters" icon="bi bi-calendar3" type="department" />
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
            v-model="filters.program"
            label="Program"
            placeholder="All Programs"
            :options="programOptions"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
          <SelectInput
            v-model="filters.credits"
            label="Credit Hours"
            placeholder="All Credits"
            :options="creditOptions"
            col-class="col-md-3 col-6"
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
      loading-text="Loading subjects..."
      empty-icon="bi bi-book"
      empty-title="No subjects found"
      empty-subtitle="Try adjusting your filters or add a new subject"
    >
      <template #cell-code="{ value }">
        <span class="badge bg-light text-dark fw-semibold">{{ value }}</span>
      </template>

      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-subject me-2"><i class="bi bi-book"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
          </div>
        </div>
      </template>

      <template #cell-semester_name="{ value }">
        <span class="badge bg-info">{{ value || 'N/A' }}</span>
      </template>

      <template #cell-credit_hours="{ value }">
        <span class="fw-semibold"><i class="bi bi-clock text-muted me-1"></i>{{ value }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-toggle="false"
          @view="router.push({ name: ADMIN_ROUTES.SUBJECT_PROFILE.name, params: { id: row.id } })"
          @edit="router.push({ name: ADMIN_ROUTES.SUBJECT_EDIT.name, params: { id: row.id } })"
          @delete="router.push({ name: ADMIN_ROUTES.SUBJECT_DELETE.name, params: { id: row.id } })"
        />
      </template>
    </DataTable>

    <template #footer>
      <div class="d-flex justify-content-between flex-wrap gap-2">
        <p class="text-muted small mb-0">Total: {{ filteredData.length }} subjects</p>
        <p class="text-muted small mb-0">Credits: {{ totalCredits }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, SelectInput, ActionButtons } from '@/components/shared/common'
import { useEntityList, useFilterOptions, useListStats } from '@/composables/shared'
import { subjectService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Subjects' }
]

const actions = [
  { label: 'Add Subject', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => router.push({ name: ADMIN_ROUTES.SUBJECT_ADD.name }) }
]

const tableColumns = [
  { key: 'code', label: 'Code' },
  { key: 'name', label: 'Subject Name' },
  { key: 'semester_name', label: 'Semester', hideOnMobile: true },
  { key: 'program_name', label: 'Program', hideOnMobile: true, default: 'N/A' },
  { key: 'credit_hours', label: 'Credits', center: true },
  { key: 'actions', label: 'Actions', center: true }
]

const fetchSubjects = async () => {
  const response = await subjectService.getAllSubjects()
  if (Array.isArray(response)) return response
  if (response.results) return response.results
  if (response.data) return Array.isArray(response.data) ? response.data : (response.data.results || [])
  return []
}

const { loading, data, filteredData, filters, loadData, resetFilters, refresh } = useEntityList({
  cacheKey: 'subjects_list',
  searchFields: ['name', 'code'],
  defaultFilters: { program: '', credits: '' },
  filterSchema: [
    {
      key: 'program',
      itemValue: 'program_name',
      normalize: value => String(value || '').trim()
    },
    {
      key: 'credits',
      itemValue: 'credit_hours',
      normalize: value => Number(value || 0)
    }
  ]
})

const scopedSubjects = computed(() => filteredData.value)

const listStats = useListStats(scopedSubjects)

const totalCredits = listStats.sum((subject) => subject.credit_hours)
const avgCredits = listStats.average((subject) => subject.credit_hours)
const uniqueSemesters = listStats.uniqueCount((subject) => subject.semester || subject.semester_name)
const totalSubjects = listStats.count()

const { createPrimitiveOptions } = useFilterOptions(data)

const creditOptions = createPrimitiveOptions({
  value: 'credit_hours',
  sortFn: (a, b) => Number(a) - Number(b)
})

const programOptions = createPrimitiveOptions({ value: 'program_name' })

const handleRefresh = () => refresh(fetchSubjects)

onMounted(() => {
  loadData(fetchSubjects)
})
</script>

