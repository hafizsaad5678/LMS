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
        :show-status-filter="false"
        search-col-size="col-md-3 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="handleRefresh"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Subject Code</label>
            <select v-model="filters.code" class="form-select">
              <option value="">All Codes</option>
              <option v-for="code in codeOptions" :key="code" :value="code">
                {{ code }}
              </option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Credit Hours</label>
            <select v-model="filters.credits" class="form-select">
              <option value="">All Credits</option>
              <option v-for="credit in creditOptions" :key="credit" :value="credit">
                {{ credit }} {{ credit === 1 ? 'Credit' : 'Credits' }}
              </option>
            </select>
          </div>
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
import { StatCard, DataTable, SearchFilter, ActionButtons } from '@/components/shared/common'
import { useEntityList, useAsyncState } from '@/composables/shared'
import { subjectService } from '@/services/shared'
import adminPanelService from '@/services/admin/adminPanelService'
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
  searchFields: ['name', 'code'],
  defaultFilters: { code: '', credits: '' },
  customFilter: (list, f) => {
    if (f.code) list = list.filter(s => s.code === f.code)
    if (f.credits) list = list.filter(s => s.credit_hours === parseInt(f.credits))
    return list
  }
})

const totalCredits = computed(() => data.value.reduce((sum, s) => sum + (s.credit_hours || 0), 0))
const avgCredits = computed(() => data.value.length > 0 ? (totalCredits.value / data.value.length).toFixed(1) : 0)
const uniqueSemesters = computed(() => new Set(data.value.map(s => s.semester)).size)

const creditOptions = computed(() => {
  const credits = new Set(data.value.map(s => s.credit_hours).filter(c => c != null))
  return Array.from(credits).sort((a, b) => a - b)
})

const codeOptions = computed(() => {
  const codes = new Set(data.value.map(s => s.code).filter(c => c != null && c !== ''))
  return Array.from(codes).sort()
})

const statsLoader = useAsyncState()
const totalSubjects = computed(() => statsLoader.data.value?.subjects || data.value.length)

const handleRefresh = () => refresh(fetchSubjects)

onMounted(() => {
  loadData(fetchSubjects)
  statsLoader.execute(() => adminPanelService.getDashboardStats())
})
</script>

