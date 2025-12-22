<template>
  <AdminPageTemplate title="Expenses Management" subtitle="Track and manage institutional expenses" icon="bi bi-cash-stack" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Expense Records">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-3">
          <StatCard title="Total Expenses" :value="'PKR ' + totalExpenses.toLocaleString()" icon="bi bi-cash-stack" bg-color="bg-admin-light" icon-color="text-admin" />
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
        search-col-size="col-md-4 col-12"
        actions-col-size="col-md-2 col-6"
        :loading="loading"
        @refresh="loadExpenses"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Category</label>
            <select v-model="categoryFilter" class="form-select" @change="loadExpenses">
              <option value="">All Categories</option>
              <option value="utilities">Utilities</option>
              <option value="supplies">Supplies</option>
              <option value="maintenance">Maintenance</option>
              <option value="salaries">Salaries</option>
              <option value="equipment">Equipment</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="col-md-3 col-6">
            <label class="form-label small fw-semibold text-dark">Status</label>
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
    <DataTable :columns="tableColumns" :data="filteredExpenses" :loading="loading" loading-text="Loading expenses..." empty-icon="bi bi-cash-stack" empty-title="No expenses found" empty-subtitle="Add your first expense to get started">
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
        <span class="fw-bold text-danger">PKR {{ parseFloat(value || 0).toLocaleString() }}</span>
      </template>

      <template #cell-expense_date="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-is_approved="{ row }">
        <span :class="['badge', row.is_approved ? 'bg-success' : 'bg-warning']">{{ row.is_approved ? 'Approved' : 'Pending' }}</span>
      </template>

      <template #cell-actions="{ row }">
        <div class="d-flex gap-1 justify-content-center">
          <button v-if="!row.is_approved" @click="approveExpense(row)" class="btn btn-sm btn-success" title="Approve"><i class="bi bi-check"></i></button>
          <button @click="openEditModal(row)" class="btn btn-sm btn-outline-primary" title="Edit"><i class="bi bi-pencil"></i></button>
          <button @click="openDeleteModal(row)" class="btn btn-sm btn-outline-danger" title="Delete"><i class="bi bi-trash"></i></button>
        </div>
      </template>
    </DataTable>
  </AdminPageTemplate>

  <!-- Modals teleported to body for proper overlay -->
  <Teleport to="body">
    <!-- Add Modal -->
    <div v-if="showModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">Add Expense</h5><button type="button" class="btn-close" @click="closeModal"></button></div>
          <div class="modal-body">
            <form @submit.prevent="saveExpense">
              <div class="mb-3"><label class="form-label">Title <span class="text-danger">*</span></label><input v-model="expenseForm.title" type="text" class="form-control" required></div>
              <div class="mb-3"><label class="form-label">Description</label><textarea v-model="expenseForm.description" class="form-control" rows="2"></textarea></div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Category <span class="text-danger">*</span></label><select v-model="expenseForm.category" class="form-select" required><option value="utilities">Utilities</option><option value="supplies">Supplies</option><option value="maintenance">Maintenance</option><option value="equipment">Equipment</option><option value="other">Other</option></select></div>
                <div class="col-md-6 mb-3"><label class="form-label">Amount <span class="text-danger">*</span></label><input v-model.number="expenseForm.amount" type="number" class="form-control" required></div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3"><BaseInput v-model="expenseForm.expense_date" label="Date" type="date" :required="true" /></div>
                <div class="col-md-6 mb-3"><label class="form-label">Vendor</label><input v-model="expenseForm.vendor" type="text" class="form-control"></div>
              </div>
              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary">Add Expense</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">Edit Expense</h5><button type="button" class="btn-close" @click="closeEditModal"></button></div>
          <div class="modal-body">
            <form @submit.prevent="updateExpense">
              <div class="mb-3"><label class="form-label">Title <span class="text-danger">*</span></label><input v-model="editForm.title" type="text" class="form-control" required></div>
              <div class="mb-3"><label class="form-label">Description</label><textarea v-model="editForm.description" class="form-control" rows="2"></textarea></div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Category <span class="text-danger">*</span></label><select v-model="editForm.category" class="form-select" required><option value="utilities">Utilities</option><option value="supplies">Supplies</option><option value="maintenance">Maintenance</option><option value="equipment">Equipment</option><option value="other">Other</option></select></div>
                <div class="col-md-6 mb-3"><label class="form-label">Amount <span class="text-danger">*</span></label><input v-model.number="editForm.amount" type="number" class="form-control" required></div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3"><BaseInput v-model="editForm.expense_date" label="Date" type="date" :required="true" /></div>
                <div class="col-md-6 mb-3"><label class="form-label">Vendor</label><input v-model="editForm.vendor" type="text" class="form-control"></div>
              </div>
              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeEditModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary">Update Expense</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
      <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title"><i class="bi bi-exclamation-triangle me-2"></i>Confirm Delete</h5>
            <button type="button" class="btn-close btn-close-white" @click="closeDeleteModal"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">Are you sure you want to delete this expense?</p>
            <p class="fw-bold text-danger mt-2 mb-0">"{{ expenseToDelete?.title }}"</p>
            <p class="text-muted small mt-2 mb-0">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="confirmDelete" class="btn btn-danger">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, AlertMessage, BaseInput } from '@/components/common'
import { expenseService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Expenses' }]
const actions = [{ label: 'Add Expense', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => showModal.value = true }]

const tableColumns = [
  { key: 'title', label: 'Title' },
  { key: 'category', label: 'Category' },
  { key: 'amount', label: 'Amount' },
  { key: 'expense_date', label: 'Date', hideOnMobile: true },
  { key: 'vendor', label: 'Vendor', hideOnMobile: true, default: '-' },
  { key: 'is_approved', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(false)
const expenses = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const showModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const expenseForm = ref({ title: '', description: '', category: 'utilities', amount: 0, expense_date: '', vendor: '' })
const editForm = ref({ id: '', title: '', description: '', category: 'utilities', amount: 0, expense_date: '', vendor: '' })
const expenseToDelete = ref(null)

const totalExpenses = computed(() => expenses.value.filter(e => e.is_approved).reduce((sum, e) => sum + parseFloat(e.amount || 0), 0))
const approvedCount = computed(() => expenses.value.filter(e => e.is_approved).length)
const pendingCount = computed(() => expenses.value.filter(e => !e.is_approved).length)

const filteredExpenses = computed(() => {
  let list = expenses.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(e => e.title?.toLowerCase().includes(q) || e.vendor?.toLowerCase().includes(q))
  }
  if (categoryFilter.value) list = list.filter(e => e.category === categoryFilter.value)
  if (statusFilter.value === 'approved') list = list.filter(e => e.is_approved)
  else if (statusFilter.value === 'pending') list = list.filter(e => !e.is_approved)
  return list.sort((a, b) => new Date(b.expense_date) - new Date(a.expense_date))
})

const formatDate = (date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
const truncate = (text, length) => text && text.length > length ? text.substring(0, length) + '...' : text || ''

const loadExpenses = async () => {
  loading.value = true
  try {
    const response = await expenseService.getAll()
    expenses.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading expenses:', error)
    alert.value = { show: true, type: 'error', title: 'Error', message: 'Failed to load expenses' }
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  statusFilter.value = ''
}

const approveExpense = async (expense) => {
  try {
    await expenseService.approve(expense.id)
    expense.is_approved = true
    alert.value = { show: true, type: 'success', title: 'Success', message: 'Expense approved' }
  } catch (error) {
    console.error('Error approving expense:', error)
    alert.value = { show: true, type: 'error', title: 'Error', message: 'Failed to approve expense' }
  }
}

const deleteExpense = async (expense) => {
  if (confirm(`Delete expense "${expense.title}"?`)) {
    try {
      await expenseService.delete(expense.id)
      expenses.value = expenses.value.filter(e => e.id !== expense.id)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Expense deleted' }
    } catch (error) {
      console.error('Error deleting expense:', error)
      alert.value = { show: true, type: 'error', title: 'Error', message: 'Failed to delete expense' }
    }
  }
}

const openEditModal = (expense) => {
  editForm.value = { ...expense }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editForm.value = { id: '', title: '', description: '', category: 'utilities', amount: 0, expense_date: '', vendor: '' }
}

const updateExpense = async () => {
  try {
    await expenseService.update(editForm.value.id, editForm.value)
    const index = expenses.value.findIndex(e => e.id === editForm.value.id)
    if (index !== -1) expenses.value[index] = { ...editForm.value }
    alert.value = { show: true, type: 'success', title: 'Success', message: 'Expense updated' }
    closeEditModal()
  } catch (error) {
    console.error('Error updating expense:', error)
    alert.value = { show: true, type: 'error', title: 'Error', message: 'Failed to update expense' }
  }
}

const openDeleteModal = (expense) => {
  expenseToDelete.value = expense
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  expenseToDelete.value = null
}

const confirmDelete = async () => {
  if (!expenseToDelete.value) return
  try {
    await expenseService.delete(expenseToDelete.value.id)
    expenses.value = expenses.value.filter(e => e.id !== expenseToDelete.value.id)
    alert.value = { show: true, type: 'success', title: 'Success', message: 'Expense deleted' }
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting expense:', error)
    alert.value = { show: true, type: 'error', title: 'Error', message: 'Failed to delete expense' }
    closeDeleteModal()
  }
}

const saveExpense = async () => {
  try {
    await expenseService.create(expenseForm.value)
    alert.value = { show: true, type: 'success', title: 'Success', message: 'Expense added' }
    closeModal()
    loadExpenses()
  } catch (error) {
    console.error('Error saving expense:', error)
    alert.value = { show: true, type: 'error', title: 'Error', message: 'Failed to save expense' }
  }
}

const closeModal = () => {
  showModal.value = false
  expenseForm.value = { title: '', description: '', category: 'utilities', amount: 0, expense_date: '', vendor: '' }
}

let searchTimeout
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadExpenses, 300)
})

onMounted(loadExpenses)
</script>

