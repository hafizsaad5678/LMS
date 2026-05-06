<template>
  <StudentPageTemplate title="Material Preview" :subtitle="material.title || 'Loading...'" icon="bi bi-eye"
    :breadcrumbs="breadcrumbs">
    <LoadingSpinner v-if="loading" text="Loading preview..." theme="student" class="py-5" />
    <AlertMessage v-else-if="error" type="error" :message="error" title="Error">
      <div class="mt-3">
        <button class="btn btn-primary" @click="$router.push(STUDENT_ROUTES.COURSE_MATERIAL.path)">Back to
          Materials</button>
      </div>
    </AlertMessage>

    <div v-else class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
        <div>
          <h5 class="mb-0">{{ material.title }}</h5>
          <small class="text-muted">{{ material.subject_name }}</small>
        </div>
        <div class="btn-group">
          <button class="btn btn-outline-primary btn-sm" @click="downloadFile">
            <i class="bi bi-download me-1"></i> Download
          </button>
          <button class="btn btn-outline-secondary btn-sm" @click="$router.push(STUDENT_ROUTES.COURSE_MATERIAL.path)">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
      <div class="card-body p-0 bg-light text-center min-h-500">
        <!-- PDF Preview -->
        <div v-if="isPdf" class="py-5">
          <div class="display-1 text-muted mb-3">
            <i class="bi bi-file-earmark-pdf"></i>
          </div>
          <h4>PDF preview opens in a new tab</h4>
          <p class="text-muted mb-4">Your browser blocked inline preview. Open the PDF in a separate tab instead.</p>
          <a class="btn btn-primary" :href="fileUrl" target="_blank" rel="noopener">
            <i class="bi bi-box-arrow-up-right me-2"></i>
            Open PDF
          </a>
        </div>

        <!-- Image Preview -->
        <img v-else-if="isImage" :src="fileUrl" class="img-fluid p-3 h-80vh" alt="Preview">

        <!-- Video Preview -->
        <video v-else-if="isVideo" :src="fileUrl" class="w-100 h-80vh" controls></video>

        <!-- Fallback for unsupported types -->
        <div v-else class="py-5">
          <div class="display-1 text-muted mb-3">
            <i :class="`bi bi-${getFileIcon(material.file_type)}`"></i>
          </div>
          <h4>Preview not available for this file type</h4>
          <p class="text-muted mb-4">You can download the file to view it on your device.</p>
          <button class="btn btn-success" @click="downloadFile">
            <i class="bi bi-download me-2"></i>
            Download {{ material.file_type }}
          </button>
        </div>
      </div>
      <div class="card-footer bg-light border-top">
        <small class="text-muted">{{ material.description }}</small>
      </div>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getFileIcon } from '@/utils/formatters'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, LoadingSpinner } from '@/components/shared/common'
import studentPanelService from '@/services/student/studentPanelService'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const route = useRoute()
const router = useRouter()
const materialId = route.params.id

const material = ref({})
const loading = ref(true)
const error = ref(null)

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Subject Materials', href: STUDENT_ROUTES.COURSE_MATERIAL.path },
  { name: 'Preview' }
]

const fileUrl = computed(() => {
  const url = material.value.file_upload || material.value.file_url
  return studentPanelService.getFileUrl(url)
})

const isPdf = computed(() => {
  const url = fileUrl.value || ''
  return url.toLowerCase().endsWith('.pdf')
})

const isImage = computed(() => {
  const url = fileUrl.value || ''
  return url.match(/\.(jpeg|jpg|gif|png|webp)$/i)
})

const isVideo = computed(() => {
  const url = fileUrl.value || ''
  return url.match(/\.(mp4|webm|ogg)$/i)
})

const loadMaterial = async () => {
  loading.value = true
  try {
    material.value = await studentPanelService.getMaterialDetails(materialId)
  } catch (err) {
    console.error('Error loading material:', err)
    error.value = 'Failed to load material information.'
  } finally {
    loading.value = false
  }
}

const downloadFile = async () => {
  if (!fileUrl.value) return

  // Track in background
  studentPanelService.trackMaterialDownload(materialId)

  const link = document.createElement('a')
  link.href = fileUrl.value
  link.download = material.value.title || 'download'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  if (!materialId) {
    error.value = 'Invalid Material ID'
    loading.value = false
    return
  }
  loadMaterial()
})
</script>
