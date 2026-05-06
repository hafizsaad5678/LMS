<template>
  <section id="admissions" class="py-5">
    <div class="container py-3">
      <!-- Admissions Disabled State -->
      <div v-if="institution && !institution.show_admissions" class="text-center py-5" data-aos="fade-up">
        <div class="bg-light rounded-4 p-5 shadow-sm border border-brand border-opacity-10">
          <div class="bg-brand-soft rounded-circle d-inline-flex align-items-center justify-content-center size-80 mb-4">
            <i class="bi bi-door-closed fs-1 text-brand"></i>
          </div>
          <h2 class="title-font fw-bold mb-3">Admissions are Currently Closed</h2>
          <p class="text-secondary mx-auto mb-4" style="max-width: 500px;">
            Thank you for your interest in {{ institution.name }}. Our admissions section is currently closed for updates. Please check back later or contact our administration for more information.
          </p>
          <router-link :to="{ name: 'InstitutionPublicProfile', params: { slug: route.params.slug } }" class="btn btn-brand rounded-pill px-4 fw-semibold">
            Back to Home
          </router-link>
        </div>
      </div>

      <!-- Admissions Active State -->
      <template v-else>
        <div class="d-flex align-items-end justify-content-between flex-wrap gap-2 mb-4">
          <div>
            <p class="text-uppercase fw-bold mb-1 text-brand tracking-wider small">Admissions</p>
            <h2 class="mb-0 title-font fs-clamp-md">Session & Admission Details</h2>
          </div>
        </div>

      <!-- Top Admission Info Block -->
      <div v-if="admissions" class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4 position-relative">
        <!-- Subtle background pattern or color accent -->
        <div class="position-absolute top-0 start-0 w-100" style="height: 4px; background: var(--brand);"></div>
        <div class="card-body p-4 p-md-5">
          <div class="d-flex align-items-start gap-4 flex-column flex-md-row">
            <div class="bg-brand-soft rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 size-64 shadow-sm border border-brand border-opacity-25">
              <i class="bi bi-journal-check fs-2 text-brand"></i>
            </div>
            <div class="flex-grow-1">
              <h3 class="h4 fw-bold mb-2 text-dark">{{ admissions.title || 'Admissions' }}</h3>
              <p class="text-secondary mb-0 lh-base">
                {{ admissions.description || 'Admissions details will be shared soon.' }}
              </p>
              
              <!-- Dynamic Program Summary Tags -->
              <div v-if="openPrograms.length > 0 || displayFeaturedAdmissions.length > 0" class="mt-4 pt-4 border-top">
                <p class="small fw-bold text-dark text-uppercase tracking-wider mb-3">
                  <i class="bi bi-megaphone-fill text-brand me-2"></i> Currently Accepting Applications For:
                </p>
                <div class="d-flex flex-wrap gap-2">
                  <!-- Featured Promos -->
                  <span v-for="(promo, index) in displayFeaturedAdmissions" :key="'summary-promo-' + index" 
                    class="badge rounded-pill px-3 py-2 shadow-sm d-flex align-items-center"
                    style="background-color: var(--brand); color: #ffffff;"
                  >
                    <i class="bi bi-star-fill text-warning me-2"></i> {{ promo.title || 'Special Admission' }}
                  </span>
                  
                  <!-- Open Programs -->
                  <span v-for="(prog, index) in openPrograms" :key="'summary-prog-' + prog.id" class="badge bg-white text-dark border border-secondary border-opacity-25 rounded-pill px-3 py-2 shadow-sm d-flex align-items-center">
                    <i class="bi bi-check-circle-fill text-success me-2"></i> {{ prog.name }}
                    <small class="text-muted ms-1 fw-normal" v-if="getAdmissionSession(prog)?.session_name && !getAdmissionSession(prog).session_name.includes(prog.name)">
                      ({{ getAdmissionSession(prog).session_name }})
                    </small>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card border-0 bg-light rounded-4 border p-5 text-center">
        <p class="text-secondary mb-0">No admissions info available.</p>
      </div>

      <!-- Unified Admissions Grid -->
      <div v-if="displayFeaturedAdmissions.length > 0 || openPrograms.length > 0" class="row g-4 py-4">
        <!-- Featured Promo Cards -->
        <div v-for="(card, index) in displayFeaturedAdmissions" :key="'promo-' + index" class="col-md-6 col-lg-4" data-aos="fade-up" :data-aos-delay="index * 50">
          <AdmissionCard 
            :item="card" 
            type="promo" 
            :is-closed="isPromoClosed(card)"
            @apply="openApplyModal" 
            @preview="hoveredImage = $event"
            @download="downloadAd"
          />
        </div>

        <!-- Open Intake Programs Grid -->
        <div v-for="(program, index) in openPrograms" :key="program.id" class="col-md-6 col-lg-4" data-aos="fade-up" :data-aos-delay="(index + displayFeaturedAdmissions.length) * 50">
          <AdmissionCard 
            :item="program" 
            type="program" 
            :deadline="formatAdmissionWindow(getAdmissionSession(program))"
            :is-closed="isProgramClosed(program)"
            @apply="openApplyModal"
            @preview="hoveredImage = $event"
            @download="downloadAd"
          />
        </div>
      </div>
      <div v-else class="card border-0 bg-light rounded-4 border-dashed p-5 text-center mt-4">
        <p class="text-secondary mb-0">No admission programs currently available.</p>
      </div>

      <!-- Large Image Popup (Click to Preview) -->
      <transition name="pop">
        <div v-if="hoveredImage" class="hover-image-popup-overlay" @click="hoveredImage = null">
          <div class="popup-content shadow-lg rounded-4 overflow-hidden bg-white" @click.stop>
            <div class="popup-header p-3 border-bottom d-flex align-items-center justify-content-between">
              <h5 class="fw-bold text-brand mb-0 ms-1">Admission Preview</h5>
              <button type="button" class="btn-close shadow-none" aria-label="Close" @click="hoveredImage = null"></button>
            </div>
            <div class="popup-body p-0 text-center bg-light">
              <img :src="getFileUrl(hoveredImage)" class="img-fluid" alt="Preview" />
            </div>
          </div>
        </div>
      </transition>
      </template>
    </div>
    <!-- Application Modal -->
    <div class="modal fade" id="applyModal" tabindex="-1" aria-labelledby="applyModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 rounded-4 shadow-lg overflow-hidden">
          <div class="modal-header bg-brand-primary text-white border-0 py-3">
            <h5 class="modal-title fw-bold" id="applyModalLabel">
              <i class="bi bi-send-fill me-2"></i>Online Admission Inquiry
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close" id="closeModalBtn" @click="resetForm"></button>
          </div>
          <div class="modal-body p-4">
            <!-- Professional Alert Component Area -->
            <transition name="fade">
              <div v-if="alert.show" :class="['alert alert-dismissible fade show rounded-3 mb-4 d-flex align-items-center', alert.type === 'success' ? 'alert-success border-success' : 'alert-danger border-danger']" role="alert">
                <i :class="['bi me-2 fs-5', alert.type === 'success' ? 'bi-check-circle-fill text-success' : 'bi-exclamation-triangle-fill text-danger']"></i>
                <div class="flex-grow-1">{{ alert.message }}</div>
                <button type="button" class="btn-close shadow-none" @click="alert.show = false"></button>
              </div>
            </transition>

            <form v-if="!submittedSuccessfully" @submit.prevent="submitApplication" id="admissionForm">
              <p class="text-secondary small mb-4">Please fill in your details to inquire about admissions. Only programs currently open for admission are listed.</p>
              
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted text-uppercase">Full Name</label>
                <input v-model="form.name" type="text" class="form-control rounded-3 shadow-none border-2" placeholder="Enter your full name" required>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold text-muted text-uppercase">Father's Name</label>
                <input v-model="form.father_name" type="text" class="form-control rounded-3 shadow-none border-2" placeholder="Enter father's name" required>
              </div>

              <div class="row g-3 mb-3">
                <div class="col-md-6">
                  <label class="form-label small fw-bold text-muted text-uppercase">Phone Number</label>
                  <input v-model="form.phone" type="tel" class="form-control rounded-3 shadow-none border-2" placeholder="e.g. 03001234567" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-bold text-muted text-uppercase">Email Address</label>
                  <input v-model="form.email" type="email" class="form-control rounded-3 shadow-none border-2" placeholder="yourname@gmail.com" required>
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label small fw-bold text-muted text-uppercase">Interested Program</label>
                <select v-model="form.program_id" class="form-select rounded-3 shadow-none border-2" required>
                  <option value="" disabled>Select an open program</option>
                  <optgroup v-for="group in allInquiryOptions" :key="group.id" :label="group.name">
                    <option v-for="prog in group.programs" :key="prog.id" :value="prog.id">
                      {{ prog.name }}
                    </option>
                  </optgroup>
                </select>
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-brand-primary py-2 fw-bold rounded-3 h-100" :disabled="isSubmitting">
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isSubmitting ? 'Processing...' : 'Submit Application' }}
                </button>
              </div>
            </form>

            <!-- Success Message View -->
            <div v-else class="text-center py-4">
              <div class="mb-3 animate__animated animate__zoomIn">
                <i class="bi bi-check-circle-fill text-success display-1"></i>
              </div>
              <h3 class="fw-bold mb-2">Application Sent!</h3>
              <p class="text-secondary px-3">Your admission inquiry for the program has been successfully delivered to the relevant department. We will contact you soon!</p>
              <button type="button" class="btn btn-brand-primary px-5 rounded-pill mt-3 fw-bold" data-bs-dismiss="modal" @click="resetForm">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Admission Alert Popup Modal -->
    <div v-if="showAdmissionAlertModal" class="modal-backdrop fade show" style="z-index: 1050;"></div>
    <div v-if="showAdmissionAlertModal" class="modal fade show d-block" tabindex="-1" role="dialog" style="z-index: 1055;" @click.self="closeAlertModal">
      <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
          <div class="modal-header border-0 pb-0 pt-3 px-4 position-relative z-1 bg-white">
            <h5 class="modal-title fw-bold text-dark fs-4">Admission Open</h5>
            <button type="button" class="btn-close" aria-label="Close" @click="closeAlertModal"></button>
          </div>
          <div class="modal-body p-4 p-md-5">
            <div class="text-center mb-4">
              <div class="icon-circle bg-brand-light text-brand mx-auto mb-3" style="width: 70px; height: 70px; display: flex; align-items: center; justify-content: center; border-radius: 50%;">
                <i class="bi bi-megaphone-fill fs-2"></i>
              </div>
              <h3 class="fw-bold text-dark">Admissions are Open!</h3>
              <p class="text-secondary">We are currently accepting applications for the following programs for the upcoming academic session.</p>
            </div>
            
            <div class="open-programs-list bg-light rounded-4 p-2 p-md-3 mb-3" style="max-height: 350px; overflow-y: auto;">
              <ul class="list-unstyled mb-0">
                <li v-for="(item, index) in allCurrentlyOpen" :key="index" class="d-flex align-items-center mb-2 pb-2 border-bottom" :class="{ 'mb-0 pb-0 border-0': index === allCurrentlyOpen.length - 1 }">
                  <div class="me-3">
                    <i :class="item.type === 'promo' ? 'bi bi-stars text-warning' : 'bi bi-check-circle-fill text-success'" class="fs-6"></i>
                  </div>
                  <div class="flex-grow-1">
                    <h6 class="fw-bold text-dark mb-0 small">{{ item.name }}</h6>
                    <p class="text-muted mb-0" style="font-size: 0.75rem;">
                      <span v-if="item.session" class="me-2">{{ item.session }}</span>
                      <span>{{ item.subtitle }}</span>
                    </p>
                  </div>
                </li>
              </ul>
            </div>
            
            <div class="text-center mt-4">
              <button 
                class="btn btn-brand px-5 py-3 rounded-pill fw-bold w-100 shadow-sm"
                @click="closeAlertModal"
              >
                Got it, Thanks!
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/shared/core/api'
import { getFileUrl } from '@/utils/constants/config'
import AdmissionCard from '@/components/shared/cards/AdmissionCard.vue'

const props = defineProps({
  institution: {
    type: Object,
    default: () => ({})
  },
  admissions: {
    type: Object,
    default: null
  },
  departments: {
    type: Array,
    default: () => []
  }
})

// State
const isSubmitting = ref(false)
const submittedSuccessfully = ref(false)
const showAdmissionAlertModal = ref(false)
const hoveredImage = ref(null)
const alert = ref({
  show: false,
  type: 'success',
  message: ''
})

const form = ref({
  name: '',
  father_name: '',
  phone: '',
  email: '',
  program_id: ''
})

// Computed
const displayFeaturedAdmissions = computed(() => {
  const cards = props.institution?.featured_admissions || []
  // Only show cards that are active
  return cards.filter(card => card.is_active !== false)
})

const openPrograms = computed(() => {
  return props.departments.flatMap((dept) =>
    (dept.programs || [])
      .filter(program => isAdmissionOpen(program))
      .map((program) => ({
        ...program,
        department_name: dept.name,
        department_id: dept.id
      }))
  )
})

const departmentsWithOpenPrograms = computed(() => {
  return props.departments.filter(dept => 
    (dept.programs || []).some(prog => isAdmissionOpen(prog))
  )
})

const allInquiryOptions = computed(() => {
  const options = departmentsWithOpenPrograms.value.map(dept => ({
    ...dept,
    programs: (dept.programs || []).filter(prog => isAdmissionOpen(prog))
  }))
  
  // Identify featured promos that aren't already matching an open program name
  const unmatchedPromos = displayFeaturedAdmissions.value.filter(promo => {
    if (!promo.title) return false
    return !openPrograms.value.some(prog => 
      prog.name.toLowerCase().trim() === promo.title.toLowerCase().trim()
    )
  })

  if (unmatchedPromos.length > 0) {
    options.unshift({
      id: 'featured-virtual-group',
      name: 'Featured Admissions',
      programs: unmatchedPromos.map((promo, idx) => ({
        id: `featured:${promo.title}`, // Virtual ID prefix
        name: promo.title,
        is_virtual: true
      }))
    })
  }
  
  return options
})

const allCurrentlyOpen = computed(() => {
  const promos = displayFeaturedAdmissions.value
    .filter(p => !isPromoClosed(p))
    .map(p => ({
      name: p.title,
      type: 'promo',
      subtitle: 'Featured Program'
    }))
  
  const programs = openPrograms.value
    .filter(p => !isProgramClosed(p))
    .map(p => ({
      name: p.name,
      type: 'program',
      subtitle: p.department_name,
      session: getAdmissionSession(p)?.session_name
    }))
  
  return [...promos, ...programs]
})

// Methods
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return 'TBA'
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const isAdmissionOpen = (program) => {
  const sessions = Array.isArray(program?.admission_sessions) ? program.admission_sessions : []
  return sessions.some(session => session.admissions_open)
}

const getAdmissionSession = (program) => {
  const sessions = Array.isArray(program?.admission_sessions) ? program.admission_sessions : []
  return sessions.find(s => s.admissions_open)
}

const formatAdmissionWindow = (session) => {
  if (!session) return 'Dates to be announced'
  const startDate = session.admission_start_date
  const endDate = session.admission_end_date
  if (startDate && endDate) return `${formatDate(startDate)} - ${formatDate(endDate)}`
  return 'Dates to be announced'
}

const formatLevel = (level) => {
  if (!level) return 'Degree'
  const labels = {
    'bachelor': 'Bachelor (BS)',
    'master': 'Master (MS)',
    'phd': 'Doctorate (PhD)',
    'intermediate': 'Intermediate',
    'diploma': 'Diploma'
  }
  return labels[level.toLowerCase()] || level.charAt(0).toUpperCase() + level.slice(1)
}

const isPromoClosed = (promo) => {
  // Explicitly deactivated
  if (promo.is_active === false) return true
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  // Not yet started
  if (promo.admission_start_date) {
    const start = new Date(promo.admission_start_date)
    start.setHours(0, 0, 0, 0)
    if (today < start) return true
  }
  
  // Already ended
  if (promo.admission_end_date) {
    const end = new Date(promo.admission_end_date)
    end.setHours(0, 0, 0, 0)
    if (today > end) return true
  }
  
  return false
}

const isProgramClosed = (program) => {
  const session = getAdmissionSession(program)
  if (!session) return true
  if (!session.admissions_open) return true
  if (!session.admission_end_date) return false
  
  const end = new Date(session.admission_end_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return end < today
}

const getOpenProgramsByDept = (dept) => {
  return (dept.programs || []).filter(prog => isAdmissionOpen(prog))
}

const showAlert = (type, message) => {
  alert.value = { show: true, type, message }
}

const openApplyModal = (item) => {
  resetForm()
  if (!item) {
    if (openPrograms.value.length > 0) form.value.program_id = openPrograms.value[0].id
    return
  }

  // If it's a real program object (has id)
  if (item.id) {
    form.value.program_id = item.id
    return
  }

  // If it's a promo card (has title)
  if (item.title) {
    const title = item.title.toLowerCase()
    const desc = (item.description || '').toLowerCase()
    
    // 1. Try exact or partial match in title
    let match = openPrograms.value.find(p => 
      title.includes(p.name.toLowerCase()) || 
      p.name.toLowerCase().includes(title)
    )

    // 2. Try match in description keywords (e.g. "ICS", "FSc")
    if (!match) {
      match = openPrograms.value.find(p => 
        desc.includes(p.name.toLowerCase())
      )
    }

    if (match) {
      form.value.program_id = match.id
    } else {
      // Use the virtual ID for the promo so it shows in the dropdown
      form.value.program_id = `featured:${item.title}`
    }
  }
}

const resetForm = () => {
  form.value = { name: '', father_name: '', phone: '', email: '', program_id: '' }
  submittedSuccessfully.value = false
  alert.value.show = false
}

const closeAlertModal = () => {
  showAdmissionAlertModal.value = false
}

const downloadAd = async (imgPath, title) => {
  if (!imgPath) return
  try {
    const url = getFileUrl(imgPath)
    const response = await fetch(url)
    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = blobUrl
    
    let ext = 'png'
    const match = url.match(/\.([a-zA-Z0-9]+)(\?|$)/)
    if (match) {
      ext = match[1]
    }
    
    const safeTitle = (title || 'admission_ad').replace(/[^a-z0-9]/gi, '_').toLowerCase()
    a.download = `${safeTitle}_ad.${ext}`
    
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(blobUrl)
  } catch (error) {
    console.error('Failed to download image:', error)
    window.open(getFileUrl(imgPath), '_blank')
  }
}

const submitApplication = async () => {
  try {
    isSubmitting.value = true
    alert.value.show = false
    
    // Prepare data, handling virtual IDs from featured promos
    const submitData = {
      ...form.value,
      institution_id: props.institution?.id
    }

    // If it's a virtual ID (e.g. "featured:Pre-1st Year"), we handle it
    if (String(submitData.program_id).startsWith('featured:')) {
      const programName = String(submitData.program_id).split(':')[1]
      submitData.program_id = null // The backend likely needs null for non-existent IDs
      submitData.remarks = (submitData.remarks || '') + ` [Interested in Featured Program: ${programName}]`
    }
    
    const response = await api.post('/institution/inquiry/', submitData)
    
    if (response.data.status === 'success' || response.data.status === 'partial_success') {
      submittedSuccessfully.value = true
    } else {
      throw new Error(response.data.message || 'Submission failed')
    }
  } catch (error) {
    console.error('Error submitting application:', error)
    const errorMsg = error.response?.data?.error || 
                     error.response?.data?.message || 
                     'The server is currently unavailable. Please try again later.';
    showAlert('danger', errorMsg)
  } finally {
    isSubmitting.value = false
  }
}

// Hooks
onMounted(() => {
  if (openPrograms.value.length > 0) {
    setTimeout(() => {
      showAdmissionAlertModal.value = true
    }, 500)
  }
})
</script>

<style scoped>
</style>
