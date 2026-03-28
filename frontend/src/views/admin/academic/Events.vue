<template>
  <AdminPageTemplate title="Events Management" subtitle="Manage academic and institutional events" icon="bi bi-calendar-event" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Event List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />

    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Delete Event"
      :message="eventToDelete ? `Delete event '${eventToDelete.title}'?` : 'Delete this event?'"
      type="danger"
      theme="admin"
      confirm-text="Delete"
      @confirm="confirmDeleteEvent"
    />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Events" :value="events.length" icon="bi bi-calendar-event" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Upcoming" :value="upcomingCount" icon="bi bi-calendar-check" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Today" :value="todayCount" icon="bi bi-clock-history" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Past Events" :value="pastCount" icon="bi bi-calendar-x" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="searchQuery"
        search-placeholder="Search events..."
        :show-status-filter="false"
        :loading="loading"
        @refresh="loadEvents"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <select v-model="typeFilter" class="form-select" @change="loadEvents">
              <option value="">All Types</option>
              <option v-for="opt in EVENT_TYPE_OPTIONS" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <select v-model="statusFilter" class="form-select" @change="loadEvents">
              <option value="">All Status</option>
              <option v-for="opt in EVENT_TIME_STATUS_OPTIONS" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredEvents" :loading="loading" loading-text="Loading events..." empty-icon="bi bi-calendar-event" empty-title="No events found" empty-subtitle="Add your first event to get started">
      <template #cell-title="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-event me-2"><i class="bi bi-calendar-event"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.title }}</div>
            <small class="text-muted d-none d-md-block">{{ truncate(row.description, 30) }}</small>
          </div>
        </div>
      </template>

      <template #cell-event_date="{ row }">
        <div class="fw-medium">{{ formatDate(row.event_date) }}</div>
        <small class="text-muted">{{ row.event_time || 'All Day' }}</small>
      </template>

      <template #cell-event_type="{ value }">
        <span class="badge bg-info text-capitalize">{{ value }}</span>
      </template>

      <template #cell-status="{ row }">
        <span :class="['badge', getStatusBadge(row.event_date)]">{{ getStatus(row.event_date) }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons :item="row" :show-view="false" @edit="editEvent(row)" @delete="deleteEvent(row)" />
      </template>
    </DataTable>

    <!-- Add/Edit Modal using reusable component -->
    <EntityFormModal
      v-model="showAddModal"
      :title="editingEvent ? 'Edit Event' : 'Add New Event'"
      icon="bi bi-calendar-event"
      :loading="saving"
      :confirm-text="editingEvent ? 'Update Event' : 'Add Event'"
      @confirm="saveEvent"
      @close="closeModal"
    >
      <form @submit.prevent="saveEvent">
        <div class="mb-3"><label class="form-label">Event Title <span class="text-danger">*</span></label><input v-model="eventForm.title" type="text" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">Description</label><textarea v-model="eventForm.description" class="form-control" rows="2"></textarea></div>
        <div class="row">
          <div class="col-md-6 mb-3"><BaseInput v-model="eventForm.event_date" label="Date" type="date" :required="true" /></div>
          <div class="col-md-6 mb-3"><label class="form-label">Time</label><input v-model="eventForm.event_time" type="time" class="form-control"></div>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <SelectInput
              v-model="eventForm.event_type"
              :options="EVENT_TYPE_OPTIONS"
              label="Type"
              placeholder="Select event type"
              :required="true"
            />
          </div>
          <div class="col-md-6 mb-3"><label class="form-label">Location</label><input v-model="eventForm.location" type="text" class="form-control" placeholder="e.g., Main Auditorium"></div>
        </div>
      </form>
    </EntityFormModal>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage, BaseInput, ConfirmDialog, EntityFormModal, SelectInput } from '@/components/shared/common'
import { useAlert } from '@/composables/shared'
import { eventService } from '@/services/admin/managementService'
import { formatDate as formatDateUtil, truncateText } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { EVENT_TYPE_OPTIONS, EVENT_TIME_STATUS_OPTIONS } from '@/utils/constants/options'
import { smartSearch } from '@/utils'
import { generateBreadcrumbs } from '@/utils/navigation'

const breadcrumbs = generateBreadcrumbs('admin', 'Events')
const actions = [{ label: 'Add Event', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => showAddModal.value = true }]

const tableColumns = [
  { key: 'title', label: 'Event' },
  { key: 'event_date', label: 'Date & Time' },
  { key: 'event_type', label: 'Type' },
  { key: 'location', label: 'Location', hideOnMobile: true, default: '-' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

// Use shared alert composable
const { alert, showAlert } = useAlert()
const loading = ref(false)
const saving = ref(false)
const events = ref([])
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const showAddModal = ref(false)
const editingEvent = ref(null)
const showConfirmDialog = ref(false)
const eventToDelete = ref(null)
const eventForm = ref({ title: '', description: '', event_date: '', event_time: '', event_type: 'academic', location: '' })

const upcomingCount = computed(() => events.value.filter(e => new Date(e.event_date) > new Date()).length)
const todayCount = computed(() => events.value.filter(e => new Date(e.event_date).toDateString() === new Date().toDateString()).length)
const pastCount = computed(() => events.value.filter(e => new Date(e.event_date) < new Date()).length)

const filteredEvents = computed(() => {
  let list = events.value
  if (searchQuery.value) {
    const searchFields = ['title', 'description', 'location', 'event_type']
    list = list.filter(e => smartSearch(e, searchQuery.value, searchFields))
  }
  if (typeFilter.value) list = list.filter(e => e.event_type === typeFilter.value)
  if (statusFilter.value === 'upcoming') list = list.filter(e => new Date(e.event_date) > new Date())
  else if (statusFilter.value === 'today') list = list.filter(e => new Date(e.event_date).toDateString() === new Date().toDateString())
  else if (statusFilter.value === 'past') list = list.filter(e => new Date(e.event_date) < new Date())
  return list.sort((a, b) => new Date(b.event_date) - new Date(a.event_date))
})

// Use shared formatDate utility
const formatDate = (date) => formatDateUtil(date)

// Use shared truncateText utility
const truncate = (text, length) => truncateText(text, length)

const getStatus = (date) => new Date(date).toDateString() === new Date().toDateString() ? 'Today' : new Date(date) > new Date() ? 'Upcoming' : 'Past'
const getStatusBadge = (date) => getStatus(date) === 'Today' ? 'bg-info' : getStatus(date) === 'Upcoming' ? 'bg-success' : 'bg-secondary'

const loadEvents = async () => {
  loading.value = true
  try {
    const response = await eventService.getAll()
    events.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading events:', error)
    showAlert('error', 'Failed to load events', 'Error')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
  statusFilter.value = ''
}

const editEvent = (event) => {
  editingEvent.value = event
  eventForm.value = { title: event.title, description: event.description, event_date: event.event_date, event_time: event.event_time || '', event_type: event.event_type, location: event.location || '' }
  showAddModal.value = true
}

const deleteEvent = (event) => {
  eventToDelete.value = event
  showConfirmDialog.value = true
}

const confirmDeleteEvent = async () => {
  try {
    await eventService.delete(eventToDelete.value.id)
    events.value = events.value.filter(e => e.id !== eventToDelete.value.id)
    showAlert('success', 'Event deleted successfully', 'Success')
  } catch (error) {
    console.error('Error deleting event:', error)
    showAlert('error', 'Failed to delete event', 'Error')
  } finally {
    showConfirmDialog.value = false
    eventToDelete.value = null
  }
}

const saveEvent = async () => {
  saving.value = true
  try {
    if (editingEvent.value) {
      await eventService.update(editingEvent.value.id, eventForm.value)
      showAlert('success', 'Event updated successfully', 'Success')
    } else {
      await eventService.create(eventForm.value)
      showAlert('success', 'Event added successfully', 'Success')
    }
    closeModal()
    loadEvents()
  } catch (error) {
    console.error('Error saving event:', error)
    showAlert('error', 'Failed to save event', 'Error')
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingEvent.value = null
  eventForm.value = { title: '', description: '', event_date: '', event_time: '', event_type: 'academic', location: '' }
}

let searchTimeout
watch(searchQuery, () => {
  // Local filtering only
})

onMounted(loadEvents)
</script>


