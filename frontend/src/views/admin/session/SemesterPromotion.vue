<template>
  <AdminPageTemplate
    title="Semester Promotion"
    subtitle="Close current semester and move students to the next semester"
    icon="bi bi-arrow-up-circle"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    :show-content-card="false"
  >
    <AlertMessage
      v-if="alert.show"
      :type="alert.type"
      :title="alert.title"
      :message="alert.message"
      :auto-close="true"
      :auto-close-duration="3500"
      @close="alert.show = false"
    />

    <div class="semester-promotion-page">
      <LoadingSpinner v-if="loadingSessions" text="Loading sessions..." theme="admin" />

      <div v-else-if="sessions.length === 0" class="card border-0 shadow-sm">
        <div class="card-body p-4 text-center">
          <i class="bi bi-calendar-x display-4 text-muted"></i>
          <h5 class="mt-3 mb-2">No Active Sessions Found</h5>
          <p class="text-muted mb-0">Activate a session first to run semester promotion.</p>
        </div>
      </div>

      <template v-else>
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body p-4">
            <div class="row g-3 align-items-end">
              <div class="col-md-8">
                <label for="session-picker" class="form-label fw-semibold">Select Session</label>
                <select id="session-picker" v-model="selectedSessionId" class="form-select">
                  <option v-for="session in sessions" :key="session.id" :value="session.id">
                    {{ session.session_name || session.name }} ({{ session.session_code || session.code }})
                  </option>
                </select>
              </div>
              <div class="col-md-4 d-grid">
                <button class="btn btn-outline-secondary" @click="goToSessionProfile" :disabled="!selectedSessionId">
                  <i class="bi bi-person-lines-fill me-2"></i>Open Session Profile
                </button>
              </div>
            </div>
          </div>
        </div>

        <LoadingSpinner v-if="loadingOverview" text="Loading promotion overview..." theme="admin" />

        <template v-else-if="overview">
          <div class="row g-3 mb-4">
            <div class="col-sm-6 col-lg-3">
              <div class="metric-card h-100">
                <div class="metric-label">Active Semester</div>
                <div class="metric-value">{{ overview.active_semester?.name || 'Not set' }}</div>
              </div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="metric-card h-100">
                <div class="metric-label">Next Semester</div>
                <div class="metric-value">{{ overview.next_semester?.name || 'Not available' }}</div>
              </div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="metric-card h-100">
                <div class="metric-label">Eligible Students</div>
                <div class="metric-value">{{ overview.eligible_students_count ?? 0 }}</div>
              </div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="metric-card h-100">
                <div class="metric-label">Session Students</div>
                <div class="metric-value">{{ overview.total_students_in_session ?? 0 }}</div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-info-circle me-2 text-admin"></i>Promotion Summary</h6>
              <span class="badge text-bg-light">{{ overview.session?.name || 'Session' }}</span>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table mb-0 align-middle">
                  <tbody>
                    <tr>
                      <th class="w-25 ps-3">Current Semester</th>
                      <td>{{ overview.active_semester?.name || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <th class="ps-3">Current End Date</th>
                      <td>{{ formatDate(overview.active_semester?.end_date) }}</td>
                    </tr>
                    <tr>
                      <th class="ps-3">Next Semester</th>
                      <td>{{ overview.next_semester?.name || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <th class="ps-3">Promotion Scope</th>
                      <td>All active students in current semester</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow-sm promote-card">
            <div class="card-body p-4">
              <div class="d-flex flex-wrap justify-content-between align-items-start gap-3">
                <div>
                  <h5 class="mb-2">Run Semester Promotion</h5>
                  <p class="text-muted mb-0">
                    This action marks the current semester as completed, activates the next semester,
                    and updates eligible students in one transaction.
                  </p>
                </div>
                <button
                  class="btn btn-admin-primary btn-lg"
                  @click="handlePromote"
                  :disabled="!canPromote"
                >
                  <i class="bi bi-arrow-up-right-circle me-2"></i>
                  {{ isPromoting ? 'Promoting...' : 'Promote Semester' }}
                </button>
              </div>
              <div v-if="!overview.next_semester" class="alert alert-warning mt-3 mb-0">
                No next semester is available. Complete setup before running promotion.
              </div>
              <div v-else-if="(overview.eligible_students_count || 0) === 0" class="alert alert-info mt-3 mb-0">
                No eligible students found in the current semester.
              </div>
            </div>
          </div>

          <div class="card border-0 shadow-sm mt-4">
            <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-semibold"><i class="bi bi-clock-history me-2 text-admin"></i>Promotion History</h6>
              <span class="badge text-bg-light">{{ history.length }} records</span>
            </div>
            <div class="card-body p-0">
              <div v-if="history.length === 0" class="p-4 text-muted">No promotion history found for this session.</div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      <th class="ps-3">Student</th>
                      <th>Enrollment</th>
                      <th>Action</th>
                      <th>From</th>
                      <th>To</th>
                      <th>When</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="entry in history" :key="entry.id">
                      <td class="ps-3">{{ entry.student_name || 'N/A' }}</td>
                      <td>{{ entry.enrollment_number || 'N/A' }}</td>
                      <td>
                        <span class="badge" :class="actionBadgeClass(entry.action)">{{ formatAction(entry.action) }}</span>
                      </td>
                      <td>{{ entry.from_semester || '-' }}</td>
                      <td>{{ entry.to_semester || '-' }}</td>
                      <td>{{ formatDateTime(entry.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </template>
      </template>
    </div>
  </AdminPageTemplate>

  <ConfirmDialog
    v-model="showPromotionConfirm"
    title="Confirm Semester Promotion"
    :message="promotionConfirmMessage"
    type="warning"
    theme="admin"
    confirm-text="Promote Semester"
    cancel-text="Cancel"
    :loading="isPromoting"
    @confirm="confirmPromotion"
  />
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { AlertMessage, ConfirmDialog, LoadingSpinner } from '@/components/shared/common'
import { sessionService } from '@/services/shared'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { formatDate as formatDateUtil } from '@/utils/formatters'

const router = useRouter()
const route = useRoute()

const sessions = ref([])
const selectedSessionId = ref('')
const overview = ref(null)
const loadingSessions = ref(true)
const loadingOverview = ref(false)
const isPromoting = ref(false)
const showPromotionConfirm = ref(false)
const history = ref([])

const alert = reactive({
  show: false,
  type: 'info',
  title: '',
  message: ''
})

const breadcrumbs = computed(() => [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Sessions', href: ADMIN_ROUTES.SESSION_LIST.path },
  { name: 'Semester Promotion' }
])

const actions = computed(() => [
  {
    label: 'Refresh',
    icon: 'bi bi-arrow-repeat',
    variant: 'btn-admin-outline',
    onClick: () => refreshData()
  },
  {
    label: 'Session List',
    icon: 'bi bi-list-ul',
    variant: 'btn-admin-outline',
    onClick: () => router.push(ADMIN_ROUTES.SESSION_LIST.path)
  }
])

const canPromote = computed(() => {
  if (!overview.value || isPromoting.value) return false
  if (!overview.value.next_semester) return false
  return (overview.value.eligible_students_count || 0) > 0
})

const promotionConfirmMessage = computed(() => {
  const activeName = overview.value?.active_semester?.name || 'current semester'
  const nextName = overview.value?.next_semester?.name || 'next semester'
  const studentCount = overview.value?.eligible_students_count || 0
  const studentLabel = studentCount === 1 ? 'student' : 'students'

  return `Move ${studentCount} ${studentLabel} from ${activeName} to ${nextName}? This will mark ${activeName} as completed and activate ${nextName}.`
})

const showAlert = (type, title, message) => {
  alert.type = type
  alert.title = title
  alert.message = message
  alert.show = true
}

const normalizeListResponse = (payload) => {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.results)) return payload.results
  return []
}

const formatDate = (value) => {
  if (!value) return 'N/A'
  return formatDateUtil(value)
}

const formatDateTime = (value) => {
  if (!value) return 'N/A'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'N/A'
  return date.toLocaleString()
}

const formatAction = (action) => {
  if (!action) return 'Unknown'
  return action.charAt(0).toUpperCase() + action.slice(1)
}

const actionBadgeClass = (action) => {
  if (action === 'promoted') return 'text-bg-success'
  if (action === 'held') return 'text-bg-warning'
  if (action === 'graduated') return 'text-bg-primary'
  return 'text-bg-secondary'
}

const syncQuerySession = () => {
  if (!selectedSessionId.value) return

  router.replace({
    query: {
      ...route.query,
      session: selectedSessionId.value
    }
  })
}

const loadSessions = async () => {
  loadingSessions.value = true
  try {
    const data = await sessionService.getActiveSessions()
    sessions.value = normalizeListResponse(data)

    const routeSessionId = route.query.session
    const hasRouteSession = sessions.value.some((session) => session.id === routeSessionId)

    if (hasRouteSession) {
      selectedSessionId.value = routeSessionId
    } else {
      selectedSessionId.value = sessions.value[0]?.id || ''
    }
  } catch (error) {
    console.error('Failed to load active sessions:', error)
    showAlert('error', 'Load Failed', 'Unable to fetch active sessions.')
    sessions.value = []
    selectedSessionId.value = ''
  } finally {
    loadingSessions.value = false
  }
}

const loadOverview = async () => {
  if (!selectedSessionId.value) {
    overview.value = null
    return
  }

  loadingOverview.value = true
  try {
    overview.value = await sessionService.getPromotionOverview(selectedSessionId.value)
  } catch (error) {
    console.error('Failed to load promotion overview:', error)
    const backendError = error?.response?.data?.error
    showAlert('error', 'Overview Failed', backendError || 'Could not load semester promotion overview.')
    overview.value = null
  } finally {
    loadingOverview.value = false
  }
}

const loadHistory = async () => {
  if (!selectedSessionId.value) {
    history.value = []
    return
  }

  try {
    const data = await sessionService.getPromotionHistory(selectedSessionId.value)
    history.value = normalizeListResponse(data)
  } catch (error) {
    console.error('Failed to load promotion history:', error)
    history.value = []
  }
}

const goToSessionProfile = () => {
  if (!selectedSessionId.value) return
  router.push({ name: 'SessionProfile', params: { id: selectedSessionId.value } })
}

const handlePromote = async () => {
  if (!canPromote.value || !selectedSessionId.value) return

  showPromotionConfirm.value = true
}

const confirmPromotion = async () => {
  if (!canPromote.value || !selectedSessionId.value) return

  isPromoting.value = true
  try {
    const result = await sessionService.promoteSemester(selectedSessionId.value)
    showPromotionConfirm.value = false
    showAlert(
      'success',
      'Promotion Completed',
      `Promoted ${result.promoted_count || 0} students and held ${result.held_count || 0}.`
    )
    await loadOverview()
    await loadHistory()
  } catch (error) {
    console.error('Promotion failed:', error)
    const backendError = error?.response?.data?.error
    showAlert('error', 'Promotion Failed', backendError || 'Semester promotion failed.')
  } finally {
    isPromoting.value = false
  }
}

const refreshData = async () => {
  await loadOverview()
  await loadHistory()
}

watch(selectedSessionId, async () => {
  syncQuerySession()
  await refreshData()
})

onMounted(async () => {
  await loadSessions()
  await refreshData()
})
</script>
