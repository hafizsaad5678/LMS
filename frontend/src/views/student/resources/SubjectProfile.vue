<template>
  <StudentPageTemplate :title="subject?.name || 'Subject Profile'" subtitle="Detailed information about this subject"
    icon="bi bi-journal-text" :breadcrumbs="breadcrumbs">
    <!-- Loading State -->
    <LoadingSpinner v-if="loading" text="Loading subject details..." theme="student" class="py-5" />

    <!-- Error State -->
    <AlertMessage v-if="error" type="error" :message="error" title="Error" />

    <div v-else class="row g-4">
      <!-- Subject Info Card -->
      <div class="col-md-8">
        <div class="card border-0 shadow-sm mb-4 border-start-student-thick">
          <div class="card-body">
            <h5 class="card-title text-success mb-3">Subject Information</h5>
            <div class="row g-3">
              <div class="col-md-6">
                <p class="text-muted small mb-1">Subject Name</p>
                <p class="fw-bold">{{ subject.name }}</p>
              </div>
              <div class="col-md-6">
                <p class="text-muted small mb-1">Subject Code</p>
                <p class="fw-bold">{{ subject.code }}</p>
              </div>
              <div class="col-md-6">
                <p class="text-muted small mb-1">Credit Hours</p>
                <p class="fw-bold">{{ subject.credit_hours }} Credits</p>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Department</label>
                <div class="fw-bold">{{ subject.department_name || 'N/A' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Current Semester</label>
                <div class="fw-bold">{{ subject.semester_name || 'N/A' }}</div>
              </div>
              <div class="col-12" v-if="subject.description">
                <p class="text-muted small mb-1">Description</p>
                <p>{{ subject.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Teacher Info (if available) -->
        <div v-if="subject.teacher" class="card border-0 shadow-sm mb-4">
          <StudentSectionHeader title="Instructor" />
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar-circle bg-student-light text-student">
                  {{ getInitials(subject.teacher_name || subject.teacher?.user?.first_name || 'T') }}
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <h5 class="mb-1">{{ subject.teacher_name || subject.teacher?.user?.first_name + ' ' +
                  subject.teacher?.user?.last_name || 'Unknown' }}</h5>
                <p class="text-muted mb-0 small">{{ subject.teacher?.email || 'No contact email' }}</p>
              </div>
              <div>
                <button class="btn btn-student-outline btn-sm">
                  <i class="bi bi-envelope"></i> Contact
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Schedule / Lecture Time (Placeholder or Real Data) -->
        <div class="card border-0 shadow-sm">
          <StudentSectionHeader title="Class Schedule" />
          <div class="card-body">
            <div v-if="normalizedSchedule.length > 0">
              <!-- Iterate over schedule -->
              <div v-for="(slot, index) in normalizedSchedule" :key="index"
                class="d-flex align-items-center mb-3 last-mb-0 border-bottom pb-2">
                <div class="me-3 text-center min-w-80">
                  <span class="badge badge-soft-success text-capitalize d-block mb-1">{{ formatDayLabel(slot.day) }}</span>
                </div>
                <div class="flex-grow-1">
                  <div class="fw-bold fs-5">{{ formatScheduleTime(slot.start_time, false) }} - {{ formatScheduleTime(slot.end_time, true) }}</div>
                  <div class="small text-muted">
                    <i class="bi bi-geo-alt-fill me-1"></i>
                    Room: {{ slot.room || 'TBD' }}
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-3 text-muted">
              <i class="bi bi-calendar-x fs-4 d-block mb-2"></i>
              No schedule information available.
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar Actions -->
      <div class="col-md-4">
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <h6 class="fw-bold mb-3">Quick Actions</h6>
            <div class="d-grid gap-2">
              <button class="btn btn-student-primary" @click="goToMaterials">
                <i class="bi bi-folder me-2"></i> View Materials
              </button>
              <button class="btn btn-student-outline">
                <i class="bi bi-people me-2"></i> Classmates
              </button>
            </div>
          </div>
        </div>

        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h6 class="fw-bold mb-3">Performance</h6>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="text-muted small">Attendance</span>
              <span class="badge"
                :class="subject.attendance_summary >= 75 ? 'badge-soft-success' : 'badge-soft-danger'">
                {{ subject.attendance_summary !== null ? subject.attendance_summary + '%' : 'N/A' }}
              </span>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <span class="text-muted small">Current Grade</span>
              <span class="badge badge-soft-primary">{{ subject.current_grade || 'N/A' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { studentService } from '@/services/shared'
import { StudentPageTemplate } from '@/components/shared/panels'
import { AlertMessage, LoadingSpinner, StudentSectionHeader } from '@/components/shared/common'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const route = useRoute()
const router = useRouter()
const subjectId = route.params.id
const loading = ref(true)
const error = ref(null)
const subject = ref({})

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'My Subjects', href: STUDENT_ROUTES.ENROLLED_SUBJECTS.path },
  { name: 'Subject Profile' }
]

const dayOrder = {
  monday: 1,
  tuesday: 2,
  wednesday: 3,
  thursday: 4,
  friday: 5,
  saturday: 6,
  sunday: 7
}

const toMinutes = (timeValue) => {
  const raw = String(timeValue || '').trim()
  if (!raw) return Number.POSITIVE_INFINITY
  const [h, m] = raw.split(':').map(Number)
  if (!Number.isFinite(h) || !Number.isFinite(m)) return Number.POSITIVE_INFINITY
  return h * 60 + m
}

const normalizedSchedule = computed(() => {
  const slots = Array.isArray(subject.value?.schedule) ? [...subject.value.schedule] : []
  return slots.sort((a, b) => {
    const dayA = dayOrder[String(a?.day || '').toLowerCase()] || 99
    const dayB = dayOrder[String(b?.day || '').toLowerCase()] || 99
    if (dayA !== dayB) return dayA - dayB
    return toMinutes(a?.start_time) - toMinutes(b?.start_time)
  })
})

const formatDayLabel = (dayValue) => {
  const raw = String(dayValue || '').trim().toLowerCase()
  if (!raw) return 'N/A'
  return raw.charAt(0).toUpperCase() + raw.slice(1)
}

const formatScheduleTime = (timeValue, isEnd = false) => {
  const raw = String(timeValue || '').trim()
  if (!raw) return '--:--'

  const [hRaw, mRaw] = raw.split(':')
  let hours = Number(hRaw)
  let minutes = Number(mRaw)
  if (!Number.isFinite(hours) || !Number.isFinite(minutes)) return raw

  // Many backends store period end as xx:59 for inclusive ranges; render as next-hour xx:00.
  if (isEnd && minutes === 59) {
    hours += 1
    minutes = 0
  }

  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}

const loadSubjectDetails = async () => {
  if (!subjectId || subjectId === 'undefined') {
    error.value = 'Invalid Subject ID. Please return to dashboard.'
    loading.value = false
    return
  }

  loading.value = true
  try {
    // If we have studentService.getSubjectDetails
    subject.value = await studentService.getSubjectDetails(subjectId)
  } catch (err) {
    console.error('Error loading subject details:', err)
    error.value = 'Failed to load subject details.'
  } finally {
    loading.value = false
  }
}

import { getInitials } from '@/utils/formatters'

const goToMaterials = () => {
  router.push({ path: STUDENT_ROUTES.COURSE_MATERIAL.path, query: { subject: subjectId } })
}

onMounted(() => {
  if (subjectId) {
    loadSubjectDetails()
  } else {
    error.value = 'Invalid Subject ID'
    loading.value = false
  }
})
</script>

<!-- Styles moved to assets/css/custom.css and components.css -->
