<template>
  <AdminPageTemplate
    title="Edit Semester"
    subtitle="Update semester details"
    icon="bi bi-pencil-square"
    :breadcrumbs="breadcrumbs"
  >
    <div class="row justify-content-center">
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-light border-bottom px-4 py-3">
            <h5 class="card-title mb-0">Semester Information</h5>
          </div>
          <div class="card-body p-4">
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
              <div class="spinner-border text-admin"></div>
            </div>
            <form v-else @submit.prevent="submitForm">
              <div class="mb-3">
                <label for="program-select" class="form-label">Program <span class="text-danger">*</span></label>
                <select id="program-select" v-model="form.program" class="form-select" required>
                  <option value="" disabled>Select Program</option>
                  <option v-for="p in programs" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>

              <div class="mb-3">
                <label for="semester-name" class="form-label">Semester Name <span class="text-danger">*</span></label>
                <input id="semester-name" v-model="form.name" type="text" class="form-control" placeholder="e.g. Fall 2023" required>
              </div>

              <div class="mb-3">
                <label for="semester-number" class="form-label">Semester Number <span class="text-danger">*</span></label>
                <input id="semester-number" v-model.number="form.number" type="number" class="form-control" required min="1">
              </div>

              <div class="row">
                <div class="col-md-6">
                  <BaseInput v-model="form.start_date" label="Start Date" type="date" />
                </div>
                <div class="col-md-6">
                  <BaseInput v-model="form.end_date" label="End Date" type="date" />
                </div>
              </div>

              <div class="mb-3">
                <label for="semester-status" class="form-label">Status</label>
                <select id="semester-status" v-model="form.status" class="form-select">
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" @click="handleCancel" class="btn btn-light">Cancel</button>
                <button type="submit" class="btn btn-admin-primary" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  <span v-if="!submitting"><i class="bi bi-check-circle me-2"></i></span>
                  Update Semester
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { semesterService } from '@/services/semesterService'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const breadcrumbs = [
  { name: 'Dashboard', href: '/admin-dashboard' },
  { name: 'Semesters', href: '/admin-dashboard/semesters' },
  { name: 'Edit' }
]

const loading = ref(true)
const submitting = ref(false)
const programs = ref([])
const alert = ref({ show: false, type: 'success', title: '', message: '' })

const form = ref({
  program: '',
  name: '',
  number: 1,
  start_date: '',
  end_date: '',
  status: 'draft'
})

const showAlert = (type, message, title = null) => {
  alert.value = { show: true, type, title, message }
}

onMounted(async () => {
  const id = route.params.id
  if (!id) {
    router.push('/admin-dashboard/semesters')
    return
  }
  
  try {
    const [sem, progRes] = await Promise.all([
      semesterService.getById(id),
      api.get('/programs/')
    ])
    
    programs.value = Array.isArray(progRes.data) ? progRes.data : (progRes.data.results || progRes.data)
    form.value = {
      program: sem.program,
      name: sem.name,
      number: sem.number,
      start_date: sem.start_date || '',
      end_date: sem.end_date || '',
      status: sem.status || 'draft'
    }
  } catch (e) {
    console.error('Error loading semester:', e)
    showAlert('error', 'Failed to load semester details', 'Error')
    setTimeout(() => router.push('/admin-dashboard/semesters'), 2000)
  } finally {
    loading.value = false
  }
})

const handleCancel = () => {
  if (confirm('Are you sure? All unsaved changes will be lost.')) {
    router.back()
  }
}

const submitForm = async () => {
  submitting.value = true
  try {
    if (!form.value.program || !form.value.name) {
      showAlert('error', 'Please fill in all required fields', 'Validation Error')
      submitting.value = false
      return
    }

    await semesterService.update(route.params.id, form.value)
    showAlert('success', 'Semester updated successfully!', 'Success!')
    setTimeout(() => router.push('/admin-dashboard/semesters'), 1500)
  } catch (e) {
    console.error('Error updating semester:', e.response?.data || e.message)
    const msg = e.response?.data?.detail || e.response?.data?.non_field_errors?.[0] || 'Failed to update semester'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}
</script>
