<template>
  <section class="py-5 bg-white">
    <div class="container py-4">
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-3 mb-5">
        <div>
          <p class="text-uppercase fw-bold mb-2 event-subtitle">Campus Life</p>
          <h2 class="mb-0 event-title">Upcoming Events</h2>
        </div>
        <span class="badge rounded-pill py-2 px-3 fw-semibold badge-event">
          {{ items ? items.length : 0 }} Events
        </span>
      </div>
      <div v-if="items && items.length > 0" class="row g-4">
        <div v-for="event in items" :key="event.id" class="col-md-6 col-lg-4">
          <div class="card h-100 border-0 shadow-sm rounded-4 hover-lift">
            <div class="card-body p-4">
              <div class="d-flex align-items-center flex-wrap gap-3 mb-3">
                <span v-if="event.event_date" class="badge bg-light text-dark border d-flex align-items-center gap-1 px-3 py-2 rounded-pill">
                  <i class="bi bi-calendar3 icon-brand"></i> {{ formatDate(event.event_date) }}
                </span>
                <span v-if="event.location" class="text-secondary small d-flex align-items-center gap-1">
                  <i class="bi bi-geo-alt"></i> {{ event.location }}
                </span>
              </div>
              <h3 class="h5 fw-bold mb-2">{{ event.title }}</h3>
              <p class="text-secondary small mb-0 event-desc">{{ event.description || 'Event details will be shared soon.' }}</p>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center p-5 bg-light rounded shadow-sm border">
        <p class="text-muted mb-0">No upcoming events scheduled at the moment.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  },
  emptyMessage: {
    type: String,
    default: 'No events added yet.'
  }
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const parsed = new Date(dateStr)
  if (Number.isNaN(parsed.getTime())) return dateStr
  return parsed.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

