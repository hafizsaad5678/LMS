<template>
  <AdminPageTemplate
    title="Assignment Management"
    subtitle="Whole-college assignment records and reporting"
    icon="bi bi-file-earmark-text"
    :breadcrumbs="breadcrumbs"
    :actions="actions"
    content-title="Assignment List"
  >
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Assignments" :value="stats.total" icon="bi bi-file-earmark-text" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Upcoming" :value="stats.upcoming" icon="bi bi-calendar-week" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Due Today" :value="stats.dueToday" icon="bi bi-calendar-day" bg-color="bg-info-light" icon-color="text-info" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Overdue" :value="stats.overdue" icon="bi bi-exclamation-triangle" bg-color="bg-danger-light" icon-color="text-danger" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search by title or subject..."
        preset="admin-list"
        :show-status-filter="false"
        :loading="loading"
        @refresh="handleRefresh"
        @reset="resetFilters"
      >
        <template #filters>
          <SelectInput
            v-model="filters.program"
            label="Program"
            placeholder="All Programs"
            :options="programOptions"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
          <SelectInput
            v-model="filters.session"
            label="Session"
            placeholder="All Sessions"
            :options="sessionOptions"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
          <SelectInput
            v-model="filters.subject"
            label="Subject"
            placeholder="All Subjects"
            :options="subjectOptions"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
          <SelectInput
            v-model="filters.status"
            label="Status"
            placeholder="All Status"
            :options="assignmentStatusOptions"
            col-class="col-md-2 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
          <div class="col-md-2 col-6">
            <label class="small fw-semibold text-dark mb-1">From Date</label>
            <input v-model="filters.from_date" type="date" class="form-control" />
          </div>
          <div class="col-md-2 col-6">
            <label class="small fw-semibold text-dark mb-1">To Date</label>
            <input v-model="filters.to_date" type="date" class="form-control" />
          </div>
          <SelectInput
            v-model="filters.submission_state"
            label="Submission"
            placeholder="All"
            :options="submissionFilterOptions"
            col-class="col-md-2 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable
      :columns="tableColumns"
      :data="assignments"
      :loading="loading"
      loading-text="Loading assignments..."
      empty-icon="bi bi-file-earmark-text"
      empty-title="No assignments found"
      empty-subtitle="Try adjusting your filters"
    >
      <template #cell-title="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-assignment me-2"><i class="bi bi-file-earmark-text"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.title }}</div>
            <small class="text-muted d-none d-md-block">{{ truncate(row.description, 30) }}</small>
          </div>
        </div>
      </template>

      <template #cell-subject_code="{ row }">
        <span class="badge bg-info">{{ row.subject_code || getSubjectCode(row) || 'N/A' }}</span>
      </template>

      <template #cell-program="{ row }">
        <span class="text-muted">{{ getProgramName(row) }}</span>
      </template>

      <template #cell-session="{ row }">
        <span class="text-muted">{{ getSessionName(row) }}</span>
      </template>

      <template #cell-due_date="{ row }">
        <div :class="getDueDateClass(row.due_date)">
          <i class="bi bi-calendar me-1"></i>{{ formatDate(row.due_date) }}
        </div>
      </template>

      <template #cell-total_marks="{ value }">
        <span class="fw-semibold">{{ value }}</span>
      </template>

      <template #cell-submission_count="{ value }">
        <span class="badge bg-success">{{ value || 0 }}</span>
      </template>

      <template #cell-status="{ row }">
        <span :class="getStatusBadge(row.due_date)">{{ getStatus(row.due_date) }}</span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons
          :item="row"
          :show-view="true"
          :show-edit="canManageAssignments"
          :show-delete="canManageAssignments"
          view-title="View Assignment"
          @edit="editAssignment"
          @delete="deleteAssignment"
          @view="viewAssignment"
        />
      </template>
    </DataTable>

    <template #footer>
      <p class="text-muted small mb-0">Total: {{ assignments.length }} assignments</p>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, SelectInput, ActionButtons } from '@/components/shared/common'
import { useEntityList, useFilterOptions } from '@/composables/shared'
import { assignmentService, subjectService, sessionService, programService, semesterService, cacheService } from '@/services/shared'
import { formatDate as formatDateUtil, truncateText } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { FEATURE_FLAGS } from '@/utils/constants/config'

const router = useRouter()
const canManageAssignments = FEATURE_FLAGS.ADMIN_ASSIGNMENT_MANAGEMENT

const breadcrumbs = [
  { name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path },
  { name: 'Assignments' }
]

const actions = computed(() => {
  const reportActions = [
    { label: 'Export CSV', icon: 'bi bi-filetype-csv', variant: 'btn-admin-outline', onClick: exportCsv },
    { label: 'Export Excel', icon: 'bi bi-file-earmark-spreadsheet', variant: 'btn-admin-outline', onClick: exportExcel }
  ]

  if (canManageAssignments) {
    reportActions.unshift({
      label: 'Add Assignment',
      icon: 'bi bi-plus-circle',
      variant: 'btn-admin-primary',
      onClick: () => router.push(`${ADMIN_ROUTES.ASSIGNMENTS.path}/add`)
    })
  }

  return reportActions
})

const tableColumns = [
  { key: 'title', label: 'Title' },
  { key: 'subject_code', label: 'Subject' },
  { key: 'program', label: 'Program', hideOnMobile: true },
  { key: 'session', label: 'Session', hideOnMobile: true },
  { key: 'due_date', label: 'Due Date' },
  { key: 'total_marks', label: 'Marks', hideOnMobile: true },
  { key: 'submission_count', label: 'Submissions', hideOnMobile: true },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const subjects = ref([])
const programs = ref([])
const sessions = ref([])
const semesters = ref([])
const { createObjectOptions } = useFilterOptions(subjects)
const subjectOptions = createObjectOptions({
  value: (subject) => subject.id,
  label: (subject) => `${subject.code} - ${subject.name}`,
  uniqueBy: (subject) => subject.id
})

const programOptions = computed(() => (programs.value || []).map((program) => ({
  value: String(program.id),
  label: `${program.name}${program.code ? ` (${program.code})` : ''}`
})))

const sessionOptions = computed(() => (sessions.value || []).map((session) => ({
  value: String(session.id),
  label: `${session.session_name} (${session.start_year}-${session.end_year})`
})))

const assignmentStatusOptions = [
  { value: 'upcoming', label: 'Upcoming' },
  { value: 'due_today', label: 'Due Today' },
  { value: 'overdue', label: 'Overdue' }
]

const submissionFilterOptions = [
  { value: 'submitted', label: 'Has Submissions' },
  { value: 'pending', label: 'No Submissions' }
]

const normalizeToArray = (value) => {
  if (Array.isArray(value)) return value
  if (Array.isArray(value?.results)) return value.results
  if (Array.isArray(value?.data)) return value.data
  return []
}

const extractId = (value) => {
  if (value && typeof value === 'object') return String(value.id || value.pk || '')
  if (value == null) return ''
  return String(value)
}

const subjectById = computed(() => {
  const map = new Map()
  for (const subject of subjects.value || []) {
    map.set(String(subject.id), subject)
  }
  return map
})

const semesterById = computed(() => {
  const map = new Map()
  for (const semester of semesters.value || []) {
    map.set(String(semester.id), semester)
  }
  return map
})

const programById = computed(() => {
  const map = new Map()
  for (const program of programs.value || []) {
    map.set(String(program.id), program)
  }
  return map
})

const sessionById = computed(() => {
  const map = new Map()
  for (const session of sessions.value || []) {
    map.set(String(session.id), session)
  }
  return map
})

const toDate = (value) => {
  const date = value ? new Date(value) : null
  return date && !Number.isNaN(date.getTime()) ? date : null
}

const isSameCalendarDay = (left, right) => (
  left.getFullYear() === right.getFullYear() &&
  left.getMonth() === right.getMonth() &&
  left.getDate() === right.getDate()
)

const getAssignmentSubjectId = (assignment) => {
  if (!assignment || typeof assignment !== 'object') return ''
  return extractId(assignment.subject_id || assignment.subject)
}

const getAssignmentSemesterId = (assignment) => {
  if (!assignment || typeof assignment !== 'object') return ''
  const directSemester = extractId(assignment.semester_id || assignment.semester)
  if (directSemester) return directSemester

  const subjectId = getAssignmentSubjectId(assignment)
  const subject = subjectById.value.get(subjectId)
  return extractId(subject?.semester_id || subject?.semester)
}

const getAssignmentProgramId = (assignment) => {
  if (!assignment || typeof assignment !== 'object') return ''
  const directProgram = extractId(assignment.program_id || assignment.program)
  if (directProgram) return directProgram

  const semester = semesterById.value.get(getAssignmentSemesterId(assignment))
  return extractId(semester?.program_id || semester?.program)
}

const getAssignmentSessionId = (assignment) => {
  if (!assignment || typeof assignment !== 'object') return ''
  const directSession = extractId(assignment.session_id || assignment.session)
  if (directSession) return directSession

  const semester = semesterById.value.get(getAssignmentSemesterId(assignment))
  return extractId(semester?.session_id || semester?.session)
}

const getSubjectCode = (assignment) => {
  const subjectId = getAssignmentSubjectId(assignment)
  const subject = subjectById.value.get(subjectId)
  return subject?.code || assignment.subject_code || ''
}

const getProgramName = (assignment) => {
  const programId = getAssignmentProgramId(assignment)
  if (!programId) return 'N/A'
  const program = programById.value.get(programId)
  return program?.name || assignment.program_name || 'N/A'
}

const getSessionName = (assignment) => {
  const sessionId = getAssignmentSessionId(assignment)
  if (!sessionId) return assignment.session_name || 'N/A'
  const session = sessionById.value.get(sessionId)
  if (!session) return assignment.session_name || 'N/A'
  return `${session.session_name} (${session.start_year}-${session.end_year})`
}

// Use composable for list logic
const {
  loading,
  filteredData: assignments,
  filters,
  loadData,
  refresh,
  resetFilters: baseResetFilters
} = useEntityList({
  cacheKey: 'assignments_list',
  searchFields: ['title', 'subject_name', 'subject_code', 'description', 'created_by_name'],
  defaultFilters: {
    subject: '',
    status: '',
    program: '',
    session: '',
    from_date: '',
    to_date: '',
    submission_state: ''
  },
  filterSchema: [
    {
      key: 'subject',
      predicate: (assignment, selectedSubjectId) => getAssignmentSubjectId(assignment) === String(selectedSubjectId || '')
    },
    {
      key: 'program',
      predicate: (assignment, selectedProgramId) => getAssignmentProgramId(assignment) === String(selectedProgramId || '')
    },
    {
      key: 'session',
      predicate: (assignment, selectedSessionId) => getAssignmentSessionId(assignment) === String(selectedSessionId || '')
    },
    {
      key: 'status',
      predicate: (assignment, value) => {
        const dueDate = toDate(assignment.due_date)
        if (!dueDate) return false
        const now = new Date()
        if (value === 'upcoming') return dueDate > now && !isSameCalendarDay(dueDate, now)
        if (value === 'due_today') return isSameCalendarDay(dueDate, now)
        if (value === 'overdue') return dueDate < now && !isSameCalendarDay(dueDate, now)
        return true
      }
    },
    {
      key: 'from_date',
      predicate: (assignment, fromDate) => {
        const dueDate = toDate(assignment.due_date)
        const start = toDate(fromDate)
        if (!dueDate || !start) return true
        start.setHours(0, 0, 0, 0)
        return dueDate >= start
      }
    },
    {
      key: 'to_date',
      predicate: (assignment, toDateValue) => {
        const dueDate = toDate(assignment.due_date)
        const end = toDate(toDateValue)
        if (!dueDate || !end) return true
        end.setHours(23, 59, 59, 999)
        return dueDate <= end
      }
    },
    {
      key: 'submission_state',
      predicate: (assignment, selectedState) => {
        const submissionCount = Number(assignment.submission_count || 0)
        if (selectedState === 'submitted') return submissionCount > 0
        if (selectedState === 'pending') return submissionCount === 0
        return true
      }
    }
  ]
})

// Custom stats
const stats = computed(() => {
  const total = assignments.value.length
  const now = new Date()

  const upcoming = assignments.value.filter((assignment) => {
    const due = toDate(assignment.due_date)
    if (!due) return false
    return due > now && !isSameCalendarDay(due, now)
  }).length

  const dueToday = assignments.value.filter((assignment) => {
    const due = toDate(assignment.due_date)
    if (!due) return false
    return isSameCalendarDay(due, now)
  }).length

  const overdue = assignments.value.filter((assignment) => {
    const due = toDate(assignment.due_date)
    if (!due) return false
    return due < now && !isSameCalendarDay(due, now)
  }).length

  return { total, upcoming, dueToday, overdue }
})

const fetchAssignments = () => assignmentService.getAllAssignments()

const loadAssignments = () => loadData(fetchAssignments)

const loadSubjects = async () => {
  const cachedSubjects = cacheService.get('subjects_list')
  if (cachedSubjects) {
    subjects.value = cachedSubjects
    return
  }

  try {
    const response = await subjectService.getAllSubjects()
    const subjectList = Array.isArray(response) ? response : (response.results || [])
    cacheService.set('subjects_list', subjectList)
    subjects.value = subjectList
  } catch (error) {
    console.error('Error loading subjects:', error)
  }
}

const loadPrograms = async () => {
  const cachedPrograms = cacheService.get('courses_list') || cacheService.get('programs_list')
  if (cachedPrograms) {
    programs.value = cachedPrograms
    return
  }

  try {
    const response = await programService.getAllPrograms()
    const programList = normalizeToArray(response)
    cacheService.set('programs_list', programList)
    programs.value = programList
  } catch (error) {
    console.error('Error loading programs:', error)
  }
}

const loadSessions = async () => {
  const cachedSessions = cacheService.get('sessions_list')
  if (cachedSessions) {
    sessions.value = cachedSessions
    return
  }

  try {
    const response = await sessionService.getSessions()
    const sessionList = normalizeToArray(response)
    cacheService.set('sessions_list', sessionList)
    sessions.value = sessionList
  } catch (error) {
    console.error('Error loading sessions:', error)
  }
}

const loadSemesters = async () => {
  const cachedSemesters = cacheService.get('semesters_list')
  if (cachedSemesters) {
    semesters.value = cachedSemesters
    return
  }

  try {
    const response = await semesterService.getAll()
    const semesterList = normalizeToArray(response)
    cacheService.set('semesters_list', semesterList)
    semesters.value = semesterList
  } catch (error) {
    console.error('Error loading semesters:', error)
  }
}

const resetFilters = () => {
  baseResetFilters()
}

const handleRefresh = () => refresh(fetchAssignments)

const viewAssignment = (assignment) => {
  router.push({ name: ADMIN_ROUTES.ASSIGNMENT_VIEW.name, params: { id: assignment.id } })
}

const editAssignment = (assignment) => {
  if (!canManageAssignments) return
  router.push({ name: ADMIN_ROUTES.ASSIGNMENT_EDIT.name, params: { id: assignment.id } })
}

const deleteAssignment = (assignment) => {
  if (!canManageAssignments) return
  router.push({ name: ADMIN_ROUTES.ASSIGNMENT_DELETE.name, params: { id: assignment.id } })
}

const escapeCsv = (value) => {
  const raw = value == null ? '' : String(value)
  return `"${raw.replace(/"/g, '""')}"`
}

const buildExportRows = (rows) => rows.map((assignment) => ({
  title: assignment.title || '',
  subject: assignment.subject_name || getSubjectCode(assignment) || '',
  program: getProgramName(assignment),
  session: getSessionName(assignment),
  dueDate: formatDate(assignment.due_date),
  status: getStatus(assignment.due_date),
  marks: assignment.total_marks || 0,
  submissions: assignment.submission_count || 0,
  teacher: assignment.created_by_name || 'N/A'
}))

const downloadBlob = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}

const exportCsv = () => {
  const rows = buildExportRows(assignments.value)
  const header = ['Title', 'Subject', 'Program', 'Session', 'Due Date', 'Status', 'Total Marks', 'Submissions', 'Teacher']
  const lines = [header.map(escapeCsv).join(',')]
  for (const row of rows) {
    lines.push([
      row.title,
      row.subject,
      row.program,
      row.session,
      row.dueDate,
      row.status,
      row.marks,
      row.submissions,
      row.teacher
    ].map(escapeCsv).join(','))
  }

  const stamp = new Date().toISOString().slice(0, 10)
  downloadBlob(lines.join('\n'), `assignments-report-${stamp}.csv`, 'text/csv;charset=utf-8;')
}

const escapeHtml = (value) => String(value == null ? '' : value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')

const exportExcel = () => {
  const rows = buildExportRows(assignments.value)
  const header = ['Title', 'Subject', 'Program', 'Session', 'Due Date', 'Status', 'Total Marks', 'Submissions', 'Teacher']
  const tableHeader = `<tr>${header.map((cell) => `<th>${escapeHtml(cell)}</th>`).join('')}</tr>`
  const tableRows = rows.map((row) => `<tr>${[
    row.title,
    row.subject,
    row.program,
    row.session,
    row.dueDate,
    row.status,
    row.marks,
    row.submissions,
    row.teacher
  ].map((cell) => `<td>${escapeHtml(cell)}</td>`).join('')}</tr>`).join('')

  const html = `
    <html>
      <head>
        <meta charset="utf-8" />
      </head>
      <body>
        <table border="1">
          ${tableHeader}
          ${tableRows}
        </table>
      </body>
    </html>
  `

  const stamp = new Date().toISOString().slice(0, 10)
  downloadBlob(html, `assignments-report-${stamp}.xls`, 'application/vnd.ms-excel;charset=utf-8;')
}

// Use shared formatDate utility
const formatDate = (dateString) => formatDateUtil(dateString)

// Use shared truncateText utility
const truncate = (text, length) => truncateText(text, length)

const getDueDateClass = (dueDate) => {
  const due = toDate(dueDate)
  if (!due) return 'text-muted'
  const now = new Date()
  if (due < now && !isSameCalendarDay(due, now)) return 'text-danger fw-semibold'
  if (isSameCalendarDay(due, now)) return 'text-info fw-semibold'
  const diff = due.getTime() - now.getTime()
  if (diff < 3 * 24 * 60 * 60 * 1000) return 'text-warning fw-semibold'
  return 'text-muted'
}

const getStatus = (dueDate) => {
  const due = toDate(dueDate)
  if (!due) return 'Unknown'
  const now = new Date()
  if (isSameCalendarDay(due, now)) return 'Due Today'
  return due < now ? 'Overdue' : 'Upcoming'
}

const getStatusBadge = (dueDate) => {
  const status = getStatus(dueDate)
  if (status === 'Overdue') return 'badge bg-danger'
  if (status === 'Due Today') return 'badge bg-info'
  if (status === 'Upcoming') return 'badge bg-success'
  return 'badge bg-secondary'
}

onMounted(() => {
  loadSubjects()
  loadPrograms()
  loadSessions()
  loadSemesters()
  loadAssignments()
})
</script>



