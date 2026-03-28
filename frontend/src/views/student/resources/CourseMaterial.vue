<template>
  <StudentPageTemplate title="Subject Materials"
    subtitle="Access and download subject materials for your enrolled subjects" icon="bi bi-folder2-open"
    :breadcrumbs="breadcrumbs">
    <!-- Alert Message -->
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true"
      :auto-close-duration="3000" @close="alert.show = false" />

    <!-- Subject Filter -->
    <div class="px-2 pt-1 pb-2">
      <SearchFilter v-model="filters.search" :show-card="false" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search materials..." search-col-size="col-md-5"
        actions-col-size="col-md-3" theme="student" @refresh="loadData" @reset="resetFilters">
        <template #filters>
          <div class="col-md-4">
            <SelectInput v-model="filters.subject" :options="subjectOptions" placeholder="All Subjects"
              :no-margin="true" />
          </div>
        </template>
      </SearchFilter>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" text="Loading materials..." theme="student" class="py-5" />

    <!-- Error State -->
    <AlertMessage v-if="error" type="error" :message="error" title="Error" />

    <!-- Empty State -->
    <div v-else-if="filteredMaterials.length === 0" class="text-center py-5">
      <i class="bi bi-folder-x display-1 text-muted"></i>
      <h3 class="mt-3">No Materials Found</h3>
      <p class="text-muted">
        {{ (filters.search || filters.subject) ? 'Try adjusting your filters' : 'No materials available yet' }}
      </p>
    </div>

    <!-- Materials Grid -->
    <div v-else class="row g-4">
      <div v-for="material in paginatedMaterials" :key="material.id" class="col-12 col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-lift">
          <div class="card-body">
            <div class="d-flex align-items-start mb-3">
              <div class="flex-shrink-0">
                <div class="bg-student-glass rounded-3 p-3 text-student">
                  <i :class="`bi bi-${getFileIcon(material.file_type)} fs-3`"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <h5 class="card-title mb-1 text-truncate">{{ material.title }}</h5>
                <p class="text-muted small mb-0">{{ material.subject_name || material.subject?.name }}</p>
              </div>
            </div>

            <p class="text-muted small mb-3 min-h-40">
              {{ material.description || 'No description available' }}
            </p>

            <div class="d-flex flex-wrap gap-2 mb-3">
              <span class="badge badge-soft-success d-flex align-items-center">
                <i :class="`bi bi-${getFileIcon(material.file_type).replace('-fill', '')} me-1`"></i>
                {{ material.file_type || 'File' }}
              </span>
              <span v-if="material.file_size" class="badge badge-soft-secondary d-flex align-items-center">
                <i class="bi bi-hdd-fill me-1"></i>
                {{ formatFileSize(material.file_size) }}
              </span>
              <span v-if="material.uploaded_at" class="badge badge-soft-success d-flex align-items-center">
                <i class="bi bi-calendar-check-fill me-1"></i>
                {{ formatDate(material.uploaded_at) }}
              </span>
            </div>

            <div class="d-grid gap-2">
              <button class="btn btn-student-primary btn-sm d-flex align-items-center justify-content-center"
                @click="downloadMaterial(material)">
                <i class="bi bi-cloud-arrow-down-fill me-2"></i>
                Download
              </button>
              <button class="btn btn-student-outline btn-sm d-flex align-items-center justify-content-center"
                @click="viewMaterial(material)">
                <i class="bi bi-eye-fill me-2"></i>
                Preview
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-4 d-flex justify-content-center">
      <nav>
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link text-success" @click="changePage(currentPage - 1)">Previous</button>
          </li>
          <li v-for="page in displayPages" :key="page" class="page-item" :class="{ active: page === currentPage }">
            <button class="page-link"
              :class="page === currentPage ? 'bg-gradient-emerald border-success text-white' : 'text-success'"
              @click="changePage(page)">
              {{ page }}
            </button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button class="page-link text-success" @click="changePage(currentPage + 1)">Next</button>
          </li>
        </ul>
      </nav>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { studentService } from '@/services/shared'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, SearchFilter, SelectInput, LoadingSpinner } from '@/components/shared/common'
import studentPanelService from '@/services/student/studentPanelService'
import { formatDate, getFileIcon, formatFileSize } from '@/utils/formatters'
import { useEntityList, usePagination, useAlert } from '@/composables/shared'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const { studentId, loadProfile } = useStudentBase()
const subjects = ref([])
const { alert, showError } = useAlert()

const {
  loading,
  error,
  filteredData: filteredMaterials,
  filters,
  loadData
} = useEntityList({
  cacheKey: `student:${studentId}:materials`,
  searchFields: ['title', 'description', 'subject_name'],
  defaultFilters: { subject: '' },
  customFilter: (items, f) => {
    if (!f.subject) return items
    return items.filter(m => [m.subject_id, m.subject?.id, m.subject].includes(f.subject))
  }
})

const { currentPage, totalItems, totalPages, displayPages, paginate, changePage } = usePagination({ pageSize: 12 })

// Update pagination when filtered data changes
watch(filteredMaterials, (newData) => {
  totalItems.value = newData ? newData.length : 0
  currentPage.value = 1
}, { immediate: true })

const paginatedMaterials = computed(() => paginate(filteredMaterials.value || []))
const breadcrumbs = [{ name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path }, { name: 'Subject Materials' }]



const downloadMaterial = async (m) => {
  if (!m.id) return
  const url = studentPanelService.getFileUrl(m.file_upload || m.file_url)
  if (!url) {
    showError('File URL not found')
    return
  }

  // Track download
  studentPanelService.trackMaterialDownload(m.id)

  try {
    // Fetch the file as a blob to force download
    const response = await fetch(url)
    const blob = await response.blob()

    // Create blob URL and trigger download
    const blobUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = m.title || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // Clean up blob URL
    window.URL.revokeObjectURL(blobUrl)
  } catch (error) {
    console.error('Download error:', error)
    // Fallback to simple download link if fetch fails
    const link = document.createElement('a')
    link.href = url
    link.download = m.title || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const viewMaterial = (m) => router.push(`${STUDENT_ROUTES.COURSE_MATERIAL.path}/preview/${m.id}`)
const resetFilters = () => { filters.value = { search: '', subject: '' } }

const subjectOptions = computed(() => subjects.value.map(sub => ({
  value: sub.subject || sub.subject_id,
  label: `${sub.subject_name || sub.name} (${sub.subject_code || sub.code})`
})))

onMounted(async () => {
  loadProfile()
  await loadData(async () => {
    const res = await studentService.getEnrolledSubjects(studentId)
    subjects.value = Array.isArray(res) ? res : (res.results || [])
    const ids = subjects.value.map(s => s.subject_id || s.subject?.id || s.subject).filter(Boolean)
    return ids.length ? studentPanelService.getMaterialsBySubjects(ids) : []
  })
})
</script>

<!-- Using Bootstrap classes only -->
