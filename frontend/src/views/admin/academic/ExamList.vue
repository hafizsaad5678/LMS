<template>
  <AdminPageTemplate title="Exam Schedule" subtitle="Manage examination timetable and schedules" icon="bi bi-clipboard-check" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Exam List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />

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
        search-col-size="col-md-4 col-12"
        actions-col-size="col-md-2 col-6"
        :loading="loading"
        @refresh="loadExams"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Type</label>
            <select v-model="typeFilter" class="form-select" @change="loadExams">
              <option value="">All Types</option>
              <option value="midterm">Midterm</option>
              <option value="final">Final</option>
              <option value="quiz">Quiz</option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Status</label>
            <select v-model="statusFilter" class="form-select" @change="loadExams">
              <option value="">All Status</option>
              <option value="upcoming">Upcoming</option>
              <option value="ongoing">Ongoing</option>
              <option value="completed">Completed</option>
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

    <!-- Modal -->
    <div v-if="showModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">{{ editingExam ? 'Edit Exam' : 'Add Exam' }}</h5><button type="button" class="btn-close" @click="closeModal"></button></div>
          <div class="modal-body">
            <form @submit.prevent="saveExam">
              <div class="mb-3"><label class="form-label">Subject <span class="text-danger">*</span></label><input v-model="examForm.subject" type="text" class="form-control" required></div>
              <div class="row">
                <div class="col-md-6 mb-3"><BaseInput v-model="examForm.exam_date" label="Date" type="date" :required="true" /></div>
                <div class="col-md-6 mb-3"><label class="form-label">Time <span class="text-danger">*</span></label><input v-model="examForm.exam_time" type="time" class="form-control" required></div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Type</label><select v-model="examForm.exam_type" class="form-select"><option value="midterm">Midterm</option><option value="final">Final</option><option value="quiz">Quiz</option></select></div>
                <div class="col-md-6 mb-3"><label class="form-label">Duration (mins)</label><input v-model.number="examForm.duration_minutes" type="number" class="form-control"></div>
              </div>
              <div class="mb-3"><label class="form-label">Room</label><input v-model="examForm.room" type="text" class="form-control"></div>
              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary">{{ editingExam ? 'Update' : 'Add' }}</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage, BaseInput } from '@/components/common'
import { examService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Exams' }]
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

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(false)
const exams = ref([])
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const showModal = ref(false)
const editingExam = ref(null)
const examForm = ref({ subject: '', exam_date: '', exam_time: '', exam_type: 'midterm', duration_minutes: 120, room: '' })

const upcomingExams = computed(() => exams.value.filter(e => new Date(e.exam_date) > new Date()).length)
const ongoingExams = computed(() => exams.value.filter(e => new Date(e.exam_date).toDateString() === new Date().toDateString()).length)
const completedExams = computed(() => exams.value.filter(e => new Date(e.exam_date) < new Date()).length)

const filteredExams = computed(() => {
  let list = exams.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(e => e.subject_name?.toLowerCase().includes(q) || e.subject_code?.toLowerCase().includes(q))
  }
  if (typeFilter.value) list = list.filter(e => e.exam_type === typeFilter.value)
  if (statusFilter.value === 'upcoming') list = list.filter(e => new Date(e.exam_date) > new Date())
  else if (statusFilter.value === 'ongoing') list = list.filter(e => new Date(e.exam_date).toDateString() === new Date().toDateString())
  else if (statusFilter.value === 'completed') list = list.filter(e => new Date(e.exam_date) < new Date())
  return list.sort((a, b) => new Date(a.exam_date) - new Date(b.exam_date))
})

const formatDate = (date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
const getStatus = (date) => new Date(date).toDateString() === new Date().toDateString() ? 'Today' : new Date(date) > new Date() ? 'Upcoming' : 'Completed'
const getStatusBadge = (date) => getStatus(date) === 'Today' ? 'bg-info' : getStatus(date) === 'Upcoming' ? 'bg-success' : 'bg-secondary'

const loadExams = async () => {
  loading.value = true
  try {
    const response = await examService.getAll()
    exams.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading exams:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to load exams' }
  } finally {
    loading.value = false
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

const deleteExam = async (exam) => {
  if (confirm(`Delete exam "${exam.subject_name || exam.subject_code}"?`)) {
    try {
      await examService.delete(exam.id)
      exams.value = exams.value.filter(e => e.id !== exam.id)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Exam deleted' }
    } catch (error) {
      console.error('Error deleting exam:', error)
      alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to delete exam' }
    }
  }
}

const saveExam = async () => {
  try {
    if (editingExam.value) {
      await examService.update(editingExam.value.id, examForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Exam updated' }
    } else {
      await examService.create(examForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Exam added' }
    }
    closeModal()
    loadExams()
  } catch (error) {
    console.error('Error saving exam:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to save exam' }
  }
}

const closeModal = () => {
  showModal.value = false
  editingExam.value = null
  examForm.value = { subject: '', exam_date: '', exam_time: '', exam_type: 'midterm', duration_minutes: 120, room: '' }
}

let searchTimeout
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadExams, 300)
})

onMounted(loadExams)
</script>


