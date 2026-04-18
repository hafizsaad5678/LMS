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
        preset="admin-list"
        :show-status-filter="false"
        :loading="loading"
        @refresh="handleRefresh"
        @reset="resetFilters"
      >
        <template #filters>
          <SelectInput
            v-model="filters.statusType"
            label="Status"
            placeholder="All Status"
            :options="FEE_STATUS_OPTIONS"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
          <SelectInput
            v-model="filters.semester"
            label="Semester"
            placeholder="All Semesters"
            :options="SEMESTER_NUMBER_OPTIONS"
            col-class="col-md-3 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
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
import { StatCard, DataTable, SearchFilter, SelectInput, AlertMessage } from '@/components/shared/common'
import { useEntityList, useAlert, useListStats } from '@/composables/shared'
import { feeService } from '@/services/admin/managementService'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getStatusBadgeClass } from '@/utils/badgeHelpers'
import { CURRENCY } from '@/utils/constants/config'
import { FEE_STATUS_OPTIONS, SEMESTER_NUMBER_OPTIONS } from '@/utils/constants/options'
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

const { loading, data, filteredData, filters, loadData, resetFilters, refresh } = useEntityList({
  searchFields: ['student_name', 'student_enrollment', 'semester_name'],
  defaultFilters: { statusType: '', semester: '' },
  filterSchema: [
    {
      key: 'statusType',
      itemValue: 'status'
    },
    {
      key: 'semester',
      predicate: (fee, selectedSemester) => {
        const selected = String(selectedSemester || '').trim()
        const semesterName = String(fee.semester_name || fee.semester || '').trim()
        if (!selected) return true
        if (semesterName === selected) return true
        return semesterName.toLowerCase().endsWith(` ${selected}`)
      }
    }
  ]
})

const formatDate = (date) => formatDateUtil(date)
const getStatusBadge = (status) => getStatusBadgeClass(status)

const listStats = useListStats(data)

const totalCollected = computed(() => data.value
  .filter((fee) => fee.status === 'paid')
  .reduce((sum, fee) => sum + parseFloat(fee.paid_amount || 0), 0))

const totalPending = computed(() => data.value
  .filter((fee) => fee.status === 'pending')
  .reduce((sum, fee) => sum + parseFloat(fee.amount || 0), 0))

const overdueCount = listStats.count((fee) => fee.status === 'overdue')

const handleRefresh = () => refresh(fetchFees)

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


