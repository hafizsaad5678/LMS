<template>
  <AdminPageTemplate title="Book Borrowings" subtitle="Manage book circulation" icon="bi bi-arrow-left-right" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Borrowing Records">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <ConfirmDialog
      v-model="showReturnDialog"
      title="Return Book"
      :message="itemToReturn ? `Mark book '${itemToReturn.book_title}' as returned?` : 'Return this book?'"
      type="info"
      theme="admin"
      confirm-text="Return"
      @confirm="confirmReturnBook"
    />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-4">
          <StatCard title="Active Borrowings" :value="activeCount" icon="bi bi-arrow-left-right" bg-color="bg-warning-light" icon-color="text-warning" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Returned" :value="returnedCount" icon="bi bi-check-circle" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Overdue" :value="overdueCount" icon="bi bi-exclamation-circle" bg-color="bg-danger-light" icon-color="text-danger" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="filters.search"
        search-placeholder="Search by book, student, or teacher..."
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
            placeholder="All Statuses"
            :options="BORROWING_STATUS_OPTIONS"
            col-class="col-md-4 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredData" :loading="loading" loading-text="Loading borrowings..." empty-icon="bi bi-arrow-left-right" empty-title="No borrowings found" empty-subtitle="Borrowing records will appear here">
      <template #cell-book_title="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-book me-2"><i class="bi bi-book"></i></div>
          <div class="fw-semibold text-dark">{{ row.book_title || 'Unknown' }}</div>
        </div>
      </template>

      <template #cell-borrower="{ row }">
        {{ row.student_name || row.teacher_name || 'Unknown' }}
      </template>

      <template #cell-borrowed_date="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-due_date="{ row, value }">
        <span :class="isOverdue(value) && row.status === 'borrowed' ? 'text-danger fw-bold' : ''">{{ formatDate(value) }}</span>
      </template>

      <template #cell-status="{ row }">
        <span :class="['badge', row.status === 'returned' ? 'bg-success' : isOverdue(row.due_date) ? 'bg-danger' : 'bg-warning']">{{ formatStatus(row) }}</span>
      </template>

      <template #cell-actions="{ row }">
        <button v-if="row.status === 'borrowed'" @click="returnBook(row)" class="btn btn-sm btn-success"><i class="bi bi-check-circle me-1"></i>Return</button>
        <span v-else class="text-muted small">Returned</span>
      </template>
    </DataTable>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, SelectInput, AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { useEntityList, useAlert, useListStats } from '@/composables/shared'
import { bookBorrowingService } from '@/services/admin/managementService'
import { formatDate as formatDateUtil } from '@/utils/formatters'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { BORROWING_STATUS_OPTIONS } from '@/utils/constants/options'

const breadcrumbs = [{ name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path }, { name: 'Library', href: `${ADMIN_ROUTES.LIBRARY.path}/books` }, { name: 'Borrowings' }]
const actions = []

const tableColumns = [
  { key: 'book_title', label: 'Book' },
  { key: 'borrower', label: 'Borrower' },
  { key: 'borrowed_date', label: 'Borrowed', hideOnMobile: true },
  { key: 'due_date', label: 'Due Date' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const { alert, showSuccess, showError } = useAlert()

const isOverdue = (date) => date ? new Date(date) < new Date() : false
const formatDate = (date) => formatDateUtil(date)
const formatStatus = (borrow) => {
  if (borrow.status === 'returned') return 'Returned'
  if (isOverdue(borrow.due_date)) return 'Overdue'
  return 'Borrowed'
}

const fetchBorrowings = async () => {
  const res = await bookBorrowingService.getAll()
  return res.data?.results || res.data || []
}

const { loading, data, filteredData, filters, loadData, resetFilters, refresh } = useEntityList({
  searchFields: ['book_title', 'student_name', 'teacher_name'],
  defaultFilters: { statusType: '' },
  filterSchema: [
    {
      key: 'statusType',
      predicate: (borrow, statusType) => {
        if (statusType === 'overdue') {
          return isOverdue(borrow.due_date) && borrow.status === 'borrowed'
        }
        if (statusType) {
          return borrow.status === statusType
        }
        return true
      }
    }
  ],
  customFilter: (list) => list.sort((a, b) => new Date(b.borrowed_date) - new Date(a.borrowed_date))
})

const listStats = useListStats(data)
const activeCount = listStats.count((borrow) => borrow.status === 'borrowed')
const returnedCount = listStats.count((borrow) => borrow.status === 'returned')
const overdueCount = listStats.count((borrow) => isOverdue(borrow.due_date) && borrow.status === 'borrowed')

const handleRefresh = () => refresh(fetchBorrowings)

const showReturnDialog = ref(false)
const itemToReturn = ref(null)

const returnBook = (borrow) => {
  itemToReturn.value = borrow
  showReturnDialog.value = true
}

const confirmReturnBook = async () => {
  try {
    await bookBorrowingService.returnBook(itemToReturn.value.id)
    itemToReturn.value.status = 'returned'
    itemToReturn.value.returned_date = new Date().toISOString().split('T')[0]
    showSuccess('Book returned successfully')
  } catch (err) {
    showError('Failed to return book')
  } finally {
    showReturnDialog.value = false
    itemToReturn.value = null
  }
}

onMounted(() => loadData(fetchBorrowings))
</script>
