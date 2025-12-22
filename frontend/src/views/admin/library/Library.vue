<template>
  <AdminPageTemplate title="Library Overview" subtitle="Library status and quick actions" icon="bi bi-book" :breadcrumbs="breadcrumbs">
    
    <!-- Stats -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-admin-light text-admin rounded-circle me-3"><i class="bi bi-book"></i></div>
            <div><h3 class="mb-0 fw-bold">{{ stats.totalBooks }}</h3><small class="text-muted">Total Books</small></div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-success-light text-success rounded-circle me-3"><i class="bi bi-check-circle"></i></div>
            <div><h3 class="mb-0 fw-bold">{{ stats.availableBooks }}</h3><small class="text-muted">Available</small></div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-warning-light text-warning rounded-circle me-3"><i class="bi bi-arrow-left-right"></i></div>
            <div><h3 class="mb-0 fw-bold">{{ stats.activeBorrowings }}</h3><small class="text-muted">Active Borrowings</small></div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-danger-light text-danger rounded-circle me-3"><i class="bi bi-exclamation-circle"></i></div>
            <div><h3 class="mb-0 fw-bold">{{ stats.overdueBorrowings }}</h3><small class="text-muted">Overdue</small></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Navigation -->
    <div class="row g-4 mb-4">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm hover-card" @click="$router.push('/admin-dashboard/library/books')" style="cursor: pointer;">
          <div class="card-body p-4 text-center">
            <div class="display-4 text-admin mb-3"><i class="bi bi-journal-album"></i></div>
            <h4 class="fw-bold">Manage Books</h4>
            <p class="text-muted">Add new books, update inventory, and manage categories.</p>
            <button class="btn btn-admin-outline mt-2">Go to Books</button>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card border-0 shadow-sm hover-card" @click="$router.push('/admin-dashboard/library/borrowings')" style="cursor: pointer;">
          <div class="card-body p-4 text-center">
            <div class="display-4 text-warning mb-3"><i class="bi bi-arrow-left-right"></i></div>
            <h4 class="fw-bold">Manage Circulation</h4>
            <p class="text-muted">Issue books, return books, and view borrowing history.</p>
            <button class="btn btn-outline-warning mt-2">Go to Borrowings</button>
          </div>
        </div>
      </div>
    </div>

  </AdminPageTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { libraryBookService, bookBorrowingService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Library' }]
const stats = ref({
  totalBooks: 0,
  availableBooks: 0,
  activeBorrowings: 0,
  overdueBorrowings: 0
})

const loadStats = async () => {
  try {
    const [booksRes, borrowingsRes] = await Promise.all([
      libraryBookService.getAll(),
      bookBorrowingService.getAll()
    ])
    
    const books = booksRes.data.results || booksRes.data
    const borrowings = borrowingsRes.data.results || borrowingsRes.data
    
    stats.value.totalBooks = books.length
    stats.value.availableBooks = books.filter(b => b.copies_available > 0).length
    stats.value.activeBorrowings = borrowings.filter(b => b.status === 'borrowed').length
    stats.value.overdueBorrowings = borrowings.filter(b => b.status === 'borrowed' && new Date(b.due_date) < new Date()).length
    
  } catch (error) {
    console.error('Error loading library stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>


