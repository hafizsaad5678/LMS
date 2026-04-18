<template>
  <AdminPageTemplate title="Library Overview" subtitle="Library status and quick actions" icon="bi bi-book" :breadcrumbs="breadcrumbs">
    
    <!-- Stats -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div
          class="card border-0 shadow-sm h-100 cursor-pointer hover-card"
          role="button"
          @click="router.push({ name: ADMIN_ROUTES.LIBRARY_BOOKS.name })"
        >
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-admin-light text-admin rounded-circle me-3"><i class="bi bi-book"></i></div>
            <div><h3 class="mb-0 fw-bold">{{ stats.totalBooks }}</h3><small class="text-muted">Total Books</small></div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div
          class="card border-0 shadow-sm h-100"
        >
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-success-light text-success rounded-circle me-3"><i class="bi bi-check-circle"></i></div>
            <div><h3 class="mb-0 fw-bold">{{ stats.availableBooks }}</h3><small class="text-muted">Available</small></div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div
          class="card border-0 shadow-sm h-100"
        >
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-warning-light text-warning rounded-circle me-3"><i class="bi bi-arrow-left-right"></i></div>
            <div><h3 class="mb-0 fw-bold">{{ stats.activeBorrowings }}</h3><small class="text-muted">Active Borrowings</small></div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div
          class="card border-0 shadow-sm h-100"
        >
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-danger-light text-danger rounded-circle me-3"><i class="bi bi-exclamation-circle"></i></div>
            <div><h3 class="mb-0 fw-bold">{{ stats.overdueBorrowings }}</h3><small class="text-muted">Overdue</small></div>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm mb-4" :class="stats.overdueBorrowings > 0 ? 'border-start border-4 border-danger' : 'border-start border-4 border-success'">
      <div class="card-body d-flex flex-wrap justify-content-between align-items-center gap-3">
        <div>
          <h5 class="mb-1 fw-semibold">
            <i :class="['bi me-2', stats.overdueBorrowings > 0 ? 'bi-exclamation-triangle text-danger' : 'bi-check-circle text-success']"></i>
            {{ stats.overdueBorrowings > 0 ? 'Action Required' : 'All Good' }}
          </h5>
          <p class="text-muted mb-0" v-if="stats.overdueBorrowings > 0">
            {{ stats.overdueBorrowings }} overdue borrowing(s) need follow-up.
          </p>
          <p class="text-muted mb-0" v-else>
            No overdue borrowings right now.
          </p>
        </div>
        <button class="btn btn-admin-primary" @click="router.push({ name: ADMIN_ROUTES.LIBRARY_BORROWING.name })">
          <i class="bi bi-arrow-right-circle me-2"></i>Open Borrowings
        </button>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-7">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
            <h6 class="mb-0 fw-semibold"><i class="bi bi-clock-history text-admin me-2"></i>Recent Borrowings</h6>
            <button class="btn btn-sm btn-admin-outline" @click="router.push({ name: ADMIN_ROUTES.LIBRARY_BORROWING.name })">View All</button>
          </div>
          <div class="card-body p-0">
            <div v-if="recentBorrowings.length === 0" class="text-muted p-4">No borrowing activity found.</div>
            <div v-else class="table-responsive">
              <table class="table mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th class="ps-3">Book</th>
                    <th>Borrower</th>
                    <th>Status</th>
                    <th class="text-end pe-3">Due</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in recentBorrowings" :key="item.id">
                    <td class="ps-3 fw-medium">{{ item.book_title || 'Unknown Book' }}</td>
                    <td>{{ getBorrower(item) }}</td>
                    <td>
                      <span :class="['badge', getBorrowingBadge(item)]">{{ getBorrowingStatusLabel(item) }}</span>
                    </td>
                    <td class="text-end pe-3">{{ formatDate(item.due_date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-5">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
            <h6 class="mb-0 fw-semibold"><i class="bi bi-exclamation-diamond text-warning me-2"></i>Low Stock Books</h6>
            <button class="btn btn-sm btn-admin-outline" @click="router.push({ name: ADMIN_ROUTES.LIBRARY_BOOKS.name })">Manage</button>
          </div>
          <div class="card-body">
            <div v-if="lowStockBooks.length === 0" class="text-muted">No low-stock books. Inventory looks healthy.</div>
            <div v-else class="d-flex flex-column gap-3">
              <div v-for="book in lowStockBooks" :key="book.id" class="d-flex justify-content-between align-items-center border rounded p-2">
                <div class="me-2">
                  <div class="fw-semibold text-dark">{{ book.title || 'Untitled' }}</div>
                  <small class="text-muted">{{ book.author || 'Unknown Author' }}</small>
                </div>
                <span class="badge" :class="book.copies_available === 0 ? 'bg-danger' : 'bg-warning text-dark'">
                  {{ book.copies_available || 0 }} / {{ book.copies_total || 0 }} left
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminPageTemplate } from '@/components/shared/panels'
import { libraryBookService, bookBorrowingService } from '@/services/admin/managementService'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { formatDate as formatDateUtil } from '@/utils/formatters'

const router = useRouter()
const breadcrumbs = [{ name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path }, { name: 'Library' }]
const books = ref([])
const borrowings = ref([])
const stats = ref({
  totalBooks: 0,
  availableBooks: 0,
  activeBorrowings: 0,
  overdueBorrowings: 0
})

const isOverdue = (date) => date ? new Date(date) < new Date() : false
const formatDate = (date) => formatDateUtil(date)

const recentBorrowings = computed(() => {
  return [...borrowings.value]
    .sort((a, b) => new Date(b.borrowed_date || 0) - new Date(a.borrowed_date || 0))
    .slice(0, 5)
})

const lowStockBooks = computed(() => {
  return books.value
    .filter((book) => Number(book.copies_available || 0) <= 1)
    .sort((a, b) => Number(a.copies_available || 0) - Number(b.copies_available || 0))
    .slice(0, 5)
})

const getBorrower = (item) => item.student_name || item.teacher_name || 'Unknown'

const getBorrowingStatusLabel = (item) => {
  if (item.status === 'returned') return 'Returned'
  if (isOverdue(item.due_date) && item.status === 'borrowed') return 'Overdue'
  return 'Borrowed'
}

const getBorrowingBadge = (item) => {
  if (item.status === 'returned') return 'bg-success'
  if (isOverdue(item.due_date) && item.status === 'borrowed') return 'bg-danger'
  return 'bg-warning text-dark'
}

const loadStats = async () => {
  try {
    const [booksRes, borrowingsRes] = await Promise.all([
      libraryBookService.getAll(),
      bookBorrowingService.getAll()
    ])
    
    books.value = booksRes.data.results || booksRes.data || []
    borrowings.value = borrowingsRes.data.results || borrowingsRes.data || []
    
    stats.value.totalBooks = books.value.length
    stats.value.availableBooks = books.value.filter((b) => Number(b.copies_available || 0) > 0).length
    stats.value.activeBorrowings = borrowings.value.filter((b) => b.status === 'borrowed').length
    stats.value.overdueBorrowings = borrowings.value.filter((b) => b.status === 'borrowed' && isOverdue(b.due_date)).length
    
  } catch (error) {
    console.error('Error loading library stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>


