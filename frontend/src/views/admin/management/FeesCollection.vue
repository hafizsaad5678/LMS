<template>
  <AdminPageTemplate title="Fees Collection" subtitle="Manage student fee payments and records" icon="bi bi-cash-coin" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Fee Records">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Collected" :value="CURRENCY + ' ' + totalCollected.toLocaleString()" icon="bi bi-cash-stack" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Pending" :value="CURRENCY + ' ' + totalPending.toLocaleString()" icon="bi bi-hourglass-split" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Overdue" :value="overdueCount" icon="bi bi-exclamation-triangle" bg-color="bg-danger-light" icon-color="text-danger" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Records" :value="data.length" icon="bi bi-people" bg-color="bg-info-light" icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search student..."
        :show-status-filter="false"
        :loading="loading"
        @refresh="() => loadData(fetchFees, false)"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <select v-model="filters.statusType" class="form-select">
              <option value="">All Status</option>
              <option value="paid">Paid</option>
              <option value="pending">Pending</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <select v-model="filters.semester" class="form-select">
              <option value="">All Semesters</option>
              <option value="1">Semester 1</option>
              <option value="2">Semester 2</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredData" :loading="loading" loading-text="Loading fee records..." empty-icon="bi bi-cash-coin" empty-title="No fee records found" empty-subtitle="Fee records will appear here">
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
        <div class="fw-bold text-success">{{ CURRENCY }} {{ parseFloat(row.amount || 0).toLocaleString() }}</div>
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
        <p class="text-muted small mb-0">Total: {{ filteredData.length }} records</p>
        <p class="text-muted small mb-0">Collected: {{ CURRENCY }} {{ totalCollected.toLocaleString() }}</p>
      </div>
    </template>
  </AdminPageTemplate>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert } from '@/composables/shared'
import { feeService } from '@/services/admin/managementService'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getStatusBadgeClass } from '@/utils/badgeHelpers'
import { CURRENCY } from '@/utils/constants/config'
import { generateBreadcrumbs } from '@/utils/navigation'

const breadcrumbs = generateBreadcrumbs('admin', 'Fees Collection')
const actions = [{ label: 'Generate Report', icon: 'bi bi-file-earmark-pdf', variant: 'btn-admin-primary', onClick: () => {} }]

const tableColumns = [
  { key: 'student_name', label: 'Student' },
  { key: 'amount', label: 'Amount' },
  { key: 'due_date', label: 'Due Date', hideOnMobile: true },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const { alert, showSuccess, showError } = useAlert()

const fetchFees = async () => {
  const res = await feeService.getAll()
  return res.data?.results || res.data || []
}

const { loading, data, filteredData, filters, loadData, resetFilters } = useEntityList({
  searchFields: ['student_name', 'student_enrollment', 'semester_name'],
  defaultFilters: { statusType: '', semester: '' },
  customFilter: (list, f) => {
    if (f.statusType) list = list.filter(fee => fee.status === f.statusType)
    if (f.semester) list = list.filter(fee => fee.semester_name === f.semester)
    return list
  }
})

const formatDate = (date) => formatDateUtil(date)
const getStatusBadge = (status) => getStatusBadgeClass(status)

const totalCollected = computed(() => data.value.filter(f => f.status === 'paid').reduce((sum, f) => sum + parseFloat(f.paid_amount || 0), 0))
const totalPending = computed(() => data.value.filter(f => f.status === 'pending').reduce((sum, f) => sum + parseFloat(f.amount || 0), 0))
const overdueCount = computed(() => data.value.filter(f => f.status === 'overdue').length)

const markPaid = async (fee) => {
  try {
    await feeService.markPaid(fee.id)
    fee.status = 'paid'
    fee.paid_amount = fee.amount
    showSuccess(`Payment marked as paid for ${fee.student_name}`)
  } catch (err) {
    showError('Failed to mark fee as paid')
  }
}

onMounted(() => loadData(fetchFees))
</script>


