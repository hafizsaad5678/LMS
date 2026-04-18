<template>
  <AdminPageTemplate
    title="Add Semester"
    subtitle="Create a new academic semester"
    icon="bi bi-calendar-plus"
    :breadcrumbs="breadcrumbs"
  >
    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Discard Changes"
      message="Are you sure? All unsaved changes will be lost."
      type="warning"
      theme="admin"
      confirm-text="Discard"
      @confirm="confirmCancel"
    />

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
            <div class="mb-4 d-flex justify-content-center">
              <div class="btn-group" role="group">
                <input type="radio" class="btn-check" name="mode" id="single" v-model="mode" value="single" autocomplete="off">
                <label class="btn btn-outline-danger" for="single">Single Semester</label>

                <input type="radio" class="btn-check" name="mode" id="bulk" v-model="mode" value="bulk" autocomplete="off">
                <label class="btn btn-outline-danger" for="bulk">Bulk Create</label>
              </div>
            </div>

            <form @submit.prevent="submitForm">
              <div class="mb-3">
                <label for="program-select" class="form-label">Program <span class="text-danger">*</span></label>
                <select id="program-select" v-model="form.program" class="form-select" required>
                  <option value="" disabled>Select Program</option>
                  <option v-for="p in programs" :key="p.id" :value="p.id">
                    {{ p.name }} ({{ p.duration_years }} Years)
                  </option>
                </select>
              </div>

              <!-- Single Create Fields -->
              <div v-if="mode === 'single'">
                <div class="mb-3">
                  <label for="semester-name" class="form-label">Semester Name <span class="text-danger">*</span></label>
                  <input id="semester-name" v-model="form.name" type="text" class="form-control" placeholder="e.g. Fall 2023" :required="mode === 'single'">
                </div>

                <div class="mb-3">
                  <label for="semester-number" class="form-label">Semester Number <span class="text-danger">*</span></label>
                  <input id="semester-number" v-model.number="form.number" type="number" class="form-control" :required="mode === 'single'" min="1">
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
                  <SelectInput
                    v-model="form.status"
                    :options="SEMESTER_STATUS_OPTIONS"
                    label="Status"
                    placeholder="Select status"
                  />
                </div>
              </div>

              <!-- Bulk Create Fields -->
              <div v-else-if="mode === 'bulk' && form.program">
                <div v-if="bulkSemesters.length > 0" class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>
                  Generating <strong>{{ bulkSemesters.length }}</strong> semester(s) for this program.
                </div>
                <div v-else class="alert alert-warning">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  No semesters to create. This program may already have all required semesters.
                </div>
                
                <div class="table-responsive position-relative max-h-400-scroll">
                  <table class="table table-bordered table-sm">
                    <thead class="table-light sticky-top">
                      <tr>
                        <th class="col-w-60">#</th>
                        <th>Name</th>
                        <th>Start Date</th>
                        <th>End Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(sem, index) in bulkSemesters" :key="index">
                        <td class="text-center align-middle">{{ sem.number }}</td>
                        <td>
                          <input v-model="sem.name" type="text" class="form-control form-control-sm" required>
                        </td>
                        <td>
                          <VueDatePicker
                            v-model="sem.start_date"
                            :enable-time-picker="false"
                            model-type="yyyy-MM-dd"
                            format="yyyy-MM-dd"
                            auto-apply
                            :text-input="false"
                            :state="null"
                            :teleport="false"
                            input-class-name="form-control form-control-sm"
                          />
                        </td>
                        <td>
                          <VueDatePicker
                            v-model="sem.end_date"
                            :enable-time-picker="false"
                            model-type="yyyy-MM-dd"
                            format="yyyy-MM-dd"
                            auto-apply
                            :text-input="false"
                            :state="null"
                            :teleport="false"
                            input-class-name="form-control form-control-sm"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" @click="handleCancel" class="btn btn-light">Cancel</button>
                <button type="submit" class="btn btn-admin-primary" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  <span v-if="!submitting"><i class="bi bi-check-circle me-2"></i></span>
                  {{ mode === 'bulk' ? 'Create Semesters' : 'Save Semester' }}
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
import { ref, onMounted, computed, watch } from 'vue'
import { useAlert } from '@/composables/shared'
import { useRouter, useRoute } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { BaseInput, AlertMessage, ConfirmDialog, SelectInput } from '@/components/shared/common'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { semesterService } from '@/services/shared'
import { api } from '@/services/shared'
import { cacheService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { SEMESTER_STATUS_OPTIONS } from '@/utils/constants/options'

const router = useRouter()
const route = useRoute()
const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Semesters', href: ADMIN_ROUTES.SEMESTER_LIST.path },
  { name: 'Add' }
]

const submitting = ref(false)
const programs = ref([])
const { alert, showAlert } = useAlert()
const mode = ref('single') // single or bulk
const showConfirmDialog = ref(false)

const form = ref({
  program: '',
  name: '',
  number: 1,
  start_date: '',
  end_date: '',
  status: 'draft'
})

const bulkSemesters = ref([])


onMounted(async () => {
  if (route.query.program) {
    form.value.program = route.query.program
  }

  try {
    // Check cache first
    const cached = cacheService.get('programs_list')
    if (cached) {
      programs.value = (Array.isArray(cached) ? cached : []).filter(p => p?.is_active !== false)
      return
    }
    
    const res = await api.get('/programs/')
    const result = (Array.isArray(res.data) ? res.data : (res.data.results || res.data)).filter(p => p?.is_active !== false)
    
    // Store in cache
    cacheService.set('programs_list', result)
    programs.value = result
  } catch (e) {
    console.error('Error loading programs:', e)
    showAlert('error', 'Failed to load programs', 'Error')
  }
})

// Helper function to generate semester dates (6 months apart)
const generateSemesterDates = (semesterIndex, startFromDate = null) => {
  const baseDate = startFromDate ? new Date(startFromDate) : new Date()
  
  // Each semester is 6 months
  const semesterMonths = 6
  
  // Calculate start date for this semester
  const startDate = new Date(baseDate)
  startDate.setMonth(startDate.getMonth() + (semesterIndex * semesterMonths))
  
  // Calculate end date (6 months after start)
  const endDate = new Date(startDate)
  endDate.setMonth(endDate.getMonth() + semesterMonths)
  endDate.setDate(endDate.getDate() - 1) // End day before next semester starts
  
  // Format as yyyy-MM-dd
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  return {
    start_date: formatDate(startDate),
    end_date: formatDate(endDate)
  }
}

// Watch for program change in bulk mode to auto-generate semester rows
watch(() => form.value.program, async (newProgramId) => {
  if (mode.value === 'bulk' && newProgramId) {
    const program = programs.value.find(p => p.id === newProgramId)
    if (program) {
      // Check if semesters already exist for this program
      try {
        const res = await api.get(`/semesters/?program=${newProgramId}`)
        const existingSemesters = Array.isArray(res.data) ? res.data : (res.data.results || [])
        
        // Calculate expected semester count
        const expectedCount = program.duration_years ? program.duration_years * 2 : (program.default_semesters || 8)
        
        if (existingSemesters.length >= expectedCount) {
          showAlert('warning', `This program already has ${existingSemesters.length} semesters created. Cannot create more semesters.`, 'Already Exists')
          bulkSemesters.value = []
          form.value.program = '' // Reset program selection
          return
        }
        
        if (existingSemesters.length > 0) {
          showAlert('info', `This program already has ${existingSemesters.length} semester(s). You can create ${expectedCount - existingSemesters.length} more.`, 'Partial Semesters')
        }
        
        // Generate remaining semesters with default dates (6 months each)
        const startNumber = existingSemesters.length + 1
        const remainingCount = expectedCount - existingSemesters.length
        
        bulkSemesters.value = Array.from({ length: remainingCount }, (_, i) => {
          const dates = generateSemesterDates(i)
          return {
            number: startNumber + i,
            name: `Semester ${startNumber + i}`,
            start_date: dates.start_date,
            end_date: dates.end_date,
            status: 'draft'
          }
        })
      } catch (e) {
        console.error('Error checking existing semesters:', e)
        // If error, proceed with normal generation with default dates
        const semesterCount = program.duration_years ? program.duration_years * 2 : (program.default_semesters || 8)
        
        bulkSemesters.value = Array.from({ length: semesterCount }, (_, i) => {
          const dates = generateSemesterDates(i)
          return {
            number: i + 1,
            name: `Semester ${i + 1}`,
            start_date: dates.start_date,
            end_date: dates.end_date,
            status: 'draft'
          }
        })
      }
    }
  }
})

const handleCancel = () => {
  if (form.value.name || form.value.number > 1 || form.value.program) {
    showConfirmDialog.value = true
  } else {
    router.back()
  }
}

const confirmCancel = () => {
  showConfirmDialog.value = false
  router.back()
}

const submitForm = async () => {
  submitting.value = true
  try {
    if (!form.value.program) {
      showAlert('error', 'Please select a program', 'Validation Error')
      submitting.value = false
      return
    }

    if (mode.value === 'single') {
      if (!form.value.name) {
        showAlert('error', 'Please fill in all required fields', 'Validation Error')
        submitting.value = false
        return
      }
      
      // Check if semester number already exists for this program
      try {
        const res = await api.get(`/semesters/?program=${form.value.program}`)
        const existingSemesters = Array.isArray(res.data) ? res.data : (res.data.results || [])
        const duplicateNumber = existingSemesters.find(s => s.number === form.value.number)
        
        if (duplicateNumber) {
          showAlert('error', `Semester ${form.value.number} already exists for this program. Please choose a different semester number.`, 'Duplicate Semester')
          submitting.value = false
          return
        }
      } catch (e) {
        console.error('Error checking existing semesters:', e)
      }
      
      await semesterService.create(form.value)
    } else {
      // Bulk Create
      if (bulkSemesters.value.length === 0) {
        showAlert('error', 'No semesters to create. This program may already have all semesters.', 'Error')
        submitting.value = false
        return
      }
      const payload = bulkSemesters.value.map(sem => ({
        ...sem,
        program: form.value.program
      }))
      await semesterService.bulkCreate(payload)
    }

    showAlert('success', 'Semester(s) created successfully!', 'Success!')
    setTimeout(() => router.push({ name: ADMIN_ROUTES.SEMESTER_LIST.name, query: { refresh: Date.now() } }), 1500)
  } catch (e) {
    console.error('Error creating semester:', e.response?.data || e.message)
    const programError = e.response?.data?.program
    const sessionError = e.response?.data?.session
    const firstProgramError = Array.isArray(programError) ? programError[0] : programError
    const firstSessionError = Array.isArray(sessionError) ? sessionError[0] : sessionError
    const msg = firstProgramError || firstSessionError || e.response?.data?.detail || e.response?.data?.non_field_errors?.[0] || 'Failed to create semester'
    showAlert('error', msg, 'Error!')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* Datepicker z-index fix - must be scoped for :deep() selector */
:deep(.dp__menu) {
  z-index: 9999 !important;
}
</style>


