<template>
  <TeacherPageTemplate
    title="Upload Material"
    subtitle="Upload and manage learning resources for your classes"
    icon="bi bi-cloud-upload"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :message="alert.message"
      :title="alert.title"
      :auto-close="true"
      :auto-close-duration="3000"
      @close="alert.show = false"
    />

    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h6 class="mb-0 fw-semibold">
              <i class="bi bi-cloud-upload me-2 text-teacher"></i>Upload Resource
            </h6>
          </div>
          <div class="card-body">
            <form @submit.prevent="uploadMaterial">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-semibold">Material Title *</label>
                  <input 
                    v-model="form.title" 
                    type="text" 
                    class="form-control" 
                    placeholder="Enter material title"
                    required
                  >
                </div>
                
                <div class="col-md-6">
                  <label class="form-label fw-semibold">Subject *</label>
                  <select v-model="form.subject_id" class="form-select" required>
                    <option value="">Select subject...</option>
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.subject_id">
                      {{ subject.subject_name }} ({{ subject.subject_code }})
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">Material Type *</label>
                  <select v-model="form.type" class="form-select" required>
                    <option value="">Select type...</option>
                    <option v-for="opt in MATERIAL_TYPE_OPTIONS" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">Access Level</label>
                  <select v-model="form.access_level" class="form-select">
                    <option value="public">All Students</option>
                    <option value="class_only">Subject Only</option>
                    <option value="restricted">Restricted</option>
                  </select>
                  <div class="form-text">Who can view this material?</div>
                </div>

                  <RichTextEditor 
                    v-model="form.description" 
                    placeholder="Brief description of the material..."
                  />

                <div class="col-12">
                  <label class="form-label fw-semibold">Upload File *</label>
                  <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
                    <input 
                      ref="fileInput"
                      type="file" 
                      @change="handleFileSelect"
                      accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.zip,.mp4,.avi,.jpg,.jpeg,.png"
                      class="d-none"
                    >
                    <div v-if="!selectedFile" class="text-center py-4">
                      <i class="bi bi-cloud-upload display-4 text-muted"></i>
                      <p class="mt-2 mb-1">Drag and drop your file here</p>
                      <p class="text-muted small">or <button type="button" @click="$refs.fileInput.click()" class="btn btn-link p-0">browse files</button></p>
                      <small class="text-muted">Supported: PDF, DOC, PPT, ZIP, MP4, Images (Max: 50MB)</small>
                    </div>
                    <div v-else class="text-center py-3">
                      <i class="bi bi-file-earmark-check display-4 text-success"></i>
                      <p class="mt-2 mb-1 fw-semibold">{{ selectedFile.name }}</p>
                      <p class="text-muted small">{{ formatFileSize(selectedFile.size) }}</p>
                      <button type="button" @click="removeFile" class="btn btn-sm btn-outline-danger">
                        <i class="bi bi-trash me-1"></i>Remove
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center mt-4 pt-3 border-top">
                <button type="button" @click="resetForm" class="btn btn-outline-secondary">
                  <i class="bi bi-x-circle me-2"></i>Reset
                </button>
                <button type="submit" class="btn btn-teacher-primary" :disabled="uploading || !selectedFile">
                  <span v-if="uploading">
                    <span class="spinner-border spinner-border-sm me-2"></span>Uploading...
                  </span>
                  <span v-else>
                    <i class="bi bi-upload me-2"></i>Upload Material
                  </span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </TeacherPageTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { useRouter } from 'vue-router'
import { TeacherPageTemplate } from '@/components/shared/panels'
import { AlertMessage, RichTextEditor } from '@/components/shared/common'
import teacherPanelService from '@/services/teacher/teacherPanelService'
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { MATERIAL_TYPE_OPTIONS } from '@/utils/constants/options'

const router = useRouter()

const breadcrumbs = [
  { name: 'Dashboard', href: TEACHER_ROUTES.DASHBOARD.path },
  { name: 'Resources', href: TEACHER_ROUTES.MATERIAL_DOWNLOAD.path },
  { name: 'Upload Material' }
]

const actions = [
  // Link to a view where teacher can see their uploads if it exists, or maybe back to dashboard
  { label: 'Back to Dashboard', icon: 'bi bi-arrow-left', variant: 'btn-teacher-outline', onClick: () => router.push({ name: TEACHER_ROUTES.DASHBOARD.name }) }
]

const uploading = ref(false)
const subjects = ref([])
const selectedFile = ref(null)
const { alert, showAlert } = useAlert()

const form = ref({
  title: '',
  subject_id: '',
  type: '',
  access_level: 'public',
  description: ''
})

const loadSubjects = async () => {
  try {
    const response = await teacherPanelService.getMyClasses()
    subjects.value = response.results || []
  } catch (error) {
    console.error('Error loading subjects:', error)
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  const file = event.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const removeFile = () => {
  selectedFile.value = null
  // Reset input
  // if ($refs.fileInput) $refs.fileInput.value = '' 
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const resetForm = () => {
  form.value = {
    title: '',
    subject_id: '',
    type: '',
    access_level: 'public',
    description: ''
  }
  selectedFile.value = null
}

const uploadMaterial = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.value.title)
    formData.append('subject', form.value.subject_id)
    formData.append('material_type', form.value.type)
    formData.append('description', form.value.description)
    formData.append('file_upload', selectedFile.value)
    formData.append('access_level', form.value.access_level) 

    // Use service method for upload
    await teacherPanelService.createMaterial(formData)
    
    showAlert('success', 'Material uploaded successfully!', 'Success!')
    resetForm()
  } catch (error) {
    console.error('Error uploading material:', error)
    showAlert('error', 'Failed to upload material. Please ensure file size is within limits.', 'Error!')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  loadSubjects()
})
</script>

