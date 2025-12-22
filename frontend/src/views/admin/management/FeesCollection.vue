<template>
  <AdminPageTemplate title="Fees Collection" subtitle="Manage student fee payments and records" icon="bi bi-cash-coin" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Fee Records">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Collected" :value="'PKR ' + totalCollected.toLocaleString()" icon="bi bi-cash-stack" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Pending" :value="'PKR ' + totalPending.toLocaleString()" icon="bi bi-hourglass-split" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Overdue" :value="overdueCount" icon="bi bi-exclamation-triangle" bg-color="bg-danger-light" icon-color="text-danger" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Records" :value="fees.length" icon="bi bi-people" bg-color="bg-info-light" icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="searchQuery"
        search-placeholder="Search student..."
        :show-status-filter="false"
        search-col-size="col-md-4 col-12"
        actions-col-size="col-md-2 col-6"
        :loading="loading"
        @refresh="loadFees"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Status</label>
            <select v-model="statusFilter" class="form-select" @change="loadFees">
              <option value="">All Status</option>
              <option value="paid">Paid</option>
              <option value="pending">Pending</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Semester</label>
            <select v-model="semesterFilter" class="form-select" @change="loadFees">
              <option value="">All Semesters</option>
              <option value="1">Semester 1</option>
              <option value="2">Semester 2</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredFees" :loading="loading" loading-text="Loading fee records..." empty-icon="bi bi-cash-coin" empty-title="No fee records found" empty-subtitle="Fee records will appear here">
      <template #cell-student_name="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-fee me-2"><i class="bi bi-person"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.student_name || 'N/A' }}</div>
            <small class="text-muted">{{ row.student_enrollment || '' }}</small>
          </div>
        </div>
      </template>

      <template #cell-amount="{ row }">
        <div class="fw-bold text-success">PKR {{ parseFloat(row.amount || 0).toLocaleString() }}</div>
        <small class="text-muted">{{ row.semester_name || row.fee_type }}</small>
      </template>

      <template #cell-due_date="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-status="{ row }">
        <span :class="['badge', getStatusBadge(row.status)]">{{ row.status }}</span>
      </template>

      <template #cell-actions="{ row }">
        <button v-if="row.status !== 'paid'" @click="markPaid(row)" class="btn btn-sm btn-success"><i class="bi bi-check-circle me-1"></i>Mark Paid</button>
        <button v-else class="btn btn-sm btn-outline-secondary" disabled><i class="bi bi-check-circle-fill me-1"></i>Paid</button>
      </template>
    </DataTable>

    <template #footer>
      <div class="d-flex justify-content-between flex-wrap gap-2">
        <p class="text-muted small mb-0">Total: {{ filteredFees.length }} records</p>
        <p class="text-muted small mb-0">Collected: PKR {{ totalCollected.toLocaleString() }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, AlertMessage } from '@/components/common'
import { feeService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Fees Collection' }]
const actions = [{ label: 'Generate Report', icon: 'bi bi-file-earmark-pdf', variant: 'btn-admin-primary', onClick: () => {} }]

const tableColumns = [
  { key: 'student_name', label: 'Student' },
  { key: 'amount', label: 'Amount' },
  { key: 'due_date', label: 'Due Date', hideOnMobile: true },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const fees = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const semesterFilter = ref('')
const loading = ref(false)

const totalCollected = computed(() => fees.value.filter(f => f.status === 'paid').reduce((sum, f) => sum + parseFloat(f.paid_amount || 0), 0))
const totalPending = computed(() => fees.value.filter(f => f.status === 'pending').reduce((sum, f) => sum + parseFloat(f.amount || 0), 0))
const overdueCount = computed(() => fees.value.filter(f => f.status === 'overdue').length)

const filteredFees = computed(() => {
  let list = fees.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(f => f.student_name?.toLowerCase().includes(q) || f.student_enrollment?.toLowerCase().includes(q))
  }
  if (statusFilter.value) list = list.filter(f => f.status === statusFilter.value)
  if (semesterFilter.value) list = list.filter(f => f.semester_name?.includes(semesterFilter.value))
  return list
})

const formatDate = (date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
const getStatusBadge = (status) => status === 'paid' ? 'bg-success' : status === 'pending' ? 'bg-warning' : 'bg-danger'

const loadFees = async () => {
  loading.value = true
  try {
    const response = await feeService.getAll()
    fees.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading fees:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to load fees' }
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  semesterFilter.value = ''
}

const markPaid = async (fee) => {
  try {
    await feeService.markPaid(fee.id)
    fee.status = 'paid'
    fee.paid_amount = fee.amount
    alert.value = { show: true, type: 'success', title: 'Success', message: `Payment marked as paid for ${fee.student_name}` }
  } catch (error) {
    console.error('Error marking fee as paid:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to mark fee as paid' }
  }
}

let searchTimeout
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadFees, 300)
})

onMounted(loadFees)
</script>


