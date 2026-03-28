<template>
  <AdminPageTemplate title="Holidays Management" subtitle="Manage academic and public holidays" icon="bi bi-calendar-x" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Holiday List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />

    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Delete Holiday"
      :message="holidayToDelete ? `Delete holiday '${holidayToDelete.name}'?` : 'Delete this holiday?'"
      type="danger"
      theme="admin"
      confirm-text="Delete"
      @confirm="confirmDeleteHoliday"
    />

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
        <span :class="['badge', getHolidayBadgeClass(value)]">{{ getHolidayLabel(value) }}</span>
      </template>

      <template #cell-duration="{ row }">
        {{ row.duration_days || getDuration(row.start_date, row.end_date) }} day(s)
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons :item="row" :show-view="false" @edit="editHoliday(row)" @delete="deleteHoliday(row)" />
      </template>
    </DataTable>

  </AdminPageTemplate>

  <!-- Modals -->
  <EntityFormModal
    v-model="showModal"
    :title="editingHoliday ? 'Edit Holiday' : 'Add New Holiday'"
    icon="bi bi-calendar-x"
    :loading="saving"
    :confirm-text="editingHoliday ? 'Update Holiday' : 'Add Holiday'"
    @confirm="saveHoliday"
    @close="closeModal"
  >
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
          <option v-for="type in HOLIDAY_TYPE_OPTIONS" :key="type.value" :value="type.value">
            {{ type.label }}
          </option>
        </select>
      </div>
    </form>
  </EntityFormModal>

  <!-- Calendar View Modal (keeping as is - special layout) -->
  <Teleport to="body">
    <div v-if="showCalendarModal" class="modal show d-block modal-overlay" tabindex="-1">
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
                    <span :class="['badge', 'badge-sm', getHolidayBadgeClass(holiday.holiday_type)]">{{ getHolidayLabel(holiday.holiday_type) }}</span>
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
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, ActionButtons, AlertMessage, BaseInput, ConfirmDialog, EntityFormModal } from '@/components/shared/common'
import { useAlert } from '@/composables/shared'
import { holidayService } from '@/services/admin/managementService'
import { formatDate as formatDateUtil, truncateText } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { HOLIDAY_TYPE_OPTIONS, getOptionLabel } from '@/utils/constants/options'
import { getHolidayBadgeClass } from '@/utils/badgeHelpers'

const breadcrumbs = [{ name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path }, { name: 'Holidays' }]
const actions = []

const tableColumns = [
  { key: 'name', label: 'Holiday' },
  { key: 'start_date', label: 'Date' },
  { key: 'holiday_type', label: 'Type' },
  { key: 'duration', label: 'Duration', hideOnMobile: true },
  { key: 'actions', label: 'Actions', center: true }
]

// Use shared alert composable
const { alert, showAlert } = useAlert()
const loading = ref(false)
const saving = ref(false)
const holidays = ref([])
const showModal = ref(false)
const showCalendarModal = ref(false)
const editingHoliday = ref(null)
const holidayForm = ref({ name: '', description: '', start_date: '', end_date: '', holiday_type: 'public' })
const selectedYear = ref(new Date().getFullYear())
const showConfirmDialog = ref(false)
const holidayToDelete = ref(null)

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

// Use shared formatDate utility
const formatDate = (date) => formatDateUtil(date)

// Use shared truncateText utility
const truncate = (text, length) => truncateText(text, length)

const getDuration = (start, end) => (!end || end === start) ? 1 : Math.ceil((new Date(end) - new Date(start)) / (1000 * 60 * 60 * 24)) + 1
const getHolidayLabel = (type) => getOptionLabel(HOLIDAY_TYPE_OPTIONS, type)
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
    showAlert('error', 'Failed to load holidays', 'Error')
  } finally {
    loading.value = false
  }
}

const editHoliday = (holiday) => {
  editingHoliday.value = holiday
  holidayForm.value = { name: holiday.name, description: holiday.description, start_date: holiday.start_date, end_date: holiday.end_date, holiday_type: holiday.holiday_type }
  showModal.value = true
}

const deleteHoliday = (holiday) => {
  holidayToDelete.value = holiday
  showConfirmDialog.value = true
}

const confirmDeleteHoliday = async () => {
  try {
    await holidayService.delete(holidayToDelete.value.id)
    holidays.value = holidays.value.filter(h => h.id !== holidayToDelete.value.id)
    showAlert('success', 'Holiday deleted successfully', 'Success')
  } catch (error) {
    console.error('Error deleting holiday:', error)
    showAlert('error', 'Failed to delete holiday', 'Error')
  } finally {
    showConfirmDialog.value = false
    holidayToDelete.value = null
  }
}

const saveHoliday = async () => {
  saving.value = true
  try {
    if (editingHoliday.value) {
      await holidayService.update(editingHoliday.value.id, holidayForm.value)
      showAlert('success', 'Holiday updated successfully', 'Success')
    } else {
      await holidayService.create(holidayForm.value)
      showAlert('success', 'Holiday added successfully', 'Success')
    }
    closeModal()
    loadHolidays()
  } catch (error) {
    console.error('Error saving holiday:', error)
    showAlert('error', 'Failed to save holiday', 'Error')
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  editingHoliday.value = null
  holidayForm.value = { name: '', description: '', start_date: '', end_date: '', holiday_type: 'public' }
}

onMounted(loadHolidays)
</script>


