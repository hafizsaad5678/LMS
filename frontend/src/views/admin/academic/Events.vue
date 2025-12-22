<template>
  <AdminPageTemplate title="Events Management" subtitle="Manage academic and institutional events" icon="bi bi-calendar-event" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Event List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />

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
        search-col-size="col-md-4 col-12"
        actions-col-size="col-md-2 col-6"
        :loading="loading"
        @refresh="loadEvents"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Type</label>
            <select v-model="typeFilter" class="form-select" @change="loadEvents">
              <option value="">All Types</option>
              <option value="academic">Academic</option>
              <option value="cultural">Cultural</option>
              <option value="sports">Sports</option>
              <option value="seminar">Seminar</option>
              <option value="workshop">Workshop</option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Status</label>
            <select v-model="statusFilter" class="form-select" @change="loadEvents">
              <option value="">All Status</option>
              <option value="upcoming">Upcoming</option>
              <option value="today">Today</option>
              <option value="past">Past</option>
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

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">{{ editingEvent ? 'Edit Event' : 'Add New Event' }}</h5><button type="button" class="btn-close" @click="closeModal"></button></div>
          <div class="modal-body">
            <form @submit.prevent="saveEvent">
              <div class="mb-3"><label class="form-label">Event Title <span class="text-danger">*</span></label><input v-model="eventForm.title" type="text" class="form-control" required></div>
              <div class="mb-3"><label class="form-label">Description</label><textarea v-model="eventForm.description" class="form-control" rows="2"></textarea></div>
              <div class="row">
                <div class="col-md-6 mb-3"><BaseInput v-model="eventForm.event_date" label="Date" type="date" :required="true" /></div>
                <div class="col-md-6 mb-3"><label class="form-label">Time</label><input v-model="eventForm.event_time" type="time" class="form-control"></div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Type <span class="text-danger">*</span></label><select v-model="eventForm.event_type" class="form-select" required><option value="academic">Academic</option><option value="cultural">Cultural</option><option value="sports">Sports</option><option value="seminar">Seminar</option><option value="workshop">Workshop</option></select></div>
                <div class="col-md-6 mb-3"><label class="form-label">Location</label><input v-model="eventForm.location" type="text" class="form-control" placeholder="e.g., Main Auditorium"></div>
              </div>
              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary">{{ editingEvent ? 'Update' : 'Add' }} Event</button>
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
import { eventService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Events' }]
const actions = [{ label: 'Add Event', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => showAddModal.value = true }]

const tableColumns = [
  { key: 'title', label: 'Event' },
  { key: 'event_date', label: 'Date & Time' },
  { key: 'event_type', label: 'Type' },
  { key: 'location', label: 'Location', hideOnMobile: true, default: '-' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(false)
const events = ref([])
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const showAddModal = ref(false)
const editingEvent = ref(null)
const eventForm = ref({ title: '', description: '', event_date: '', event_time: '', event_type: 'academic', location: '' })

const upcomingCount = computed(() => events.value.filter(e => new Date(e.event_date) > new Date()).length)
const todayCount = computed(() => events.value.filter(e => new Date(e.event_date).toDateString() === new Date().toDateString()).length)
const pastCount = computed(() => events.value.filter(e => new Date(e.event_date) < new Date()).length)

const filteredEvents = computed(() => {
  let list = events.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(e => e.title?.toLowerCase().includes(q) || e.description?.toLowerCase().includes(q))
  }
  if (typeFilter.value) list = list.filter(e => e.event_type === typeFilter.value)
  if (statusFilter.value === 'upcoming') list = list.filter(e => new Date(e.event_date) > new Date())
  else if (statusFilter.value === 'today') list = list.filter(e => new Date(e.event_date).toDateString() === new Date().toDateString())
  else if (statusFilter.value === 'past') list = list.filter(e => new Date(e.event_date) < new Date())
  return list.sort((a, b) => new Date(b.event_date) - new Date(a.event_date))
})

const formatDate = (date) => new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
const truncate = (text, length) => text && text.length > length ? text.substring(0, length) + '...' : text || ''
const getStatus = (date) => new Date(date).toDateString() === new Date().toDateString() ? 'Today' : new Date(date) > new Date() ? 'Upcoming' : 'Past'
const getStatusBadge = (date) => getStatus(date) === 'Today' ? 'bg-info' : getStatus(date) === 'Upcoming' ? 'bg-success' : 'bg-secondary'

const loadEvents = async () => {
  loading.value = true
  try {
    const response = await eventService.getAll()
    events.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading events:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to load events' }
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

const deleteEvent = async (event) => {
  if (confirm(`Delete event "${event.title}"?`)) {
    try {
      await eventService.delete(event.id)
      events.value = events.value.filter(e => e.id !== event.id)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Event deleted successfully' }
    } catch (error) {
      console.error('Error deleting event:', error)
      alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to delete event' }
    }
  }
}

const saveEvent = async () => {
  try {
    if (editingEvent.value) {
      await eventService.update(editingEvent.value.id, eventForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Event updated successfully' }
    } else {
      await eventService.create(eventForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Event added successfully' }
    }
    closeModal()
    loadEvents()
  } catch (error) {
    console.error('Error saving event:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to save event' }
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingEvent.value = null
  eventForm.value = { title: '', description: '', event_date: '', event_time: '', event_type: 'academic', location: '' }
}

let searchTimeout
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadEvents, 300)
})

onMounted(loadEvents)
</script>


