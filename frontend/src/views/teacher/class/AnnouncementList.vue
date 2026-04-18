<template>
  <TeacherPageTemplate title="Announcements" subtitle="Create and manage class announcements" icon="bi bi-megaphone"
    :breadcrumbs="breadcrumbs" :actions="actions">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true"
      :auto-close-duration="3000" @close="alert.show = false" />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <StatCard title="Total Announcements" :value="stats.total" icon="bi bi-megaphone" bg-color="bg-admin-light"
            icon-color="text-teacher" />
        </div>
        <div class="col-md-3">
          <StatCard title="This Week" :value="stats.thisWeek" icon="bi bi-calendar-week" bg-color="bg-success-light"
            icon-color="text-success" />
        </div>
        <div class="col-md-3">
          <StatCard title="Total Views" :value="stats.totalViews" icon="bi bi-eye" bg-color="bg-info-light"
            icon-color="text-info" />
        </div>
        <div class="col-md-3">
          <StatCard title="Urgent" :value="stats.urgent" icon="bi bi-exclamation-triangle" bg-color="bg-danger-light"
            icon-color="text-danger" />
        </div>
      </div>
    </template>

    <!-- Filter Section -->
    <template #filters>
      <SearchFilter v-model="filters.search" :show-card="true" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search announcements..." search-col-size="col-md-3"
        filter-col-size="col-md-3" actions-col-size="col-md-3" theme="teacher" @refresh="loadAnnouncements"
        @reset="resetFilters">
        <template #filters>
          <div class="col-md-3">
            <SelectInput v-model="filters.subject" :options="subjectOptions" placeholder="All Subjects"
              :no-margin="true" />
          </div>
          <div class="col-md-3">
            <SelectInput v-model="filters.priority" :options="ANNOUNCEMENT_PRIORITY_OPTIONS"
              placeholder="All Priorities" :no-margin="true" />
          </div>
        </template>
      </SearchFilter>
    </template>

    <LoadingSpinner v-if="loading" text="Loading announcements..." theme="teacher" />

    <div v-else>
      <!-- Announcements Table -->
      <DataTable :columns="tableColumns" :data="filteredAnnouncements" empty-icon="bi bi-megaphone-fill"
        empty-title="No announcements yet" empty-subtitle="Create your first announcement to notify students">
        <template #cell-title="{ row }">
          <div>
            <div class="fw-bold text-dark">{{ row.title }}</div>
            <div class="small text-muted text-truncate-300" v-html="renderAnnouncementMessage(row.message)"></div>
          </div>
        </template>

        <template #cell-subject="{ row }">
          <span class="badge bg-primary-light text-primary px-3">
            {{ row.subject_name || 'General' }}
          </span>
        </template>

        <template #cell-priority="{ value }">
          <span :class="getPriorityBadge(value)">{{ value }}</span>
        </template>

        <template #cell-created_at="{ value }">
          <div class="small text-muted">
            <i class="bi bi-calendar-event me-1"></i>
            {{ formatDate(value) }}
          </div>
        </template>

        <template #cell-views="{ value }">
          <div class="text-center">
            <span class="badge bg-info-light text-info px-3">
              <i class="bi bi-eye me-1"></i>{{ value }}
            </span>
          </div>
        </template>

        <template #cell-actions="{ row }">
          <div class="d-flex gap-2 justify-content-center">
            <button @click="openEditModalWithData(row)" class="btn btn-sm btn-outline-primary btn-action" title="Edit">
              <i class="bi bi-pencil"></i>
            </button>
            <button @click="confirmDelete(row)" class="btn btn-sm btn-outline-danger btn-action" title="Delete">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Create/Edit Modal -->
    <AnnouncementFormModal v-model="showModal" :form="form" :subjects="subjects" :is-editing="editMode"
      :loading="submitting" @submit="handleSubmit" />

    <!-- Delete Confirmation Modal -->
    <BaseModal v-model="showDeleteModal" title="Delete Announcement" @confirm="handleDelete" :loading="deleting"
      confirm-text="Delete" confirm-variant="btn-danger">
      <div class="p-3 text-center">
        <i class="bi bi-exclamation-triangle text-danger icon-3rem"></i>
        <h5 class="mt-3">Are you sure?</h5>
        <p class="text-muted">
          This will permanently delete the announcement "{{ selectedAnnouncement?.title }}".
          This action cannot be undone.
        </p>
      </div>
    </BaseModal>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { DataTable, BaseModal, StatCard, SearchFilter, SelectInput, AlertMessage, LoadingSpinner } from '@/components/shared/common'
import { AnnouncementFormModal } from '@/components/teacher/shared'
import { useCrudModal } from '@/composables/shared'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { ANNOUNCEMENT_PRIORITY_OPTIONS } from '@/utils/constants/options'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { sanitizeRichHtml } from '@/utils/security'
import { smartSearch } from '@/utils'

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Classes', href: TEACHER_ROUTES.CLASS_LIST.path },
  { name: 'Announcements' }
]

const loading = ref(true)
const announcements = ref([])
const subjects = ref([])
const filters = ref({ search: '', subject: '', priority: '' })

const loadData = async () => {
  loading.value = true
  try {
    const [announcementsData, subjectsData] = await Promise.all([
      teacherPanelService.getAnnouncements(),
      teacherPanelService.getMyClasses()
    ])

    const allAnnouncements = announcementsData.results || announcementsData || []
    subjects.value = subjectsData.results || subjectsData || []

    const teacherSubjectIds = subjects.value.map(s => s.subject_id || s.id)
    announcements.value = allAnnouncements.filter(a => {
      const sId = a.subject_id || a.subject
      return !sId || teacherSubjectIds.includes(sId)
    })
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

// Use CRUD modal composable
const {
  alert,
  showModal,
  showDeleteModal,
  editMode,
  submitting,
  deleting,
  form,
  selectedItem: selectedAnnouncement,
  openCreateModal,
  openEditModal,
  handleSubmit,
  confirmDelete,
  handleDelete
} = useCrudModal({
  entityName: 'Announcement',
  createFn: teacherPanelService.createAnnouncement,
  updateFn: teacherPanelService.updateAnnouncement,
  deleteFn: teacherPanelService.deleteAnnouncement,
  onSuccess: loadData,
  defaultForm: {
    title: '',
    message: '',
    subject: '',
    priority: 'medium',
    send_notification: true
  }
})

const actions = [
  {
    label: 'Create Announcement',
    icon: 'bi bi-plus-lg',
    variant: 'btn-teacher-outline',
    onClick: openCreateModal
  }
]

const tableColumns = [
  { key: 'title', label: 'Announcement' },
  { key: 'subject', label: 'Subject' },
  { key: 'priority', label: 'Priority' },
  { key: 'created_at', label: 'Posted On' },
  { key: 'views', label: 'Views', center: true },
  { key: 'actions', label: 'Actions', center: true }
]

const stats = computed(() => {
  const now = new Date()
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)

  return {
    total: announcements.value.length,
    thisWeek: announcements.value.filter(a => new Date(a.created_at) > weekAgo).length,
    totalViews: announcements.value.reduce((sum, a) => sum + (a.views || 0), 0),
    urgent: announcements.value.filter(a => a.priority === 'urgent').length
  }
})

// Subject options with "Other" option
const subjectOptions = computed(() => {
  const opts = subjects.value.map(s => ({
    value: s.subject_id || s.id,
    label: `${s.subject_name} (${s.subject_code})`
  }))
  // Add "Other" option
  opts.push({ value: 'other', label: 'Other' })
  return opts
})

const filteredAnnouncements = computed(() => {
  // Note: Custom selection mapping ('other' subject handling) requires manual filtering.
  // useFilterLogic omitted to preserve core features. smartSearch used cleanly.
  return announcements.value.filter(a => {
    let searchMatch = true
    if (filters.value.search) {
      const searchFields = ['title', 'message', 'subject_name', 'priority']
      searchMatch = smartSearch(a, filters.value.search, searchFields)
    }

    const sId = a.subject_id || a.subject
    const subjectMatch = !filters.value.subject ||
      (filters.value.subject === 'other' ? !sId : sId == filters.value.subject)
    const priorityMatch = !filters.value.priority || a.priority === filters.value.priority

    return searchMatch && subjectMatch && priorityMatch
  })
})


const getPriorityBadge = (priority) => {
  const badges = {
    urgent: 'badge bg-danger-light text-danger px-3',
    high: 'badge bg-warning-light text-warning px-3',
    medium: 'badge bg-primary-light text-primary px-3',
    low: 'badge bg-light text-muted px-3'
  }
  return badges[priority?.toLowerCase()] || badges.low
}

const formatDate = (dateString) => formatDateUtil(dateString)

const renderAnnouncementMessage = (message) => sanitizeRichHtml(message)

const openEditModalWithData = (announcement) => {
  openEditModal({
    ...announcement,
    subject: announcement.subject_id
  })
}

const loadAnnouncements = () => {
  loadData()
}

const resetFilters = () => {
  filters.value = { search: '', subject: '', priority: '' }
}

onMounted(() => {
  loadData()
})
</script>
