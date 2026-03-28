<template>
  <AdminPageTemplate title="Exam Schedule" subtitle="Manage examination timetable and schedules" icon="bi bi-clipboard-check" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Exam List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />

    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Delete Exam"
      :message="examToDelete ? `Delete exam '${examToDelete.subject_name || examToDelete.subject_code}'?` : 'Delete this exam?'"
      type="danger"
      theme="admin"
      confirm-text="Delete"
      @confirm="confirmDeleteExam"
    />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Exams" :value="exams.length" icon="bi bi-clipboard-check" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Upcoming" :value="upcomingExams" icon="bi bi-calendar-check" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Ongoing" :value="ongoingExams" icon="bi bi-clock" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Completed" :value="completedExams" icon="bi bi-check-circle" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="searchQuery"
        search-placeholder="Search exams..."
        :show-status-filter="false"
        :loading="loading"
        @refresh="loadExams"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <select v-model="typeFilter" class="form-select" @change="loadExams">
              <option value="">All Types</option>
              <option v-for="opt in EXAM_TYPE_OPTIONS" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <select v-model="statusFilter" class="form-select" @change="loadExams">
              <option value="">All Status</option>
              <option v-for="opt in SCHEDULE_STATUS_OPTIONS" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredExams" :loading="loading" loading-text="Loading exams..." empty-icon="bi bi-clipboard-check" empty-title="No exams found" empty-subtitle="Add your first exam to get started">
      <template #cell-subject_name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-exam me-2"><i class="bi bi-clipboard-check"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.subject_name || 'Unknown' }}</div>
            <small class="text-muted">{{ row.subject_code }}</small>
          </div>
        </div>
      </template>

      <template #cell-exam_date="{ row }">
        <div class="fw-medium">{{ formatDate(row.exam_date) }}</div>
        <small class="text-muted">{{ row.exam_time }}</small>
      </template>

      <template #cell-exam_type="{ value }">
        <span class="badge bg-info text-capitalize">{{ value }}</span>
      </template>

      <template #cell-duration_minutes="{ value }">
        {{ value }} mins
      </template>

      <template #cell-status="{ row }">
        <span :class="['badge', getStatusBadge(row.exam_date)]">{{ getStatus(row.exam_date) }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons :item="row" :show-view="false" @edit="editExam(row)" @delete="deleteExam(row)" />
      </template>
    </DataTable>

    <!-- Modal using reusable component -->
    <EntityFormModal
      v-model="showModal"
      :title="editingExam ? 'Edit Exam' : 'Add Exam'"
      icon="bi bi-clipboard-check"
      :loading="saving"
      :confirm-text="editingExam ? 'Update' : 'Add'"
      @confirm="saveExam"
      @close="closeModal"
    >
      <form @submit.prevent="saveExam">
        <div class="mb-3">
          <label class="form-label">Subject <span class="text-danger">*</span></label>
          <select v-model="examForm.subject" class="form-select" required>
            <option value="" disabled>Select Subject</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }} ({{ subject.code }})
            </option>
          </select>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3"><BaseInput v-model="examForm.exam_date" label="Date" type="date" :required="true" /></div>
          <div class="col-md-6 mb-3"><label class="form-label">Time <span class="text-danger">*</span></label><input v-model="examForm.exam_time" type="time" class="form-control" required></div>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <SelectInput
              v-model="examForm.exam_type"
              :options="EXAM_TYPE_OPTIONS"
              label="Type"
              placeholder="Select exam type"
            />
          </div>
          <div class="col-md-6 mb-3"><label class="form-label">Duration (mins)</label><input v-model.number="examForm.duration_minutes" type="number" class="form-control"></div>
        </div>
        <div class="mb-3"><label class="form-label">Room</label><input v-model="examForm.room" type="text" class="form-control"></div>
      </form>
    </EntityFormModal>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { smartSearch } from '@/utils'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage, BaseInput, ConfirmDialog, EntityFormModal, SelectInput } from '@/components/shared/common'
import { useAlert } from '@/composables/shared'
import { examService } from '@/services/admin/managementService'
import { subjectService } from '@/services/shared'
import { normalizeToArray } from '@/services/shared'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { EXAM_TYPE_OPTIONS, SCHEDULE_STATUS_OPTIONS } from '@/utils/constants/options'

const breadcrumbs = [{ name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path }, { name: 'Exams' }]
const actions = [{ label: 'Add Exam', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => showModal.value = true }]

const tableColumns = [
  { key: 'subject_name', label: 'Subject' },
  { key: 'exam_date', label: 'Date & Time' },
  { key: 'exam_type', label: 'Type' },
  { key: 'duration_minutes', label: 'Duration', hideOnMobile: true },
  { key: 'room', label: 'Room', hideOnMobile: true, default: '-' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

// Use shared alert composable
const { alert, showAlert } = useAlert()
const loading = ref(false)
const saving = ref(false)
const exams = ref([])
const subjects = ref([])
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const showModal = ref(false)
const editingExam = ref(null)
const showConfirmDialog = ref(false)
const examToDelete = ref(null)
const examForm = ref({ subject: '', exam_date: '', exam_time: '', exam_type: 'midterm', duration_minutes: 120, room: '' })

const upcomingExams = computed(() => exams.value.filter(e => new Date(e.exam_date) > new Date()).length)
const ongoingExams = computed(() => exams.value.filter(e => new Date(e.exam_date).toDateString() === new Date().toDateString()).length)
const completedExams = computed(() => exams.value.filter(e => new Date(e.exam_date) < new Date()).length)

const filteredExams = computed(() => {
  let list = exams.value
  if (searchQuery.value) {
    list = list.filter(e => smartSearch(e, searchQuery.value, ['subject_name', 'subject_code', 'room', 'exam_type']))
  }
  if (typeFilter.value) list = list.filter(e => e.exam_type === typeFilter.value)
  if (statusFilter.value === 'upcoming') list = list.filter(e => new Date(e.exam_date) > new Date())
  else if (statusFilter.value === 'ongoing') list = list.filter(e => new Date(e.exam_date).toDateString() === new Date().toDateString())
  else if (statusFilter.value === 'completed') list = list.filter(e => new Date(e.exam_date) < new Date())
  return list.sort((a, b) => new Date(a.exam_date) - new Date(b.exam_date))
})

// Use shared formatDate utility
const formatDate = (date) => formatDateUtil(date)

const getStatus = (date) => new Date(date).toDateString() === new Date().toDateString() ? 'Today' : new Date(date) > new Date() ? 'Upcoming' : 'Completed'
const getStatusBadge = (date) => getStatus(date) === 'Today' ? 'bg-info' : getStatus(date) === 'Upcoming' ? 'bg-success' : 'bg-secondary'

const loadExams = async () => {
  loading.value = true
  try {
    const response = await examService.getAll()
    exams.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading exams:', error)
    showAlert('error', 'Failed to load exams', 'Error')
  } finally {
    loading.value = false
  }
}

const loadSubjects = async () => {
  try {
    const response = await subjectService.getAllSubjects()
    subjects.value = normalizeToArray(response)
  } catch (error) {
    console.error('Error loading subjects:', error)
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
  statusFilter.value = ''
}

const editExam = (exam) => {
  editingExam.value = exam
  examForm.value = { subject: exam.subject, exam_date: exam.exam_date, exam_time: exam.exam_time, exam_type: exam.exam_type, duration_minutes: exam.duration_minutes, room: exam.room }
  showModal.value = true
}

const deleteExam = (exam) => {
  examToDelete.value = exam
  showConfirmDialog.value = true
}

const confirmDeleteExam = async () => {
  try {
    await examService.delete(examToDelete.value.id)
    exams.value = exams.value.filter(e => e.id !== examToDelete.value.id)
    showAlert('success', 'Exam deleted', 'Success')
  } catch (error) {
    console.error('Error deleting exam:', error)
    showAlert('error', 'Failed to delete exam', 'Error')
  } finally {
    showConfirmDialog.value = false
    examToDelete.value = null
  }
}

const saveExam = async () => {
  saving.value = true
  try {
    if (editingExam.value) {
      await examService.update(editingExam.value.id, examForm.value)
      showAlert('success', 'Exam updated', 'Success')
    } else {
      await examService.create(examForm.value)
      showAlert('success', 'Exam added', 'Success')
    }
    closeModal()
    loadExams()
  } catch (error) {
    console.error('Error saving exam:', error)
    showAlert('error', 'Failed to save exam', 'Error')
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  editingExam.value = null
  examForm.value = { subject: '', exam_date: '', exam_time: '', exam_type: 'midterm', duration_minutes: 120, room: '' }
}

let searchTimeout
watch(searchQuery, () => {
  // Local filtering only
})

onMounted(() => {
  loadExams()
  loadSubjects()
})
</script>



