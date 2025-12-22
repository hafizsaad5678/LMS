<template>
  <AdminPageTemplate title="Holidays Management" subtitle="Manage academic and public holidays" icon="bi bi-calendar-x" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Holiday List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-4">
          <StatCard title="Total Holidays" :value="holidays.length" icon="bi bi-calendar-x" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Upcoming" :value="upcomingHolidays" icon="bi bi-calendar-check" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Total Days Off" :value="totalDays" icon="bi bi-calendar-range" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <div class="row g-3 align-items-end">
        <div class="col-md-6 col-12">
          <button @click="showCalendarModal = true" class="btn btn-outline-secondary w-100">
            <i class="bi bi-calendar3 me-2"></i>View Calendar
          </button>
        </div>
        <div class="col-md-3 col-6">
          <button @click="loadHolidays" class="btn btn-admin-outline w-100"><i class="bi bi-arrow-clockwise me-2"></i>Refresh</button>
        </div>
        <div class="col-md-3 col-6">
          <button @click="showModal = true" class="btn btn-admin-primary w-100"><i class="bi bi-plus-circle me-2"></i>Add</button>
        </div>
      </div>
    </template>

    <!-- List View -->
    <DataTable :columns="tableColumns" :data="sortedHolidays" :loading="loading" loading-text="Loading holidays..." empty-icon="bi bi-calendar-x" empty-title="No holidays found" empty-subtitle="Add your first holiday to get started">
      <template #cell-name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-holiday me-2"><i class="bi bi-calendar-x"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.name }}</div>
            <small class="text-muted d-none d-md-block">{{ truncate(row.description, 30) }}</small>
          </div>
        </div>
      </template>

      <template #cell-start_date="{ row }">
        <div class="fw-medium">{{ formatDate(row.start_date) }}</div>
        <small v-if="row.end_date && row.end_date !== row.start_date" class="text-muted">to {{ formatDate(row.end_date) }}</small>
      </template>

      <template #cell-holiday_type="{ value }">
        <span :class="['badge', getTypeBadge(value)]">{{ value }}</span>
      </template>

      <template #cell-duration="{ row }">
        {{ row.duration_days || getDuration(row.start_date, row.end_date) }} day(s)
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons :item="row" :show-view="false" @edit="editHoliday(row)" @delete="deleteHoliday(row)" />
      </template>
    </DataTable>

  </AdminPageTemplate>

  <!-- Modals teleported to body for proper overlay -->
  <Teleport to="body">
    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingHoliday ? 'Edit Holiday' : 'Add New Holiday' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveHoliday">
              <div class="mb-3">
                <label class="form-label">Holiday Name <span class="text-danger">*</span></label>
                <input v-model="holidayForm.name" type="text" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="holidayForm.description" class="form-control" rows="2"></textarea>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <BaseInput v-model="holidayForm.start_date" label="Start Date" type="date" :required="true" />
                </div>
                <div class="col-md-6 mb-3">
                  <BaseInput v-model="holidayForm.end_date" label="End Date" type="date" />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Type <span class="text-danger">*</span></label>
                <select v-model="holidayForm.holiday_type" class="form-select" required>
                  <option value="public">Public Holiday</option>
                  <option value="academic">Academic Break</option>
                  <option value="religious">Religious</option>
                  <option value="national">National</option>
                </select>
              </div>
              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary">{{ editingHoliday ? 'Update' : 'Add' }} Holiday</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar View Modal -->
    <div v-if="showCalendarModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050; overflow-y: auto;">
      <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header bg-admin text-white">
            <h5 class="modal-title"><i class="bi bi-calendar3 me-2"></i>Holiday Calendar {{ selectedYear }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="showCalendarModal = false"></button>
          </div>
          <div class="modal-body p-4">
            <!-- Year Selector -->
            <div class="mb-4">
              <div class="d-flex align-items-center justify-content-center gap-3">
                <button @click="selectedYear--" class="btn btn-outline-admin btn-sm">
                  <i class="bi bi-chevron-left"></i>
                </button>
                <select v-model.number="selectedYear" class="form-select form-select-sm w-auto">
                  <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
                </select>
                <button @click="selectedYear++" class="btn btn-outline-admin btn-sm">
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </div>

            <!-- Calendar Grid -->
            <div class="calendar-grid">
              <div v-for="month in 12" :key="month" class="month-card">
                <div class="month-header">{{ getMonthName(month) }} {{ selectedYear }}</div>
                <div class="month-holidays">
                  <div v-for="holiday in getMonthHolidays(month)" :key="holiday.id" class="holiday-item">
                    <i class="bi bi-calendar-x me-2 text-admin"></i>
                    <div class="flex-grow-1">
                      <div class="fw-semibold">{{ holiday.name }}</div>
                      <small class="text-muted">{{ formatDate(holiday.start_date) }}</small>
                    </div>
                    <span :class="['badge', 'badge-sm', getTypeBadge(holiday.holiday_type)]">{{ holiday.holiday_type }}</span>
                  </div>
                  <div v-if="getMonthHolidays(month).length === 0" class="text-muted small text-center py-3">No holidays</div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="showCalendarModal = false" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, ActionButtons, AlertMessage, BaseInput } from '@/components/common'
import { holidayService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Holidays' }]
const actions = []

const tableColumns = [
  { key: 'name', label: 'Holiday' },
  { key: 'start_date', label: 'Date' },
  { key: 'holiday_type', label: 'Type' },
  { key: 'duration', label: 'Duration', hideOnMobile: true },
  { key: 'actions', label: 'Actions', center: true }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(false)
const holidays = ref([])
const showModal = ref(false)
const showCalendarModal = ref(false)
const editingHoliday = ref(null)
const holidayForm = ref({ name: '', description: '', start_date: '', end_date: '', holiday_type: 'public' })
const selectedYear = ref(new Date().getFullYear())

// Generate year options (current year - 2 to current year + 5)
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear - 2; i <= currentYear + 5; i++) {
    years.push(i)
  }
  return years
})

const upcomingHolidays = computed(() => holidays.value.filter(h => new Date(h.start_date) >= new Date()).length)
const totalDays = computed(() => holidays.value.reduce((sum, h) => sum + (h.duration_days || getDuration(h.start_date, h.end_date)), 0))
const sortedHolidays = computed(() => [...holidays.value].sort((a, b) => new Date(a.start_date) - new Date(b.start_date)))

const formatDate = (date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
const truncate = (text, length) => text && text.length > length ? text.substring(0, length) + '...' : text || ''
const getDuration = (start, end) => (!end || end === start) ? 1 : Math.ceil((new Date(end) - new Date(start)) / (1000 * 60 * 60 * 24)) + 1
const getTypeBadge = (type) => ({ public: 'bg-admin', academic: 'bg-info', religious: 'bg-success', national: 'bg-warning' })[type?.toLowerCase()] || 'bg-secondary'
const getMonthName = (month) => new Date(selectedYear.value, month - 1).toLocaleDateString('en-US', { month: 'long' })
const getMonthHolidays = (month) => {
  return holidays.value.filter(h => {
    const holidayDate = new Date(h.start_date)
    return holidayDate.getFullYear() === selectedYear.value && holidayDate.getMonth() + 1 === month
  })
}

const loadHolidays = async () => {
  loading.value = true
  try {
    const response = await holidayService.getAll()
    holidays.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading holidays:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to load holidays' }
  } finally {
    loading.value = false
  }
}

const editHoliday = (holiday) => {
  editingHoliday.value = holiday
  holidayForm.value = { name: holiday.name, description: holiday.description, start_date: holiday.start_date, end_date: holiday.end_date, holiday_type: holiday.holiday_type }
  showModal.value = true
}

const deleteHoliday = async (holiday) => {
  if (confirm(`Delete holiday "${holiday.name}"?`)) {
    try {
      await holidayService.delete(holiday.id)
      holidays.value = holidays.value.filter(h => h.id !== holiday.id)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Holiday deleted successfully' }
    } catch (error) {
      console.error('Error deleting holiday:', error)
      alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to delete holiday' }
    }
  }
}

const saveHoliday = async () => {
  try {
    if (editingHoliday.value) {
      await holidayService.update(editingHoliday.value.id, holidayForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Holiday updated successfully' }
    } else {
      await holidayService.create(holidayForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Holiday added successfully' }
    }
    closeModal()
    loadHolidays()
  } catch (error) {
    console.error('Error saving holiday:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to save holiday' }
  }
}

const closeModal = () => {
  showModal.value = false
  editingHoliday.value = null
  holidayForm.value = { name: '', description: '', start_date: '', end_date: '', holiday_type: 'public' }
}

onMounted(loadHolidays)
</script>


