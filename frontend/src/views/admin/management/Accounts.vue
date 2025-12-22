<template>
  <AdminPageTemplate title="Accounts Management" subtitle="Manage financial accounts" icon="bi bi-bank" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Account List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-4">
          <StatCard title="Total Balance" :value="'PKR ' + totalBalance.toLocaleString()" icon="bi bi-wallet-fill" bg-color="bg-success-light" icon-color="text-success" />
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
              <option value="bank">Bank Account</option>
              <option value="cash">Cash</option>
              <option value="petty_cash">Petty Cash</option>
              <option value="other">Other</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Accounts Grid -->
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-admin"></div></div>
    <div v-else-if="filteredAccounts.length === 0" class="text-center py-5">
      <i class="bi bi-bank display-1 text-muted"></i>
      <h5 class="text-muted mt-3">No Accounts Found</h5>
      <button @click="showModal = true" class="btn btn-admin-primary mt-3"><i class="bi bi-plus-circle me-2"></i>Add Account</button>
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
              <span :class="['badge', account.is_active ? 'bg-success' : 'bg-secondary']">{{ account.is_active ? 'Active' : 'Inactive' }}</span>
            </div>
            <div class="mb-2"><small class="text-muted">Account Number</small><div class="fw-medium">{{ account.account_number || 'N/A' }}</div></div>
            <div class="mb-3"><small class="text-muted">Bank</small><div class="fw-medium">{{ account.bank_name || 'N/A' }}</div></div>
            <div class="border-top pt-3">
              <small class="text-muted">Balance</small>
              <h4 class="mb-0 text-success fw-bold">PKR {{ parseFloat(account.balance || 0).toLocaleString() }}</h4>
            </div>
          </div>
          <div class="card-footer bg-transparent border-top-0">
            <div class="d-flex gap-2">
              <button @click="editAccount(account)" class="btn btn-sm btn-outline-warning flex-grow-1"><i class="bi bi-pencil me-1"></i>Edit</button>
              <button @click="deleteAccount(account)" class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>

  <!-- Modals teleported to body for proper overlay -->
  <Teleport to="body">
    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">{{ editingAccount ? 'Edit Account' : 'Add Account' }}</h5><button type="button" class="btn-close" @click="closeModal"></button></div>
          <div class="modal-body">
            <form @submit.prevent="saveAccount">
              <div class="mb-3"><label class="form-label">Account Name <span class="text-danger">*</span></label><input v-model="accountForm.name" type="text" class="form-control" required></div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Account Type <span class="text-danger">*</span></label><select v-model="accountForm.account_type" class="form-select" required><option value="bank">Bank Account</option><option value="cash">Cash</option><option value="petty_cash">Petty Cash</option><option value="other">Other</option></select></div>
                <div class="col-md-6 mb-3"><label class="form-label">Account Number</label><input v-model="accountForm.account_number" type="text" class="form-control"></div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Bank Name</label><input v-model="accountForm.bank_name" type="text" class="form-control"></div>
                <div class="col-md-6 mb-3"><label class="form-label">Balance</label><input v-model.number="accountForm.balance" type="number" class="form-control"></div>
              </div>
              <div class="mb-3"><label class="form-label">Description</label><textarea v-model="accountForm.description" class="form-control" rows="2"></textarea></div>
              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary">{{ editingAccount ? 'Update' : 'Add' }} Account</button>
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
            <p class="mb-0">Are you sure you want to delete this account?</p>
            <p class="fw-bold text-danger mt-2 mb-0">"{{ accountToDelete?.name }}"</p>
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
import { StatCard, SearchFilter, AlertMessage } from '@/components/common'
import { accountService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Accounts' }]
const actions = [{ label: 'Add Account', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => showModal.value = true }]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(false)
const accounts = ref([])
const searchQuery = ref('')
const typeFilter = ref('')
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingAccount = ref(null)
const accountToDelete = ref(null)
const accountForm = ref({ name: '', account_type: 'bank', account_number: '', bank_name: '', balance: 0, description: '' })

const totalBalance = computed(() => accounts.value.filter(a => a.is_active).reduce((sum, a) => sum + parseFloat(a.balance || 0), 0))
const activeCount = computed(() => accounts.value.filter(a => a.is_active).length)

const filteredAccounts = computed(() => {
  let list = accounts.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(a => a.name?.toLowerCase().includes(q) || a.account_number?.toLowerCase().includes(q) || a.bank_name?.toLowerCase().includes(q))
  }
  if (typeFilter.value) list = list.filter(a => a.account_type === typeFilter.value)
  return list.sort((a, b) => a.name.localeCompare(b.name))
})

const loadAccounts = async () => {
  loading.value = true
  try {
    const response = await accountService.getAll()
    accounts.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading accounts:', error)
    alert.value = { show: true, type: 'error', title: 'Error', message: 'Failed to load accounts' }
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
}

const editAccount = (account) => {
  editingAccount.value = account
  accountForm.value = { name: account.name, account_type: account.account_type, account_number: account.account_number, bank_name: account.bank_name, balance: account.balance, description: account.description }
  showModal.value = true
}

const deleteAccount = (account) => {
  accountToDelete.value = account
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  accountToDelete.value = null
}

const confirmDelete = async () => {
  if (!accountToDelete.value) return
  try {
    await accountService.delete(accountToDelete.value.id)
    accounts.value = accounts.value.filter(a => a.id !== accountToDelete.value.id)
    alert.value = { show: true, type: 'success', title: 'Success', message: 'Account deleted' }
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting account:', error)
    alert.value = { show: true, type: 'error', title: 'Error', message: 'Failed to delete account' }
    closeDeleteModal()
  }
}

const saveAccount = async () => {
  try {
    if (editingAccount.value) {
      await accountService.update(editingAccount.value.id, accountForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Account updated' }
    } else {
      await accountService.create(accountForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Account added' }
    }
    closeModal()
    loadAccounts()
  } catch (error) {
    console.error('Error saving account:', error)
    const errorMsg = error.response?.data?.detail || 
                     error.response?.data?.message || 
                     JSON.stringify(error.response?.data) || 
                     'Failed to save account. The backend endpoint may not be configured.'
    alert.value = { show: true, type: 'error', title: 'Error', message: errorMsg }
  }
}

const closeModal = () => {
  showModal.value = false
  editingAccount.value = null
  accountForm.value = { name: '', account_type: 'bank', account_number: '', bank_name: '', balance: 0, description: '' }
}

let searchTimeout
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadAccounts, 300)
})

onMounted(loadAccounts)
</script>


