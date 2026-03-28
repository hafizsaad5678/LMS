<template>
  <TeacherPageTemplate title="Grade Management" subtitle="Manage grading components and assessment criteria"
    icon="bi bi-clipboard-data" :breadcrumbs="breadcrumbs" :actions="actions">
    <AlertMessage v-if="alert.show" v-bind="alert" :auto-close="true" @close="alert.show = false" />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 mb-4">
        <div v-for="stat in statsCards" :key="stat.title" class="col-md-3">
          <StatCard v-bind="stat" />
        </div>
      </div>
    </template>

    <LoadingSpinner v-if="loading" text="Loading grade components..." theme="teacher" />

    <div v-else>
      <SearchFilter v-model="searchQuery" :show-card="true" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search components..." search-col-size="col-md-3"
        actions-col-size="col-md-3" theme="teacher" @refresh="loadData" @reset="resetFilters">
        <template #filters>
          <div class="col-md-3">
            <SelectInput v-model="filters.subject" :options="subjectOptions" placeholder="All Subjects"
              :no-margin="true" />
          </div>
          <div class="col-md-3">
            <SelectInput v-model="filters.type" :options="ASSESSMENT_TYPES" placeholder="All Types" :no-margin="true" />
          </div>
        </template>
      </SearchFilter>

      <DataTable :columns="tableColumns" :data="filteredComponents" empty-icon="bi bi-clipboard-x"
        empty-title="No grading components yet">
        <template #cell-name="{ row }">
          <div>
            <div class="fw-bold text-dark">{{ row.name }}</div>
            <div class="small text-muted"><i class="bi bi-book me-1"></i>{{ row.subject_name }}</div>
          </div>
        </template>

        <template #cell-component_type="{ value }">
          <span :class="getAssessmentBadgeClass(value)">{{ getOptionLabel(ASSESSMENT_TYPES, value) }}</span>
        </template>

        <template #cell-weightage="{ value }">
          <div class="text-center"><span class="badge bg-primary-light text-primary px-3 fs-6">{{ value }}%</span></div>
        </template>

        <template #cell-total_marks="{ value }">
          <div class="text-center fw-bold text-dark">{{ value }}</div>
        </template>

        <template #cell-graded="{ row }">
          <div class="text-center">
            <div class="fw-bold text-teacher">{{ row.students_graded }} / {{ row.total_students }}</div>
            <div class="progress progress-mini">
              <div class="progress-bar bg-teacher"
                :style="{ width: (row.total_students ? Math.round((row.students_graded / row.total_students) * 100) : 0) + '%' }">
              </div>
            </div>
          </div>
        </template>

        <template #cell-actions="{ row }">
          <div class="d-flex gap-2 justify-content-center">
            <button
              @click="router.push({ path: TEACHER_ROUTES.GRADE_STUDENTS.path, query: { subject: row.subject, component: row.id } })"
              class="btn btn-sm btn-outline-success btn-action" title="Grade Students"><i
                class="bi bi-pencil-square"></i></button>
            <button @click="openEditModal({ ...row, subject: row.subject || row.subject_id })"
              class="btn btn-sm btn-outline-primary btn-action" title="Edit"><i class="bi bi-gear"></i></button>
            <button @click="confirmDelete(row)" class="btn btn-sm btn-outline-danger btn-action" title="Delete"><i
                class="bi bi-trash"></i></button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Create/Edit Component Modal -->
    <AssessmentFormModal v-model="showModal" :form="form" :subjects="subjects" :is-editing="editMode"
      :loading="submitting" @submit="handleSubmit" />

    <!-- Delete Confirmation Modal -->
    <BaseModal v-model="showDeleteModal" title="Delete Component" @confirm="handleDelete" :loading="deleting"
      confirm-text="Delete" confirm-variant="btn-danger">
      <div class="p-3 text-center">
        <i class="bi bi-exclamation-triangle text-danger icon-3rem"></i>
        <h5 class="mt-3">Are you sure?</h5>
        <p class="text-muted">This will permanently delete "{{ selectedComponent?.name }}" and all associated grades.
        </p>
      </div>
    </BaseModal>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { smartSearch } from '@/utils'
import { useRouter } from 'vue-router'
import { useFilterLogic } from '@/composables/teacher/useFilterLogic'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { DataTable, BaseModal, StatCard, SearchFilter, SelectInput, AlertMessage, LoadingSpinner } from '@/components/shared/common'
import { AssessmentFormModal } from '@/components/teacher/shared'
import { useCrudModal } from '@/composables/shared'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { getAssessmentBadgeClass } from '@/utils/badgeHelpers'
import { ASSESSMENT_TYPES, getOptionLabel } from '@/utils/constants/options'
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const router = useRouter()

const breadcrumbs = [{ name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path }, { name: 'Grade Management' }]

const loading = ref(true)
const components = ref([])
const subjects = ref([])
const filters = ref({ search: '', subject: '', type: '' })

const { alert, showModal, showDeleteModal, editMode, submitting, deleting, form, selectedItem: selectedComponent, openCreateModal, openEditModal, handleSubmit, confirmDelete, handleDelete } = useCrudModal({
  entityName: 'Assessment',
  createFn: teacherPanelService.createGradeComponent,
  updateFn: teacherPanelService.updateGradeComponent,
  deleteFn: teacherPanelService.deleteGradeComponent,
  onSuccess: loadData,
  defaultForm: { name: '', subject: '', component_type: 'assignment', max_marks: 100, weightage: 20, is_visible_to_students: false, description: '' }
})

const actions = [{ label: 'New Assessment', icon: 'bi bi-plus-lg', variant: 'btn-teacher-outline', onClick: openCreateModal }]

const tableColumns = [
  { key: 'name', label: 'Component' },
  { key: 'component_type', label: 'Type' },
  { key: 'weightage', label: 'Weightage', center: true },
  { key: 'total_marks', label: 'Total Marks', center: true },
  { key: 'graded', label: 'Progress', center: true },
  { key: 'actions', label: 'Actions', center: true }
]

const statsCards = computed(() => {
  const subjectIds = new Set(components.value.map(c => c.subject || c.subject_id).filter(Boolean))
  return [
    { title: 'Total Components', value: components.value.length, icon: 'bi bi-list-check', bgColor: 'bg-admin-light', iconColor: 'text-teacher' },
    { title: 'Active Classes', value: subjectIds.size, icon: 'bi bi-book', bgColor: 'bg-success-light', iconColor: 'text-success' },
    { title: 'Students Graded', value: components.value.reduce((sum, c) => sum + (c.students_graded || 0), 0), icon: 'bi bi-people', bgColor: 'bg-info-light', iconColor: 'text-info' },
    { title: 'Pending Grades', value: components.value.reduce((sum, c) => sum + ((c.total_students || 0) - (c.students_graded || 0)), 0), icon: 'bi bi-hourglass-split', bgColor: 'bg-warning-light', iconColor: 'text-warning' }
  ]
})

const subjectOptions = computed(() => subjects.value.map(s => ({ value: s.subject_id || s.id, label: `${s.subject_name} (${s.subject_code})` })))

const filteredComponents = computed(() => {
  // Note: Custom matching logic for multiple ID fields (subject, subject_id, component_type) requires manual filtering.
  // useFilterLogic omitted to preserve core features. smartSearch used cleanly.
  return components.value.filter(c => {
    const searchMatch = smartSearch(c, filters.value.search, ['name', 'subject_name'])
    const subjectMatch = !filters.value.subject || (c.subject || c.subject_id) === filters.value.subject
    const typeMatch = !filters.value.type || c.component_type === filters.value.type
    return searchMatch && subjectMatch && typeMatch
  })
})

async function loadData() {
  loading.value = true
  try {
    const [componentsData, subjectsData] = await Promise.all([teacherPanelService.getGradeComponents(), teacherPanelService.getMyClasses()])
    components.value = componentsData.results || componentsData || []
    subjects.value = subjectsData.results || subjectsData || []
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => { filters.value = { search: '', subject: '', type: '' } }

onMounted(loadData)
</script>
