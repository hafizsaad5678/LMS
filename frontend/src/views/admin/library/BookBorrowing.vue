<template>
  <AdminPageTemplate title="Book Borrowings" subtitle="Manage book circulation" icon="bi bi-arrow-left-right" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Borrowing Records">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
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
        v-model="searchQuery"
        search-placeholder="Search by book, student, or teacher..."
        :show-status-filter="false"
        search-col-size="col-md-5 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="loadBorrowings"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4 col-6">
            <label class="form-label small fw-semibold text-dark">Status</label>
            <select v-model="statusFilter" class="form-select">
              <option value="">All Statuses</option>
              <option value="borrowed">Borrowed</option>
              <option value="returned">Returned</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredBorrowings" :loading="loading" loading-text="Loading borrowings..." empty-icon="bi bi-arrow-left-right" empty-title="No borrowings found" empty-subtitle="Borrowing records will appear here">
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
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, AlertMessage } from '@/components/common'
import { bookBorrowingService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Library', href: '/admin-dashboard/library/books' }, { name: 'Borrowings' }]
const actions = []

const tableColumns = [
  { key: 'book_title', label: 'Book' },
  { key: 'borrower', label: 'Borrower' },
  { key: 'borrowed_date', label: 'Borrowed', hideOnMobile: true },
  { key: 'due_date', label: 'Due Date' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(false)
const borrowings = ref([])
const searchQuery = ref('')
const statusFilter = ref('')

const activeCount = computed(() => borrowings.value.filter(b => b.status === 'borrowed').length)
const returnedCount = computed(() => borrowings.value.filter(b => b.status === 'returned').length)
const overdueCount = computed(() => borrowings.value.filter(b => isOverdue(b.due_date) && b.status === 'borrowed').length)

const filteredBorrowings = computed(() => {
  let list = borrowings.value
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(b => 
      (b.book_title && b.book_title.toLowerCase().includes(q)) || 
      (b.student_name && b.student_name.toLowerCase().includes(q)) || 
      (b.teacher_name && b.teacher_name.toLowerCase().includes(q))
    )
  }
  
  if (statusFilter.value) {
    if (statusFilter.value === 'overdue') {
      list = list.filter(b => isOverdue(b.due_date) && b.status === 'borrowed')
    } else {
      list = list.filter(b => b.status === statusFilter.value)
    }
  }
  
  return list.sort((a, b) => new Date(b.borrowed_date) - new Date(a.borrowed_date))
})

const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const isOverdue = (date) => {
  if (!date) return false
  return new Date(date) < new Date()
}

const formatStatus = (borrow) => {
  if (borrow.status === 'returned') return 'Returned'
  if (isOverdue(borrow.due_date)) return 'Overdue'
  return 'Borrowed'
}

const loadBorrowings = async () => {
  loading.value = true
  try {
    const response = await bookBorrowingService.getAll()
    borrowings.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading borrowings:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to load borrowing history' }
  } finally {
    loading.value = false
  }
}

const returnBook = async (borrow) => {
  if (!confirm(`Mark book "${borrow.book_title}" as returned?`)) return
  
  try {
    await bookBorrowingService.returnBook(borrow.id)
    borrow.status = 'returned'
    borrow.returned_date = new Date().toISOString().split('T')[0] // Optimistic update
    alert.value = { show: true, type: 'success', title: 'Success', message: 'Book returned successfully' }
    // Refresh to ensure exact state?
    // loadBorrowings() 
  } catch (error) {
    console.error('Error returning book:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to return book' }
  }
}

onMounted(loadBorrowings)
</script>

<style scoped>
.avatar-circle { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.875rem; flex-shrink: 0; }
.avatar-book { background: linear-gradient(135deg, #6f42c1 0%, #5a32a3 100%); color: white; }
</style>
