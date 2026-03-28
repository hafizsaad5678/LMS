<template>
  <AdminPageTemplate title="Expenses Management" subtitle="Track and manage institutional expenses" icon="bi bi-cash-stack" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Expense Records">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Expenses" :value="CURRENCY + ' ' + totalExpenses.toLocaleString()" icon="bi bi-cash-stack" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Approved" :value="approvedCount" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Pending" :value="pendingCount" icon="bi bi-hourglass-split" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
        <div class="col-6 col-xl-3">
          <StatCard title="Total Records" :value="expenses.length" icon="bi bi-receipt" bg-color="bg-info-light" icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="searchQuery"
        search-placeholder="Search expenses..."
        :show-status-filter="false"
        :loading="loadingExpenses"
        @refresh="loadExpenses"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <select v-model="categoryFilter" class="form-select" @change="loadExpenses">
              <option value="">All Categories</option>
              <option v-for="opt in EXPENSE_CATEGORY_OPTIONS" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <select v-model="statusFilter" class="form-select" @change="loadExpenses">
              <option value="">All Status</option>
              <option value="approved">Approved</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredExpenses" :loading="loadingExpenses" loading-text="Loading expenses..." empty-icon="bi bi-cash-stack" empty-title="No expenses found" empty-subtitle="Add your first expense to get started">
      <template #cell-title="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-expense me-2"><i class="bi bi-cash-stack"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.title }}</div>
            <small class="text-muted d-none d-md-block">{{ truncate(row.description, 30) }}</small>
          </div>
        </div>
      </template>

      <template #cell-category="{ value }">
        <span class="badge bg-info text-capitalize">{{ value }}</span>
      </template>

      <template #cell-amount="{ value }">
        <span class="fw-bold text-danger">{{ CURRENCY }} {{ parseFloat(value || 0).toLocaleString() }}</span>
      </template>

      <template #cell-expense_date="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-is_approved="{ row }">
        <span :class="['badge', getStatusBadge(row.is_approved)]">{{ row.is_approved ? 'Approved' : 'Pending' }}</span>
      </template>

      <template #cell-actions="{ row }">
        <div class="d-flex gap-1 justify-content-center">
          <button v-if="!row.is_approved" @click="approveExpense(row)" class="btn btn-sm btn-success" title="Approve"><i class="bi bi-check"></i></button>
          <button @click="openEditModal(row)" class="btn btn-sm btn-outline-primary" title="Edit"><i class="bi bi-pencil"></i></button>
          <button @click="confirmDelete(row)" class="btn btn-sm btn-outline-danger" title="Delete"><i class="bi bi-trash"></i></button>
        </div>
      </template>
    </DataTable>
  </AdminPageTemplate>

  <!-- Modals using reusable components -->
  <EntityFormModal
    v-model="showModal"
    :title="editMode ? 'Edit Expense' : 'Add Expense'"
    :icon="editMode ? 'bi bi-pencil' : 'bi bi-cash-stack'"
    :loading="submitting"
    :confirm-text="editMode ? 'Update Expense' : 'Add Expense'"
    @confirm="handleSubmit()"
  >
    <form @submit.prevent="handleSubmit()">
      <div class="mb-3"><label class="form-label">Title <span class="text-danger">*</span></label><input v-model="form.title" type="text" class="form-control" required></div>
      <div class="mb-3"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="2"></textarea></div>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label class="form-label">Category <span class="text-danger">*</span></label>
          <select v-model="form.category" class="form-select" required>
            <option v-for="opt in EXPENSE_CATEGORY_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div class="col-md-6 mb-3"><label class="form-label">Amount <span class="text-danger">*</span></label><input v-model.number="form.amount" type="number" class="form-control" required></div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-3"><BaseInput v-model="form.expense_date" label="Date" type="date" :required="true" /></div>
        <div class="col-md-6 mb-3"><label class="form-label">Vendor</label><input v-model="form.vendor" type="text" class="form-control"></div>
      </div>
    </form>
  </EntityFormModal>

  <ConfirmDialog
    v-model="showDeleteModal"
    type="danger"
    theme="admin"
    title="Confirm Delete"
    :message="`Are you sure you want to delete this expense? '${selectedItem?.title}' - This action cannot be undone.`"
    :loading="deleting"
    confirm-text="Delete"
    @confirm="handleDelete"
  />
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { smartSearch } from '@/utils'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, AlertMessage, BaseInput, EntityFormModal, ConfirmDialog } from '@/components/shared/common'
import { useCrudModal, useAsyncState } from '@/composables/shared'
import { expenseService } from '@/services/admin/managementService'
import { formatDate as formatDateUtil, truncateText } from '@/utils/formatters'
import { getErrorMessage, getSuccessMessage } from '@/utils/errorMap'
import { EXPENSE_CATEGORY_OPTIONS } from '@/utils/constants/options'
import { getStatusBadgeClass } from '@/utils/badgeHelpers'
import { CURRENCY } from '@/utils/constants/config'
import { generateBreadcrumbs } from '@/utils/navigation'

const breadcrumbs = generateBreadcrumbs('admin', 'Expenses')
const actions = [{ label: 'Add Expense', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => openCreateModal() }]

const tableColumns = [
  { key: 'title', label: 'Title' },
  { key: 'category', label: 'Category' },
  { key: 'amount', label: 'Amount' },
  { key: 'expense_date', label: 'Date', hideOnMobile: true },
  { key: 'vendor', label: 'Vendor', hideOnMobile: true, default: '-' },
  { key: 'is_approved', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

// Data fetching
const { data: expensesData, loading: loadingExpenses, execute: loadExpensesApi } = useAsyncState({ initialLoading: true })
const loadExpenses = () => loadExpensesApi(async () => {
    const response = await expenseService.getAll()
    return response.data.results || response.data
})

const expenses = computed(() => expensesData.value || [])

// Modal and CRUD logic
const {
  alert, showAlert, 
  showModal, showDeleteModal, editMode, submitting, deleting,
  form, selectedItem,
  openCreateModal, openEditModal, closeModal,
  handleSubmit, confirmDelete, handleDelete
} = useCrudModal({
  entityName: 'Expense',
  defaultForm: { title: '', description: '', category: 'utilities', amount: 0, expense_date: '', vendor: '' },
  createFn: (data) => expenseService.create(data),
  updateFn: (id, data) => expenseService.update(id, data),
  deleteFn: (id) => expenseService.delete(id),
  onSuccess: loadExpenses
})

// UI Refs
import { ref } from 'vue'
const searchQuery = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')

const totalExpenses = computed(() => expenses.value.filter(e => e.is_approved).reduce((sum, e) => sum + parseFloat(e.amount || 0), 0))
const approvedCount = computed(() => expenses.value.filter(e => e.is_approved).length)
const pendingCount = computed(() => expenses.value.filter(e => !e.is_approved).length)

const filteredExpenses = computed(() => {
  let list = expenses.value
  if (searchQuery.value) {
    list = list.filter(e => smartSearch(e, searchQuery.value, ['title', 'vendor']))
  }
  if (categoryFilter.value) list = list.filter(e => e.category === categoryFilter.value)
  if (statusFilter.value === 'approved') list = list.filter(e => e.is_approved)
  else if (statusFilter.value === 'pending') list = list.filter(e => !e.is_approved)
  return list.sort((a, b) => new Date(b.expense_date) - new Date(a.expense_date))
})

const formatDate = (date) => formatDateUtil(date)
const truncate = (text, length) => truncateText(text, length)
const getStatusBadge = (isApproved) => getStatusBadgeClass(isApproved ? 'approved' : 'pending')

const resetFilters = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  statusFilter.value = ''
}

const approveExpense = async (expense) => {
  try {
    await expenseService.approve(expense.id)
    expense.is_approved = true
    showAlert('success', getSuccessMessage('expense', 'approve'), 'Success')
  } catch (error) {
    console.error('Error approving expense:', error)
    showAlert('error', getErrorMessage(error, 'expense', 'approve'), 'Error')
  }
}

let searchTimeout
watch(searchQuery, () => {
  // Local filtering only
})

onMounted(loadExpenses)
</script>
