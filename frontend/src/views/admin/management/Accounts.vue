<template>
  <AdminPageTemplate title="Accounts Management" subtitle="Manage financial accounts" icon="bi bi-bank" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Account List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-4">
          <StatCard title="Total Balance" :value="CURRENCY + ' ' + totalBalance.toLocaleString()" icon="bi bi-wallet-fill" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Total Accounts" :value="accounts.length" icon="bi bi-bank" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Active Accounts" :value="activeCount" icon="bi bi-check-circle" bg-color="bg-info-light" icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="searchQuery"
        search-placeholder="Search accounts..."
        :show-status-filter="false"
        search-col-size="col-md-5 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="loadAccounts"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4 col-6">
            <label class="form-label small fw-semibold text-dark">Type</label>
            <select v-model="typeFilter" class="form-select" @change="loadAccounts">
              <option value="">All Types</option>
              <option v-for="opt in ACCOUNT_TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Accounts Grid -->
    <LoadingSpinner v-if="loading" theme="admin" />
    <div v-else-if="filteredAccounts.length === 0" class="text-center py-5">
      <i class="bi bi-bank display-1 text-muted"></i>
      <h5 class="text-muted mt-3">No Accounts Found</h5>
      <button @click="openCreateModal()" class="btn btn-admin-primary mt-3"><i class="bi bi-plus-circle me-2"></i>Add Account</button>
    </div>
    <div v-else class="row g-4">
      <div v-for="account in filteredAccounts" :key="account.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center">
                <div class="avatar-circle avatar-account me-3"><i class="bi bi-bank"></i></div>
                <div>
                  <h6 class="mb-0 fw-semibold">{{ account.name }}</h6>
                  <small class="text-muted text-capitalize">{{ account.account_type }}</small>
                </div>
              </div>
              <span :class="['badge', getActiveBadgeClass(account.is_active)]">{{ getActiveStatusText(account.is_active) }}</span>
            </div>
            <div class="mb-2"><small class="text-muted">Account Number</small><div class="fw-medium">{{ account.account_number || 'N/A' }}</div></div>
            <div class="mb-3"><small class="text-muted">Bank</small><div class="fw-medium">{{ account.bank_name || 'N/A' }}</div></div>
            <div class="border-top pt-3">
              <small class="text-muted">Balance</small>
              <h4 class="mb-0 text-success fw-bold">{{ CURRENCY }} {{ parseFloat(account.balance || 0).toLocaleString() }}</h4>
            </div>
          </div>
          <div class="card-footer bg-transparent border-top-0">
            <div class="d-flex gap-2">
              <button @click="openEditModal(account)" class="btn btn-sm btn-outline-warning flex-grow-1"><i class="bi bi-pencil me-1"></i>Edit</button>
              <button @click="confirmDelete(account)" class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>

  <!-- Modals using reusable components -->
  <EntityFormModal
    v-model="showModal"
    :title="editMode ? 'Edit Account' : 'Add Account'"
    icon="bi bi-bank"
    :loading="submitting"
    :confirm-text="editMode ? 'Update Account' : 'Add Account'"
    @confirm="handleSubmit()"
    @close="closeModal"
  >
    <form @submit.prevent="handleSubmit()">
      <div class="mb-3"><label class="form-label">Account Name <span class="text-danger">*</span></label><input v-model="form.name" type="text" class="form-control" required></div>
      <div class="row">
        <div class="col-md-6 mb-3"><label class="form-label">Account Type <span class="text-danger">*</span></label><select v-model="form.account_type" class="form-select" required><option v-for="opt in ACCOUNT_TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option></select></div>
        <div class="col-md-6 mb-3"><label class="form-label">Account Number</label><input v-model="form.account_number" type="text" class="form-control"></div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-3"><label class="form-label">Bank Name</label><input v-model="form.bank_name" type="text" class="form-control"></div>
        <div class="col-md-6 mb-3"><label class="form-label">Balance</label><input v-model.number="form.balance" type="number" class="form-control"></div>
      </div>
      <div class="mb-3"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="2"></textarea></div>
    </form>
  </EntityFormModal>

  <ConfirmDialog
    v-model="showDeleteModal"
    type="danger"
    theme="admin"
    title="Confirm Delete"
    :message="`Are you sure you want to delete this account? '${selectedItem?.name}' - This action cannot be undone.`"
    :loading="deleting"
    confirm-text="Delete"
    @confirm="handleDelete"
  />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { smartSearch } from '@/utils'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, SearchFilter, AlertMessage, EntityFormModal, ConfirmDialog, LoadingSpinner } from '@/components/shared/common'
import { useCrudModal, useAsyncState } from '@/composables/shared'
import { accountService } from '@/services/admin/managementService'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { getActiveBadgeClass, getActiveStatusText } from '@/utils/badgeHelpers'
import { ACCOUNT_TYPE_OPTIONS } from '@/utils/constants/options'
import { CURRENCY } from '@/utils/constants/config'
import { generateBreadcrumbs } from '@/utils/navigation'

const breadcrumbs = generateBreadcrumbs('admin', 'Accounts')

const { data: rawAccounts, loading, execute: fetchAccounts } = useAsyncState({ initialLoading: true })
const accounts = computed(() => Array.isArray(rawAccounts.value) ? rawAccounts.value : [])

const loadAccounts = async () => {
  await fetchAccounts(async () => {
    const response = await accountService.getAll()
    return response.data?.results || response.data || []
  })
}

const {
  alert,
  showModal,
  showDeleteModal,
  editMode,
  submitting,
  deleting,
  form,
  selectedItem,
  openCreateModal,
  openEditModal,
  closeModal,
  handleSubmit,
  confirmDelete,
  handleDelete
} = useCrudModal({
  entityName: 'Account',
  defaultForm: { name: '', account_type: 'bank', account_number: '', bank_name: '', balance: 0, description: '' },
  createFn: accountService.create,
  updateFn: accountService.update,
  deleteFn: accountService.delete,
  onSuccess: loadAccounts
})

const actions = [{ label: 'Add Account', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => openCreateModal() }]

const searchQuery = ref('')
const typeFilter = ref('')

const totalBalance = computed(() => accounts.value.filter(a => a.is_active).reduce((sum, a) => sum + parseFloat(a.balance || 0), 0))
const activeCount = computed(() => accounts.value.filter(a => a.is_active).length)

const filteredAccounts = computed(() => {
  let list = accounts.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase().trim()
    const searchTerms = q.split(/\s+/).filter(t => t.length > 0)
    
    list = list.filter(a => {
      return searchTerms.every(term => {
        return (a.name || '').toLowerCase().includes(term) || 
               (a.account_number || '').toLowerCase().includes(term) || 
               (a.bank_name || '').toLowerCase().includes(term)
      })
    })
  }
  if (typeFilter.value) list = list.filter(a => a.account_type === typeFilter.value)
  return list.sort((a, b) => a.name.localeCompare(b.name))
})

const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
}

let searchTimeout
watch(searchQuery, () => {
  // Local filtering only - removed API call to avoid performance issues
})

onMounted(loadAccounts)
</script>


