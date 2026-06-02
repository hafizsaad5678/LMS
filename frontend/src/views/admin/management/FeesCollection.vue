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
          <div class="avatar-circle avatar-fee me-2">
            <i :class="row.student_name ? 'bi bi-person' : 'bi bi-cash-coin'"></i>
          </div>
          <div>
            <div class="fw-semibold text-dark">{{ row.student_name || row.remarks || 'General Revenue' }}</div>
            <small class="text-muted">{{ row.student_enrollment || 'External Revenue' }}</small>
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
        <span :class="['badge', getStatusBadge(getFeeStatus(row))]">{{ getFeeStatus(row) }}</span>
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

    <!-- Add Revenue Modal -->
    <BaseModal 
      v-model="showAddRevenueModal" 
      title="Add Revenue" 
      confirm-text="Save Revenue"
      cancel-text="Cancel"
      variant="admin"
      :loading="submittingRevenue"
      @confirm="submitRevenue"
    >
      <form @submit.prevent="submitRevenue" class="needs-validation">
        <div class="mb-3">
          <label class="form-label fw-semibold text-dark">Amount <span class="text-danger">*</span></label>
          <div class="input-group">
            <span class="input-group-text bg-light fw-bold">{{ CURRENCY }}</span>
            <input 
              v-model.number="revenueForm.amount" 
              type="number" 
              step="0.01" 
              min="0.01" 
              class="form-control" 
              placeholder="0.00" 
              required
            >
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold text-dark">Revenue Type <span class="text-danger">*</span></label>
          <select v-model="revenueForm.fee_type" class="form-select" required>
            <option value="tuition">Tuition Fee</option>
            <option value="admission">Admission Fee</option>
            <option value="exam">Exam Fee</option>
            <option value="lab">Lab Fee</option>
            <option value="library">Library Fee</option>
            <option value="other">Other / General Revenue</option>
          </select>
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold text-dark">Status <span class="text-danger">*</span></label>
          <select v-model="revenueForm.status" class="form-select" required>
            <option value="paid">Paid (Revenue Received)</option>
            <option value="pending">Pending (Unpaid / Invoice)</option>
            <option value="overdue">Overdue (Unpaid & Late)</option>
          </select>
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold text-dark">Due Date <span class="text-danger">*</span></label>
          <input 
            v-model="revenueForm.due_date" 
            type="date" 
            class="form-control" 
            required
          >
        </div>

        <div v-if="revenueForm.status === 'paid'" class="mb-3">
          <label class="form-label fw-semibold text-dark">Payment Date <span class="text-danger">*</span></label>
          <input 
            v-model="revenueForm.payment_date" 
            type="date" 
            class="form-control" 
            required
          >
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold text-dark">Remarks / Description</label>
          <textarea 
            v-model="revenueForm.remarks" 
            class="form-control" 
            rows="3" 
            placeholder="E.g., Alumni donation, sponsor funding, book sales..."
          ></textarea>
        </div>
      </form>
    </BaseModal>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, SelectInput, AlertMessage, BaseModal } from '@/components/shared/common'
import { useEntityList, useAlert, useListStats } from '@/composables/shared'
import { feeService } from '@/services/admin/managementService'
import { cacheService } from '@/services/shared'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getStatusBadgeClass } from '@/utils/badgeHelpers'
import { CURRENCY } from '@/utils/constants/config'
import { FEE_STATUS_OPTIONS, SEMESTER_NUMBER_OPTIONS } from '@/utils/constants/options'
import { generateBreadcrumbs } from '@/utils/navigation'

const showAddRevenueModal = ref(false)
const submittingRevenue = ref(false)

const defaultRevenueForm = () => ({
  amount: null,
  fee_type: 'other',
  payment_date: new Date().toISOString().split('T')[0],
  due_date: new Date().toISOString().split('T')[0],
  status: 'paid',
  paid_amount: null,
  remarks: ''
})

const revenueForm = ref(defaultRevenueForm())

const openAddRevenueModal = () => {
  revenueForm.value = defaultRevenueForm()
  showAddRevenueModal.value = true
}

const breadcrumbs = generateBreadcrumbs('admin', 'Fees Collection')
const actions = [{ label: 'Add Revenue', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => { openAddRevenueModal() } }]

const tableColumns = [
  { key: 'student_name', label: 'Student' },
  { key: 'amount', label: 'Amount' },
  { key: 'due_date', label: 'Due Date', hideOnMobile: true },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const { alert, showSuccess, showError } = useAlert()

const fetchFees = async () => {
  const res = await feeService.getAll({}, { forceRefresh: true })
  return res.data?.results || res.data || []
}

const { loading, data, filteredData, filters, loadData, resetFilters, refresh } = useEntityList({
  searchFields: ['student_name', 'student_enrollment', 'semester_name'],
  defaultFilters: { statusType: '', semester: '' },
  filterSchema: [
    {
      key: 'statusType',
      itemValue: (fee) => getFeeStatus(fee)
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

const getFeeStatus = (fee) => {
  return fee.status
}

const totalCollected = computed(() => data.value
  .filter((fee) => fee.status === 'paid')
  .reduce((sum, fee) => sum + parseFloat(fee.paid_amount || 0), 0))

const totalPending = computed(() => data.value
  .filter((fee) => getFeeStatus(fee) === 'pending')
  .reduce((sum, fee) => sum + parseFloat(fee.amount || 0), 0))

const overdueCount = computed(() => data.value
  .filter((fee) => getFeeStatus(fee) === 'overdue')
  .length)

const handleRefresh = () => refresh(fetchFees)

const markPaid = async (fee) => {
  try {
    await feeService.markPaid(fee.id)
    fee.status = 'paid'
    fee.paid_amount = fee.amount
    fee.payment_date = new Date().toISOString().split('T')[0]
    
    // Invalidate dashboard cache when marked paid
    cacheService.clearPattern('admin:')
    
    showSuccess(`Payment marked as paid for ${fee.student_name || fee.remarks || 'General Revenue'}`)
  } catch (err) {
    showError('Failed to mark fee as paid')
  }
}

const submitRevenue = async () => {
  if (!revenueForm.value.amount || revenueForm.value.amount <= 0) {
    showError('Please enter a valid amount')
    return
  }
  
  submittingRevenue.value = true
  try {
    if (revenueForm.value.status === 'paid') {
      revenueForm.value.paid_amount = revenueForm.value.amount
      if (!revenueForm.value.payment_date) {
        revenueForm.value.payment_date = new Date().toISOString().split('T')[0]
      }
    } else {
      revenueForm.value.paid_amount = 0
      revenueForm.value.payment_date = null
    }
    
    await feeService.create(revenueForm.value)
    
    // Invalidate dashboard / admin cache to show updated stats immediately
    cacheService.clearPattern('admin:')
    
    showSuccess('Fee record added successfully!')
    showAddRevenueModal.value = false
    handleRefresh()
  } catch (err) {
    const errorMsg = err.response?.data?.detail || 'Failed to add fee record'
    showError(errorMsg)
  } finally {
    submittingRevenue.value = false
  }
}

onMounted(() => loadData(fetchFees))
</script>


