<template>
  <section id="departments" class="py-5 bg-light border-top border-bottom overflow-hidden">
    <div class="container py-4 position-relative">
      <!-- Section Header -->
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-3 mb-5">
        <div>
          <p class="text-uppercase fw-bold mb-2 dept-subtitle">Academic Excellence</p>
          <h2 class="mb-0 dept-title">{{ isHome ? 'Our Departments' : 'Academic Programs' }}</h2>
        </div>
        <div class="d-flex align-items-center gap-2">
          <router-link 
            v-if="isHome" 
            :to="{ name: 'InstitutionPrograms', params: { slug: route.params.slug } }"
            class="btn btn-sm btn-admin-outline rounded-pill px-3 fw-semibold"
          >
            Explore All Programs <i class="bi bi-arrow-right ms-1"></i>
          </router-link>
          <div v-else class="d-flex align-items-center gap-3">
            <!-- Search for Full View -->
            <div class="input-group input-group-sm rounded-pill overflow-hidden shadow-sm border bg-white px-2 py-1 search-container w-100">
              <span class="input-group-text bg-transparent border-0 text-muted"><i class="bi bi-search"></i></span>
              <input 
                v-model="searchQuery" 
                type="text" 
                class="form-control border-0 shadow-none" 
                placeholder="Search programs..."
              >
            </div>
            <span class="badge rounded-pill py-2 px-3 fw-semibold shadow-sm badge-dept">
              {{ allPrograms.length }} Programs
            </span>
          </div>
        </div>
      </div>

      <!-- Home View: Department Cards -->
      <div v-if="isHome" class="row g-4">
        <template v-if="departments.length">
          <div v-for="dept in departments" :key="dept.id" class="col-md-6 col-lg-4">
            <div 
              class="card h-100 border-0 shadow-sm rounded-4 hover-lift transition-all overflow-hidden department-card cursor-pointer"
              :class="{ 'has-image': dept.image }"
              :style="dept.image ? { '--bg-image': `url(${getFileUrl(dept.image)})` } : {}"
              @click="router.push({ name: 'InstitutionPrograms', params: { slug: route.params.slug }, query: { dept: dept.id } })"
            >
              <div class="card-overlay" v-if="dept.image"></div>
              <div class="card-body p-4 position-relative z-1 d-flex flex-column">
                <div class="d-flex align-items-start justify-content-between mb-3">
                  <div class="p-3 rounded-4 shadow-sm icon-wrap" :class="dept.image ? 'bg-white bg-opacity-25' : 'bg-light'">
                    <i class="bi bi-building fs-3" :class="dept.image ? 'text-white' : 'icon-brand'"></i>
                  </div>
                </div>
                
                <h3 class="h5 fw-bold mb-3" :class="dept.image ? 'text-white' : 'text-dark'">{{ dept.name }}</h3>
                <p class="small mb-4 dept-description flex-grow-1" :class="dept.image ? 'text-white-50' : 'text-secondary'">{{ dept.description || 'Our department is dedicated to providing high-quality education.' }}</p>
                
                <div class="mt-auto pt-3">
                  <span class="small fw-bold text-uppercase tracking-wider" :class="dept.image ? 'text-white opacity-75' : 'text-brand'">
                    {{ dept.programs?.length || 0 }} Programs <i class="bi bi-chevron-right ms-1"></i>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </template>
        <div v-else class="col-12">
          <!-- Empty State -->
          <div class="card border-0 bg-light rounded-4 border-dashed p-5 text-center shadow-sm w-100">
            <div class="mb-3">
              <i class="bi bi-journal-text display-1 text-muted opacity-25"></i>
            </div>
            <h5 class="text-dark fw-bold">No Departments Found</h5>
            <p class="text-secondary mb-0 mx-auto" style="max-width: 400px;">
              Academic departments and courses are currently being updated. Please check back soon.
            </p>
          </div>
        </div>
      </div>

      <!-- Full View: Program List -->
      <div v-else>
        <!-- Department Tabs -->
        <div class="d-flex gap-2 mb-4 overflow-auto pb-2 scrollbar-hide">
          <button 
            class="btn btn-sm rounded-pill px-4 transition-all"
            :class="selectedDept === 'all' ? 'btn-admin-primary shadow-sm' : 'btn-light border'"
            @click="selectedDept = 'all'"
          >
            All Departments
          </button>
          <button 
            v-for="dept in departments" 
            :key="dept.id"
            class="btn btn-sm rounded-pill px-4 transition-all"
            :class="selectedDept == dept.id ? 'btn-admin-primary shadow-sm' : 'btn-light border'"
            @click="selectedDept = dept.id"
          >
            {{ dept.name }}
          </button>
        </div>

        <!-- Selected Department Highlight -->
        <div v-if="activeDeptInfo && selectedDept !== 'all'" class="mb-5">
          <!-- Main Dept Card -->
          <div class="card border-0 shadow-sm rounded-4 mb-4 overflow-hidden">
            <div class="card-body p-4 bg-white">
              <div class="row align-items-center">
                <div class="col-md-8">
                  <div class="d-flex align-items-center gap-2 mb-2">
                    <span class="badge bg-brand text-white rounded-pill px-3 py-1 small">DEPARTMENT PROFILE</span>
                  </div>
                  <h3 class="h4 fw-bold text-dark mb-2">{{ activeDeptInfo.name }}</h3>
                  <p class="text-secondary mb-3">{{ activeDeptInfo.description }}</p>
                  <div class="d-flex flex-wrap gap-4 mt-3">
                    <div v-if="activeDeptInfo.head_of_department" class="d-flex align-items-center gap-2">
                      <div class="bg-light p-2 rounded-circle"><i class="bi bi-person-badge text-brand"></i></div>
                      <div>
                        <small class="text-muted d-block extra-small">Head of Dept</small>
                        <span class="small fw-bold">{{ activeDeptInfo.head_of_department }}</span>
                      </div>
                    </div>
                    <div v-if="activeDeptInfo.email" class="d-flex align-items-center gap-2">
                      <div class="bg-light p-2 rounded-circle"><i class="bi bi-envelope text-brand"></i></div>
                      <div>
                        <small class="text-muted d-block extra-small">Contact Email</small>
                        <span class="small fw-bold">{{ activeDeptInfo.email }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-4 text-md-end mt-3 mt-md-0">
                  <div class="bg-light rounded-4 p-3 d-inline-block text-center border">
                    <h4 class="mb-0 fw-bold text-brand">{{ activeDeptInfo.programs?.length || 0 }}</h4>
                    <small class="text-muted uppercase fw-bold extra-small tracking-wider">Total Programs</small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Vision & Mission Section -->
          <div class="row g-4 mb-4">
            <div class="col-md-6">
              <div class="card h-100 border-0 shadow-sm rounded-4 bg-white p-4">
                <div class="d-flex align-items-center gap-3 mb-3">
                  <div class="icon-box bg-brand-soft p-2 rounded-3">
                    <i class="bi bi-rocket-takeoff text-brand fs-4"></i>
                  </div>
                  <h5 class="fw-bold mb-0">Our Mission</h5>
                </div>
                <p class="text-secondary small mb-0 lh-lg" v-html="activeDeptInfo.mission || 'Our mission is to empower students through cutting-edge education, fostering a culture of innovation and critical thinking in our specialized field.'"></p>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card h-100 border-0 shadow-sm rounded-4 bg-white p-4">
                <div class="d-flex align-items-center gap-3 mb-3">
                  <div class="icon-box bg-brand-soft p-2 rounded-3">
                    <i class="bi bi-eye text-brand fs-4"></i>
                  </div>
                  <h5 class="fw-bold mb-0">Our Vision</h5>
                </div>
                <p class="text-secondary small mb-0 lh-lg" v-html="activeDeptInfo.vision || 'To be a globally recognized center of academic excellence, preparing leaders who can solve complex challenges and contribute to a sustainable future.'"></p>
              </div>
            </div>
          </div>

          <!-- Academic Focus Section -->
          <div class="row g-4 mb-5">
            <div class="col-12">
              <div class="card border-0 shadow-sm rounded-4 bg-white p-4">
                <div class="d-flex align-items-center gap-3 mb-3">
                  <div class="icon-box bg-primary-soft p-2 rounded-3">
                    <i class="bi bi-mortarboard text-primary fs-4"></i>
                  </div>
                  <h5 class="fw-bold mb-0">Academic & Research Focus</h5>
                </div>
                <div class="text-secondary small lh-lg" v-html="activeDeptInfo.academic_focus || 'Our department focuses on integrating theoretical foundations with practical applications, ensuring students are well-versed in the latest industry trends and research methodologies.'"></div>
              </div>
            </div>
          </div>

          <div class="d-flex align-items-center gap-2 mb-4">
            <div class="flex-grow-1 border-top"></div>
            <span class="text-muted small fw-bold text-uppercase px-3 tracking-wider">Available Programs</span>
            <div class="flex-grow-1 border-top"></div>
          </div>
        </div>

        <div v-if="filteredPrograms.length" class="row g-4">
          <div v-for="program in filteredPrograms" :key="program.id" class="col-md-6 col-lg-4">
            <div class="card h-100 border-0 shadow-sm rounded-4 program-card hover-lift transition-all">
              <div class="card-body p-4 d-flex flex-column">
                <div class="d-flex align-items-center justify-content-between mb-3">
                  <span class="badge bg-light text-brand border rounded-pill px-3 py-1 fw-bold text-uppercase tracking-tighter extra-small">
                    {{ formatLevel(program.program_level) }}
                  </span>
                </div>

                <h4 class="h5 fw-bold mb-2 text-dark">{{ program.name }}</h4>
                <p class="small text-muted mb-3 program-description flex-grow-1" v-html="program.description || 'Comprehensive curriculum designed for modern professional standards.'"></p>

                <div class="admission-panel rounded-3 p-3 mb-3">
                  <div class="d-flex align-items-center justify-content-between mb-2">
                    <span class="admission-label text-muted">Admissions</span>
                    <span class="badge rounded-pill px-3 py-1" :class="getAdmissionBadgeClass(program)">
                      {{ getAdmissionLabel(program) }}
                    </span>
                  </div>
                  <div v-if="getAdmissionSession(program)" class="admission-meta text-muted">
                    <div class="d-flex align-items-center gap-2">
                      <i class="bi bi-calendar-range text-brand"></i>
                      <span>{{ formatAdmissionWindow(getAdmissionSession(program)) }}</span>
                    </div>
                    <div class="d-flex align-items-center gap-2 mt-1">
                      <i class="bi bi-flag text-brand"></i>
                      <span>{{ getSessionLabel(getAdmissionSession(program)) }}</span>
                    </div>
                  </div>
                  <div v-else class="admission-meta text-muted">
                    Admissions schedule not announced yet.
                  </div>
                  <div v-if="hasApplyActions" class="d-flex flex-wrap gap-2 mt-3">
                    <a
                      v-if="applyUrl"
                      :href="applyUrl"
                      target="_blank"
                      rel="noopener"
                      class="btn btn-sm btn-success rounded-pill fw-semibold"
                    >
                      Apply Now
                    </a>
                    <a
                      v-if="applyEmail"
                      :href="getMailtoLink(program)"
                      class="btn btn-sm btn-outline-secondary rounded-pill fw-semibold"
                    >
                      Email Admissions
                    </a>
                  </div>
                </div>
                
                <div class="mt-3 pt-3 border-top">
                  <div class="row g-2">
                    <div class="col-6">
                      <div class="d-flex align-items-center gap-2 text-secondary small bg-light px-2 py-2 rounded-3">
                        <i class="bi bi-clock text-brand"></i> 
                        <div class="lh-1">
                          <small class="d-block text-muted extra-small">Duration</small>
                          <span class="fw-bold">{{ program.duration_years || 'N/A' }} Years</span>
                        </div>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="d-flex align-items-center gap-2 text-secondary small bg-light px-2 py-2 rounded-3">
                        <i class="bi bi-calendar3 text-brand"></i>
                        <div class="lh-1">
                          <small class="d-block text-muted extra-small">System</small>
                          <span class="fw-bold text-capitalize">{{ program.academic_system || 'Semester' }}</span>
                        </div>
                      </div>
                    </div>
                    <div v-if="program.min_credit_hours" class="col-12 mt-2">
                      <div class="d-flex align-items-center gap-2 text-secondary small bg-light px-2 py-2 rounded-3">
                        <i class="bi bi-mortarboard text-brand"></i>
                        <span class="fw-bold">{{ program.min_credit_hours }} Credit Hours Required</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="card-footer bg-transparent border-0 p-4 pt-0 mt-auto">
                <button 
                  class="btn btn-admin-outline w-100 rounded-pill btn-sm fw-bold"
                  @click="selectedProgram = program"
                  data-bs-toggle="modal" 
                  data-bs-target="#curriculumModal"
                >
                  Explore Curriculum
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <!-- Empty State -->
          <div class="card border-0 bg-light rounded-4 border-dashed p-5 text-center shadow-sm w-100">
            <div class="mb-3">
              <i class="bi bi-journal-text display-1 text-muted opacity-25"></i>
            </div>
            <h5 class="text-dark fw-bold">No Programs Found</h5>
            <p class="text-secondary mb-0 mx-auto" style="max-width: 400px;">
              We couldn't find any programs matching your current selection. Please try adjusting your filters.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Curriculum Modal -->
    <div class="modal fade" id="curriculumModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 rounded-4 shadow">
          <div class="modal-header border-0 p-4 pb-0">
            <div>
              <h5 class="modal-title fw-bold text-dark">{{ selectedProgram?.name }}</h5>
              <p class="text-muted small mb-0">{{ formatLevel(selectedProgram?.program_level) }} • {{ selectedProgram?.department_name }}</p>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
            <div v-if="activeProgramCurriculum.length" class="curriculum-timeline">
              <div v-for="sem in activeProgramCurriculum" :key="sem.semester_number" class="mb-4">
                <h6 class="fw-bold text-brand mb-3 border-start border-3 border-brand ps-2">
                  {{ formatSemesterTitle(sem) }}
                </h6>
                <div class="table-responsive rounded-3 border bg-light">
                  <table class="table table-sm table-hover mb-0">
                    <thead class="bg-white">
                      <tr>
                        <th class="ps-3 py-2 text-muted small uppercase">Code</th>
                        <th class="py-2 text-muted small uppercase">Subject Name</th>
                        <th class="text-center py-2 text-muted small uppercase">Credits</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="subject in sem.subjects" :key="subject.code">
                        <td class="ps-3 py-2 fw-medium small">{{ subject.code }}</td>
                        <td class="py-2 small">{{ subject.name }}</td>
                        <td class="text-center py-2 small">{{ subject.credits }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-5">
              <div class="mb-3">
                <i class="bi bi-book text-muted opacity-25" style="font-size: 3rem;"></i>
              </div>
              <h6 class="fw-bold">No Curriculum Found</h6>
              <p class="text-muted small">The detailed course structure for this program is currently being updated.</p>
            </div>
          </div>
          <div class="modal-footer border-0 p-4 pt-0">
            <button type="button" class="btn btn-light rounded-pill px-4" data-bs-dismiss="modal">Close</button>
            <router-link 
              :to="{ name: 'InstitutionPublicProfile', params: { slug: route.params.slug } }" 
              class="btn btn-admin-primary rounded-pill px-4"
              data-bs-dismiss="modal"
            >
              Contact Admissions
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getFileUrl } from '@/utils/constants/config'

const props = defineProps({
  departments: {
    type: Array,
    default: () => []
  },
  isHome: {
    type: Boolean,
    default: false
  },
  admissions: {
    type: Object,
    default: null
  },
  institution: {
    type: Object,
    default: null
  }
})

const router = useRouter()
const route = useRoute()

// State for filtering
const searchQuery = ref('')
const selectedDept = ref('all')
const selectedProgram = ref(null)

// Sync selectedDept with URL query
watch(() => route.query.dept, (newDept) => {
  if (newDept) {
    selectedDept.value = newDept
  } else {
    selectedDept.value = 'all'
  }
}, { immediate: true })

// Flatten programs for the full view
const allPrograms = computed(() => {
  return props.departments.flatMap(dept => 
    (dept.programs || []).map(prog => ({
      ...prog,
      department_name: dept.name,
      department_id: dept.id
    }))
  )
})

// Get info for the currently selected department
const activeDeptInfo = computed(() => {
  if (selectedDept.value === 'all') return null
  return props.departments.find(d => d.id == selectedDept.value) || null
})

// Filtered programs based on search and department
const filteredPrograms = computed(() => {
  return allPrograms.value.filter(prog => {
    // Check if prog and prog.name exist
    if (!prog || !prog.name) return false
    
    const matchesSearch = prog.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                        (prog.department_name && prog.department_name.toLowerCase().includes(searchQuery.value.toLowerCase()))
    
    // Use loose equality for IDs in case one is a string and other is object/number
    const matchesDept = selectedDept.value === 'all' || selectedDept.value == prog.department_id
    
    return matchesSearch && matchesDept
  })
})

// Deduplicated curriculum for the selected program
const activeProgramCurriculum = computed(() => {
  if (!selectedProgram.value?.curriculum) return []
  
  // Deduplicate by semester_number to fix the "repitation" issue
  const uniqueSemesters = []
  const seenNumbers = new Set()
  
  // Sort by semester number to ensure correct order
  const sortedCurriculum = [...selectedProgram.value.curriculum].sort((a, b) => a.semester_number - b.semester_number)
  
  for (const sem of sortedCurriculum) {
    if (!seenNumbers.has(sem.semester_number)) {
      uniqueSemesters.push(sem)
      seenNumbers.add(sem.semester_number)
    }
  }
  
  return uniqueSemesters
})

const formatSemesterTitle = (sem) => {
  if (!sem) return ''
  const num = sem.semester_number
  const name = sem.semester_name || ''
  
  // If name already contains "Semester X", don't repeat it
  if (name.toLowerCase().includes(`semester ${num}`)) {
    return name
  }
  
  return name ? `Semester ${num}: ${name}` : `Semester ${num}`
}

// Handle query params on mount
onMounted(() => {
  if (route.query.dept) {
    selectedDept.value = route.query.dept
  }
})

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

const applyUrl = computed(() => props.admissions?.apply_url || '')
const applyEmail = computed(() => props.admissions?.apply_email || props.institution?.email || '')
const hasApplyActions = computed(() => Boolean(applyUrl.value || applyEmail.value))

const getMailtoLink = (program) => {
  if (!applyEmail.value) return ''
  const subject = `Admission Inquiry - ${program?.name || 'Program'}`
  return `mailto:${applyEmail.value}?subject=${encodeURIComponent(subject)}`
}

const parseDate = (value) => {
  if (!value) return null
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric'
})

const formatDate = (value) => {
  const date = parseDate(value)
  return date ? dateFormatter.format(date) : 'TBA'
}

const buildAdmissionInfo = (program) => {
  const sessions = Array.isArray(program?.admission_sessions) ? program.admission_sessions : []
  if (!sessions.length) {
    return {
      status: 'none',
      label: 'Not Announced',
      badgeClass: 'bg-light text-muted border',
      session: null
    }
  }

  const today = new Date()
  const openSession = sessions.find((session) => session.admissions_open)
  if (openSession) {
    return {
      status: 'open',
      label: 'Admissions Open',
      badgeClass: 'bg-success',
      session: openSession
    }
  }

  const upcomingSessions = sessions
    .map((session) => ({ session, start: parseDate(session.admission_start_date) }))
    .filter(({ start }) => start && start > today)
    .sort((a, b) => a.start - b.start)

  if (upcomingSessions.length) {
    return {
      status: 'upcoming',
      label: 'Admissions Upcoming',
      badgeClass: 'bg-warning text-dark',
      session: upcomingSessions[0].session
    }
  }

  return {
    status: 'closed',
    label: 'Admissions Closed',
    badgeClass: 'bg-secondary',
    session: sessions[0]
  }
}

const admissionInfoByProgram = computed(() => {
  return allPrograms.value.reduce((info, program) => {
    info[program.id] = buildAdmissionInfo(program)
    return info
  }, {})
})

const getAdmissionInfo = (program) => admissionInfoByProgram.value[program.id] || buildAdmissionInfo(program)

const getAdmissionBadgeClass = (program) => getAdmissionInfo(program).badgeClass

const getAdmissionLabel = (program) => getAdmissionInfo(program).label

const getAdmissionSession = (program) => getAdmissionInfo(program).session

const getSessionLabel = (session) => {
  if (!session) return 'Admission Session'
  return session.session_name || session.session_code || 'Admission Session'
}

const formatAdmissionWindow = (session) => {
  if (!session) return 'Dates to be announced'
  const startDate = session.admission_start_date
  const endDate = session.admission_end_date

  if (startDate && endDate) {
    return `${formatDate(startDate)} - ${formatDate(endDate)}`
  }
  if (startDate && !endDate) {
    return `From ${formatDate(startDate)}`
  }
  if (endDate && !startDate) {
    return `Until ${formatDate(endDate)}`
  }
  return 'Dates to be announced'
}
</script>

<style scoped>
/* Styles migrated to custom.csskjkkk */
</style>

