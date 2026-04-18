<template>
  <StudentPageTemplate title="Announcements"
    subtitle="Stay updated with important announcements from your teachers and administration" icon="bi bi-megaphone"
    :breadcrumbs="breadcrumbs">
    <!-- Stats Cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3 col-6">
        <StatCard title="Total" :value="totalAnnouncements" icon="bi bi-megaphone-fill" bg-color="bg-student-light"
          icon-color="text-student" />
      </div>
      <div class="col-md-3 col-6">
        <StatCard title="High Priority" :value="highPriorityCount" icon="bi bi-exclamation-triangle-fill"
          bg-color="bg-danger-light" icon-color="text-danger" />
      </div>
      <div class="col-md-3 col-6">
        <StatCard title="Today" :value="todayCount" icon="bi bi-calendar-event-fill" bg-color="bg-success-light"
          icon-color="text-success" />
      </div>
      <div class="col-md-3 col-6">
        <StatCard title="Unread" :value="unreadCount" icon="bi bi-eye-fill" bg-color="bg-info-light"
          icon-color="text-info" />
      </div>
    </div>

    <!-- Filter Section -->
    <div class="px-2 pt-1 pb-2">
      <SearchFilter v-model="filters.search" :show-card="false" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search announcements..." search-col-size="col-md-3"
        filter-col-size="col-md-3" actions-col-size="col-md-3" theme="student" @refresh="loadData" @reset="clearFilters">
        <template #filters>
          <div class="col-md-3">
            <SelectInput v-model="filters.subject" :options="availableSubjects" placeholder="All Subjects"
              :no-margin="true" />
          </div>
          <div class="col-md-3">
            <SelectInput v-model="filters.priority" :options="ANNOUNCEMENT_PRIORITY_OPTIONS" placeholder="All Priorities"
              :no-margin="true" />
          </div>
        </template>
      </SearchFilter>
    </div>


    <!-- Loading State -->
    <LoadingSpinner v-if="loading" text="Loading announcements..." theme="student" />

    <!-- Error State -->
    <AlertMessage v-if="error" type="error" :message="error" title="Error" />

    <!-- Empty State -->
    <div v-else-if="announcements.length === 0" class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-megaphone display-1 text-muted opacity-50"></i>
      </div>
      <h4 class="text-muted mb-3">No Announcements Available</h4>
      <p class="text-muted mb-4">
        <span v-if="filters.subject || filters.priority">
          No announcements match your current filters. Try adjusting your criteria.
        </span>
        <span v-else>
          There are no announcements available at the moment.<br>
          Your teachers will post important updates and announcements here.
        </span>
      </p>
      <div class="mt-3">
        <button v-if="filters.subject || filters.priority" class="btn btn-outline-success" @click="clearFilters">
          <i class="bi bi-x-circle me-2"></i>
          Clear All Filters
        </button>
      </div>
    </div>

    <!-- Announcements List -->
    <div v-else class="row g-4">
      <div v-for="announcement in paginatedAnnouncements" :key="announcement.id" class="col-md-6 col-lg-4">
        <div class="announcement-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden hover-lift">
          <StudentStatusCardHeader
            :header-class="getPriorityHeaderClass(announcement.priority)"
            title-class="text-dark text-truncate-2"
            subtitle-class="text-muted"
          >
            <template #icon>
              <div class="announcement-icon-wrapper p-3 rounded-3 bg-white shadow-sm">
                <i :class="getPriorityIcon(announcement.priority)" class="fs-4" :style="getPriorityIconStyle(announcement.priority)"></i>
              </div>
            </template>
            <template #badges>
              <div class="d-flex flex-column align-items-end gap-2">
                <span class="badge rounded-pill px-3 py-2" :class="getPriorityBadgeClass(announcement.priority)">
                  {{ formatPriority(announcement.priority) }}
                </span>
                <span v-if="!announcement.is_read" class="badge bg-student text-white rounded-pill px-3 py-2">
                  <i class="bi bi-star-fill me-1 small"></i>New
                </span>
              </div>
            </template>
            <template #title>{{ announcement.title }}</template>
            <template #subtitle>
              <div class="d-flex align-items-center gap-2 mt-2">
                <div class="teacher-avatar-xs rounded-circle bg-white d-flex align-items-center justify-content-center text-student fw-bold">
                  {{ (announcement.created_by_name || 'A')[0] }}
                </div>
                <span class="small text-muted fw-medium">{{ announcement.created_by_name || 'Administration' }}</span>
              </div>
            </template>
          </StudentStatusCardHeader>

          <!-- Card Body -->
          <div class="card-body p-4 d-flex flex-column">
            <div class="announcement-meta d-flex justify-content-between mb-3 border-bottom pb-3">
               <div class="meta-item">
                  <small class="text-muted d-block text-uppercase letter-spacing-1 text-xxs-65">Subject</small>
                  <span class="small fw-bold" :class="announcement.subject_name ? 'text-student' : 'text-muted'">
                    <i class="bi bi-journal-bookmark me-1"></i>
                    {{ announcement.subject_name || 'General' }}
                  </span>
               </div>
               <div class="meta-item text-end">
                  <small class="text-muted d-block text-uppercase letter-spacing-1 text-xxs-65">Date</small>
                  <span class="small text-muted">
                    <i class="bi bi-calendar3 me-1"></i>
                    {{ formatRelativeDate(announcement.created_at) }}
                  </span>
               </div>
            </div>

            <div class="announcement-preview mb-4 flex-grow-1">
              <p class="text-muted small mb-0 line-clamp-3" v-html="renderAnnouncementHtml(announcement)"></p>
            </div>

            <!-- Attachment -->
            <div v-if="announcement.attachment || announcement.file_upload" class="attachment-box p-3 bg-light rounded-3 mb-4 d-flex align-items-center">
              <i class="bi bi-file-earmark-pdf-fill text-danger fs-4 me-3"></i>
              <div class="flex-grow-1 overflow-hidden">
                <div class="small fw-bold text-dark text-truncate">{{ announcement.attachment_name || 'Attachment' }}</div>
                <small class="text-muted">Click to download</small>
              </div>
              <button class="btn btn-white btn-sm shadow-sm rounded-circle p-2" @click="downloadAttachment(announcement)">
                <i class="bi bi-download text-student"></i>
              </button>
            </div>

            <!-- Actions -->
            <div class="d-flex gap-2">
              <button class="btn btn-student flex-grow-1 rounded-3 py-2 fw-bold small" @click="toggleDetails(announcement)">
                 View Details
              </button>
              <button v-if="!announcement.is_read" class="btn btn-outline-student rounded-3 p-2" title="Mark as Read" @click="markAsRead(announcement)">
                 <i class="bi bi-check-lg"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <Pagination v-if="totalPages > 1" :current-page="currentPage" :total-pages="totalPages"
      :display-pages="displayPages" theme="student" @change="changePage" />
  </StudentPageTemplate>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, StatCard, SelectInput, SearchFilter, Pagination, LoadingSpinner, StudentStatusCardHeader } from '@/components/shared/common'
import { useEntityList, usePagination } from '@/composables/shared'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { studentService, api } from '@/services/shared'
import { formatDateTime, formatRelativeDate } from '@/utils/formatters'
import { getPriorityBadgeClass, getPriorityIcon } from '@/utils/badgeHelpers'
import { ANNOUNCEMENT_PRIORITY_OPTIONS as PRIORITY_OPTIONS_LIST } from '@/utils/constants/options'
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { STORAGE_KEYS } from '@/utils/constants/storage'
import { sanitizeRichHtml } from '@/utils/security'

const ANNOUNCEMENT_PRIORITY_OPTIONS = PRIORITY_OPTIONS_LIST
const PRIORITY_OPTIONS = PRIORITY_OPTIONS_LIST

const { studentId, loadProfile } = useStudentBase()

const {
  loading,
  error,
  data: allAnnouncements,
  filteredData: announcements,
  filters,
  loadData,
  applyFilters
} = useEntityList({
  cacheKey: `student:${studentId}:announcements`,
  searchFields: ['title', 'message', 'content', 'subject_name'],
  defaultFilters: { subject: '', priority: '' },
  customFilter: (items, f) => {
    let res = items; const readIds = JSON.parse(localStorage.getItem(STORAGE_KEYS.READ_ANNOUNCEMENTS(studentId)) || '[]')
    res.forEach(a => { a.is_read = readIds.includes(a.id); a.showDetails = a.showDetails || false })
    if (f.subject === 'none') {
      res = res.filter(a => !a.subject_name)
    } else if (f.subject) {
      res = res.filter(a => a.subject_name === f.subject)
    }
    if (f.priority) res = res.filter(a => a.priority === f.priority)
    return res.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
})

const { currentPage, totalItems, totalPages, displayPages, paginate, changePage } = usePagination({ pageSize: 15 })

// Update pagination when filtered data changes
watch(announcements, (newData) => {
  totalItems.value = newData ? newData.length : 0
  currentPage.value = 1
}, { immediate: true })

const paginatedAnnouncements = computed(() => paginate(announcements.value || []))

const breadcrumbs = [{ name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path }, { name: 'Announcements' }]

const availableSubjects = computed(() => {
  const subjects = [...new Set(allAnnouncements.value.map(a => a.subject_name).filter(Boolean))].sort()
  const hasNoSubject = allAnnouncements.value.some(a => !a.subject_name)
  const options = subjects.map(s => ({ value: s, label: s }))
  if (hasNoSubject) {
    options.push({ value: 'none', label: 'Other/General' })
  }
  return options
})
const totalAnnouncements = computed(() => announcements.value.length)
const highPriorityCount = computed(() => announcements.value.filter(a => a.priority === 'high').length)
const unreadCount = computed(() => announcements.value.filter(a => !a.is_read).length)
const todayCount = computed(() => {
  const today = new Date().toDateString()
  return announcements.value.filter(a => new Date(a.created_at).toDateString() === today).length
})

const markAsRead = async (announcement) => {
  if (announcement.is_read) return
  announcement.is_read = true; const readIds = JSON.parse(localStorage.getItem(STORAGE_KEYS.READ_ANNOUNCEMENTS(studentId)) || '[]')
  if (!readIds.includes(announcement.id)) {
    readIds.push(announcement.id); localStorage.setItem(STORAGE_KEYS.READ_ANNOUNCEMENTS(studentId), JSON.stringify(readIds))
  }
  try { await api.post(`/announcements/${announcement.id}/mark_read/`) } catch { }
}

const downloadAttachment = async (announcement) => {
  try {
    const res = await api.get(`/announcements/${announcement.id}/download/`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data])); const link = document.createElement('a')
    link.href = url; link.download = announcement.attachment_name || 'attachment'; link.click(); window.URL.revokeObjectURL(url)
  } catch (err) { console.error('Download failed:', err) }
}

const clearFilters = () => { filters.value = { search: '', subject: '', priority: '' } }
const getAnnouncementCardClass = (a) => !a.is_read ? 'border-start-student-thick' : ''
const getPriorityIconClass = (p) => {
  const map = { urgent: 'bg-danger-light text-danger', high: 'bg-warning-light text-warning', medium: 'bg-info-light text-info', low: 'bg-success-light text-success' }
  return map[p] || 'bg-secondary-light text-secondary'
}

const formatPriority = (p) => p ? p.charAt(0).toUpperCase() + p.slice(1) : 'Normal'
const toggleDetails = (a) => a.showDetails = !a.showDetails
const formatTime = (d) => d ? new Date(d).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }) : 'N/A'
const renderAnnouncementHtml = (announcement) => sanitizeRichHtml(announcement?.message || announcement?.content || '')

const getPriorityHeaderClass = (p) => {
  const map = {
    urgent: 'bg-danger-light',
    high: 'bg-warning-light',
    medium: 'bg-info-light'
  }
  return map[p] || 'bg-student-light'
}

const getPriorityIconStyle = (p) => {
  const map = {
    urgent: 'color: #dc3545',
    high: 'color: #ffc107',
    medium: 'color: #0dcaf0'
  }
  return map[p] || 'color: #2e7d32'
}

onMounted(async () => {
  loadProfile()
  await loadData(() => studentService.getAnnouncements(studentId))
  localStorage.setItem(STORAGE_KEYS.VISITED_ANNOUNCEMENTS(studentId), 'true')
})
</script>


