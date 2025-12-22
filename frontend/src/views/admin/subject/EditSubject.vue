<template>
  <AdminPageTemplate
    title="Edit Subject"
    subtitle="Update subject information"
    icon="bi bi-book-half"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
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

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading subject details...</p>
    </div>

    <div v-else-if="!subjectId" class="text-center py-5">
      <div class="avatar-circle-lg mx-auto mb-3 bg-light text-muted">
        <i class="bi bi-book display-4"></i>
      </div>
      <h4 class="text-muted">No Subject Selected</h4>
      <p class="text-muted mb-4">Please select a subject from the list to edit.</p>
      <button @click="router.push('/admin-dashboard/subjects')" class="btn btn-admin-primary">
        <i class="bi bi-list-ul me-2"></i>Go to Subject List
      </button>
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="card-title mb-0 fw-semibold">
              <i class="bi bi-book me-2 text-admin"></i>Subject Information
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit">
              <!-- Read-only Info -->
              <div class="mb-4 p-3 bg-light rounded">
                <div class="row">
                  <div class="col-md-6">
                    <label class="form-label text-muted small mb-1">Subject Code</label>
                    <p class="fw-semibold mb-0">{{ form.code }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted small mb-1">Current Program</label>
                    <p class="fw-semibold mb-0">{{ currentProgramName || 'Not Assigned' }}</p>
                  </div>
                </div>
              </div>

              <!-- Basic Information -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-info-circle me-2"></i>Basic Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-8">
                    <BaseInput v-model="form.name" label="Subject Name" type="text" :required="true" />
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model="form.code" label="Subject Code" type="text" :required="true" />
                  </div>
                  <div class="col-md-4">
                    <BaseInput v-model.number="form.credit_hours" label="Credit Hours" type="number" :required="true" />
                  </div>
                </div>
              </div>

              <!-- Course & Semester Selection -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-diagram-3 me-2"></i>Academic Placement
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Program/Course</label>
                      <select v-model="selectedProgram" class="form-select" @change="onProgramChange">
                        <option value="">Select Program</option>
                        <option v-for="prog in programs" :key="prog.id" :value="prog.id">
                          {{ prog.name }} ({{ prog.code }})
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Semester</label>
                      <select v-model="form.semester" class="form-select" :disabled="!selectedProgram || loadingSemesters">
                        <option value="">{{ loadingSemesters ? 'Loading...' : 'Select Semester' }}</option>
                        <option v-for="sem in filteredSemesters" :key="sem.id" :value="sem.id">
                          {{ sem.name }} (Semester {{ sem.number }})
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
                  <i class="bi bi-text-paragraph me-2"></i>Description
                </h6>
                <textarea v-model="form.description" class="form-control" rows="4" placeholder="Enter description..."></textarea>
              </div>

              <!-- Form Actions -->
              <div class="d-flex gap-3 justify-content-end pt-3 border-top">
                <button type="button" @click="handleCancel" class="btn btn-admin-outline px-4" :disabled="submitting">
                  <i class="bi bi-x-circle me-2"></i>Cancel
                </button>
                <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
                  <span v-if="submitting"><span class="spinner-border spinner-border-sm me-2"></span>Updating...</span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Update Subject</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { subjectService } from '@/services/subjectService'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const subjectId = route.params.id

const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Subjects', href: '/admin-dashboard/subjects' },
  { name: 'Edit Subject' }
]

const actions = [
  { label: 'Back to List', icon: 'bi bi-arrow-left', variant: 'btn-admin-outline', onClick: () => router.push('/admin-dashboard/subjects') }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(true)
const submitting = ref(false)
const loadingSemesters = ref(false)
const currentProgramName = ref('')

// Dropdown data
const programs = ref([])
const semesters = ref([])
const selectedProgram = ref('')

const form = ref({ name: '', code: '', semester: '', credit_hours: 3, description: '' })

// Filter semesters based on selected program
const filteredSemesters = computed(() => {
  if (!selectedProgram.value) return semesters.value
  return semesters.value.filter(s => s.program === selectedProgram.value)
})

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

const loadPrograms = async () => {
  try {
    const response = await api.get('/programs/')
    programs.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Error loading programs:', error)
  }
}

const loadSemestersForProgram = async (programId) => {
  if (!programId) return
  
  loadingSemesters.value = true
  try {
    const response = await api.get(`/programs/${programId}/semesters/`)
    const data = Array.isArray(response.data) ? response.data : (response.data.results || [])
    semesters.value = data.map(s => ({ ...s, program: programId }))
  } catch (error) {
    console.error('Error loading semesters:', error)
  } finally {
    loadingSemesters.value = false
  }
}

const onProgramChange = () => {
  form.value.semester = ''
  loadSemestersForProgram(selectedProgram.value)
}

const loadSubject = async () => {
  loading.value = true
  try {
    const subject = await subjectService.getSubjectById(subjectId)
    form.value = {
      name: subject.name || '',
      code: subject.code || '',
      semester: subject.semester || '',
      credit_hours: subject.credit_hours || 3,
      description: subject.description || ''
    }
    
    currentProgramName.value = subject.program_name || subject.semester_program_name || ''
    
    // If subject has a semester, find the program and load semesters
    if (subject.semester) {
      try {
        const semResponse = await api.get(`/semesters/${subject.semester}/`)
        if (semResponse.data?.program) {
          selectedProgram.value = semResponse.data.program
          await loadSemestersForProgram(semResponse.data.program)
        }
      } catch (e) { console.warn('Could not load semester details:', e) }
    }
  } catch (error) {
    console.error('Error loading subject:', error)
    showAlert('error', 'Failed to load subject', 'Error')
    setTimeout(() => router.push('/admin-dashboard/subjects'), 2000)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (!data.semester) delete data.semester
    
    await subjectService.updateSubject(subjectId, data)
    showAlert('success', 'Subject updated successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/subjects'), 1500)
  } catch (error) {
    console.error('Error updating subject:', error)
    showAlert('error', error.response?.data?.detail || 'Failed to update subject.', 'Error!')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => router.push('/admin-dashboard/subjects')

onMounted(async () => {
  await loadPrograms()
  if (subjectId) await loadSubject()
  else loading.value = false
})
</script>

<style scoped>
.form-control:focus, .form-select:focus { border-color: #dc3545; box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.15); }
.card { border-radius: 12px; }
.card-header { background: linear-gradient(135deg, rgba(220, 53, 69, 0.05) 0%, rgba(220, 53, 69, 0.02) 100%); }
.text-admin { color: #dc3545; }
.avatar-circle-lg { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
</style>
