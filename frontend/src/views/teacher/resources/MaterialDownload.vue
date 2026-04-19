<template>
  <TeacherPageTemplate title="Class Materials" subtitle="Manage and download learning resources" icon="bi bi-folder"
    :breadcrumbs="breadcrumbs" :actions="actions">
    <AlertMessage v-if="alert.show" v-bind="alert" :auto-close="true" @close="clearAlert" />
    <ConfirmDialog v-model="showConfirmDialog" title="Delete Material" :message="materialToDelete ?
      `Do you want to delete '${materialToDelete.title}'?`
      : 'Delete this material?'" type="danger" theme="teacher" confirm-text="Delete" @confirm="confirmDeleteMaterial" />

    <template #filters>
      <SearchFilter v-model="filters.search" :show-status-filter="false" :show-labels="false"
        search-placeholder="Search materials..." search-col-size="col-md-3" actions-col-size="col-md-3" theme="teacher"
        @refresh="refreshMaterials" @reset="resetFilters">
        <template #filters>
          <div class="col-md-3">
            <select v-model="filters.subject" class="form-select">
              <option value="">All Subjects</option>
              <option v-for="s in subjects" :key="s.subject_id" :value="s.subject_id">{{ s.subject_name }}</option>
            </select>
          </div>
          <div class="col-md-3">
            <select v-model="filters.type" class="form-select">
              <option value="">All Types</option>
              <option v-for="opt in MATERIAL_TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <LoadingSpinner v-if="loading" text="Loading materials..." theme="teacher" />
    <div v-else-if="finalFilteredData.length === 0" class="text-center py-5">
      <i class="bi bi-folder-x display-1 text-muted"></i>
      <h4 class="text-muted mt-3">No Materials Found</h4>
      <button @click="router.push({ name: TEACHER_ROUTES.MATERIAL_UPLOAD.name })"
        class="btn btn-teacher-primary mt-2"><i class="bi bi-plus-circle me-2">

        </i>Add Material</button>
    </div>

    <div v-else class="row g-4">
      <div v-for="m in finalFilteredData" :key="m.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-card material-download-card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <div class="d-flex align-items-center">
                <div :class="['file-icon me-2', getIcon(m.material_type).class]">
                  <i :class="getIcon(m.material_type).icon"></i>
                </div>
                <div>
                  <h6 class="mb-0 fw-semibold text-truncate">{{ m.title }}</h6>
                  <small class="text-muted">{{ m.subject_name }}</small>
                </div>
              </div>
              <div class="text-end">
                <span :class="['badge rounded-pill px-2 py-1 fw-bold text-uppercase d-inline-block mb-1',
                  getIcon(m.material_type).badge]">
                  {{ formatType(m.material_type) }}</span>
                <span :class="['badge rounded-pill px-2 py-1 fw-bold d-block text-uppercase',
                  getAccess(m.access_level).badge]"><i :class="getAccess(m.access_level).icon" class="me-1">
                  </i>{{ getAccess(m.access_level).label }}</span>
              </div>
            </div>
            <p v-if="m.description" class="text-muted small mb-2 text-truncate">{{ m.description }}</p>
            <div class="d-flex justify-content-between align-items-center mb-2 text-sm material-meta-row">
              <span class="text-muted"><i class="bi bi-calendar me-1">

                </i>{{ formatDate(m.uploaded_at) }}</span>
              <span class="text-muted"><i class="bi bi-download me-1">

                </i>{{ m.download_count || 0 }} downloads</span>
            </div>
            <div class="d-flex gap-2 material-action-row">
              <button @click="downloadFile(m)" class="btn btn-sm btn-teacher-primary flex-grow-1 material-action-btn">
                <i class="bi bi-download me-1"></i>Download</button>
              <button @click="shareLink(m)" class="btn btn-sm btn-teacher-outline material-icon-btn"><i class="bi bi-share">

                </i></button>
              <button @click="materialToDelete = m; showConfirmDialog = true" class="btn btn-sm btn-outline-danger material-icon-btn">
                <i class="bi bi-trash"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { SearchFilter, AlertMessage, ConfirmDialog, LoadingSpinner } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { formatDate } from '@/utils/formatters'
import { MATERIAL_TYPE_OPTIONS, getOptionLabel } from '@/utils/constants/options'
import { getFileUrl } from '@/utils/constants/config'
import { useEntityList, useAlert } from '@/composables/shared'

const router = useRouter()
const { alert, showSuccess, showError, clearAlert } = useAlert()
const { loading, data, filteredData: finalFilteredData, filters, loadData, refresh, resetFilters } = useEntityList({
  cacheKey: 'teacher_materials_list',
  searchFields: ['title', 'description', 'subject_name', 'material_type'],
  defaultFilters: {
    subject: '',
    type: ''
  },
  customFilter: (items, activeFilters) => {
    return items.filter((item) => {
      const matchSubject = !activeFilters.subject || String(item.subject_id) === String(activeFilters.subject)
      const matchType = !activeFilters.type || String(item.material_type) === String(activeFilters.type)
      return matchSubject && matchType
    })
  }
})

const subjects = ref([])
const showConfirmDialog = ref(false)
const materialToDelete = ref(null)

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Resources', href: TEACHER_ROUTES.MATERIAL_DOWNLOAD.path },
  { name: 'Materials' }
]

const actions = [{
  label: 'Add Material', icon: 'bi bi-plus-circle', variant: 'btn-teacher-outline',
  onClick: () => router.push({ name: TEACHER_ROUTES.MATERIAL_UPLOAD.name })
}]

const getIcon = (type) => {
  const map = {
    lecture_notes: { icon: 'bi bi-file-text', class: 'bg-primary-light text-primary', badge: 'bg-primary' },
    slides: { icon: 'bi bi-file-slides', class: 'bg-success-light text-success', badge: 'bg-success' },
    assignment: { icon: 'bi bi-file-earmark-check', class: 'bg-warning-light text-warning', badge: 'bg-warning text-dark' },
    reference: { icon: 'bi bi-book', class: 'bg-info-light text-info', badge: 'bg-info' },
    video: { icon: 'bi bi-play-circle', class: 'bg-danger-light text-danger', badge: 'bg-danger' }
  }
  return map[type] || { icon: 'bi bi-file-earmark', class: 'bg-secondary-light text-secondary', badge: 'bg-secondary' }
}

const getAccess = (level) => {
  const map = {
    public: { badge: 'bg-success', icon: 'bi bi-globe', label: 'All Students' },
    class_only: { badge: 'bg-primary', icon: 'bi bi-people', label: 'Subject Only' },
    restricted: { badge: 'bg-danger', icon: 'bi bi-lock', label: 'Restricted' }
  }
  return map[level] || { badge: 'bg-secondary', icon: 'bi bi-eye', label: level }
}

const formatType = (type) => getOptionLabel(MATERIAL_TYPE_OPTIONS, type)

const refreshMaterials = () => refresh(() => teacherPanelService.getMaterials())

const loadInitial = async () => {
  loadData(() => teacherPanelService.getMaterials())
  try {
    const res = await teacherPanelService.getMyClasses()
    subjects.value = res.results || res || []
  } catch (e) { }
}

const getDownloadName = (m, sourceUrl) => {
  const rawName = sourceUrl?.split('?')[0]?.split('#')[0]?.split('/').pop() || ''
  if (rawName) return decodeURIComponent(rawName)

  const safeTitle = (m?.title || 'material').replace(/[^a-zA-Z0-9-_ ]/g, '').trim().replace(/\s+/g, '_')
  return `${safeTitle || 'material'}`
}

const downloadFile = async (m) => {
  const url = m.file_upload || m.file_url
  if (!url) return showError('No file available.')
  const fullUrl = getFileUrl(url)

  try {
    const response = await fetch(fullUrl, { method: 'GET', credentials: 'include' })
    if (!response.ok) throw new Error('Download request failed')

    const blob = await response.blob()
    const objectUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = getDownloadName(m, fullUrl)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(objectUrl)

    teacherPanelService.incrementDownloadCount(m.id)
      .then(() => {
        m.download_count = (m.download_count || 0) + 1
      })
      .catch(() => {})
  } catch (e) {
    showError('Download failed. Please try again.')
  }
}

const shareLink = async (m) => {
  const url = m.file_upload || m.file_url
  const fullUrl = url.startsWith('http') ? url : `${window.location.origin}${url}`
  try {
    if (navigator.share) await navigator.share({ title: m.title, url: fullUrl })
    else { await navigator.clipboard.writeText(fullUrl); showSuccess('Link copied!') }
  } catch (e) { await navigator.clipboard.writeText(fullUrl); showSuccess('Link copied!') }
}

const confirmDeleteMaterial = async () => {
  try {
    await teacherPanelService.deleteMaterial(materialToDelete.value.id)
    showSuccess('Deleted!')
    refresh(() => teacherPanelService.getMaterials())
  } catch (e) { showError('Failed!') }
  finally { showConfirmDialog.value = false; materialToDelete.value = null }
}

onMounted(loadInitial)
</script>
