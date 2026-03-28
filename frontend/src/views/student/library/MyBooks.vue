<template>
  <StudentPageTemplate title="My Borrowed Books" subtitle="View and manage your borrowed books"
    icon="bi bi-bookmark-fill" :breadcrumbs="breadcrumbs">
    <!-- Alert Message -->
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title"
      :auto-close="!alert.showConfirm" :auto-close-duration="3000" :show-confirm-button="alert.showConfirm"
      :confirm-text="alert.confirmText" @close="alert.show = false" @confirm="handleConfirm" />

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 mb-4">
        <div class="col-md-4 col-6">
          <StatCard title="Currently Borrowed" :value="stats.borrowed" icon="bi bi-bookmark-fill"
            bg-color="bg-student-light" icon-color="text-success" />
        </div>
        <div class="col-md-4 col-6">
          <StatCard title="Overdue" :value="stats.overdue" icon="bi bi-exclamation-triangle-fill"
            bg-color="bg-danger-light" icon-color="text-danger" />
        </div>
        <div class="col-md-4 col-6">
          <StatCard title="Total Fines" :value="`Rs. ${stats.totalFines}`" icon="bi bi-cash" bg-color="bg-warning-light"
            icon-color="text-warning" />
        </div>
      </div>
    </template>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" text="Loading your books..." theme="student" class="py-5" />

    <!-- Empty State -->
    <div v-else-if="currentBorrowings.length === 0 && returnedBooks.length === 0" class="text-center py-5">
      <i class="bi bi-bookmark display-1 text-muted"></i>
      <h4 class="text-muted mt-3">No Borrowed Books</h4>
      <p class="text-muted">You haven't borrowed any books yet</p>
      <button @click="router.push(STUDENT_ROUTES.LIBRARY_CATALOG.path)" class="btn btn-student-primary mt-3">
        <i class="bi bi-book me-2"></i>Browse Library
      </button>
    </div>

    <!-- Current Borrowed Books -->
    <div v-else-if="currentBorrowings.length > 0" class="row g-4">
      <div v-for="borrowing in currentBorrowings" :key="borrowing.id" class="col-md-6 col-lg-4">
        <div class="book-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden hover-lift" :class="{ 'border-top border-danger border-4': isOverdue(borrowing) }">
          <!-- Card Header Section -->
          <StudentStatusCardHeader
            :header-class="isOverdue(borrowing) ? 'bg-danger-light' : 'bg-student-light'"
            :icon-class="isOverdue(borrowing) ? 'bi bi-book-half fs-4 text-danger' : 'bi bi-book-half fs-4 text-student'"
            :badge-class="getStatusBadgeClass(borrowing) + ' px-3 py-2'"
            :badge-text="borrowing.status"
            title-class="text-dark"
            subtitle-class="text-muted"
          >
            <template #title>{{ borrowing.book_title }}</template>
            <template #subtitle>
              <i class="bi bi-person me-1"></i>{{ borrowing.book_author }}
            </template>
          </StudentStatusCardHeader>

          <!-- Card Body -->
          <div class="card-body p-4 d-flex flex-column">
            <div class="book-meta row g-3 mb-4 pb-3 border-bottom">
              <div class="col-6">
                <small class="text-muted d-block text-uppercase letter-spacing-1 text-xxs-65">Borrowed</small>
                <span class="small fw-bold text-dark">{{ formatDate(borrowing.borrowed_date) }}</span>
              </div>
              <div class="col-6 text-end">
                <small class="text-muted d-block text-uppercase letter-spacing-1 text-xxs-65">Due Date</small>
                <span class="small fw-bold" :class="getDueDateClass(borrowing)">
                  {{ formatDate(borrowing.due_date) }}
                </span>
              </div>
            </div>

            <div class="flex-grow-1">
              <div class="d-flex flex-wrap gap-2 mb-3">
                <span class="badge bg-light text-dark border small fw-normal">
                  <i class="bi bi-tag-fill me-1 text-student"></i>{{ borrowing.book_category || 'General' }}
                </span>
                <span v-if="borrowing.book_isbn" class="badge bg-light text-dark border small fw-normal">
                   ISBN: {{ borrowing.book_isbn }}
                </span>
              </div>

              <!-- Fine Warning -->
              <div v-if="borrowing.fine_amount > 0" class="alert alert-warning py-2 px-3 border-0 rounded-3 mb-0 small d-flex align-items-center">
                <i class="bi bi-exclamation-triangle-fill fs-5 me-2"></i>
                <div>
                   <span class="fw-bold">Fine Accumulated:</span> Rs. {{ borrowing.fine_amount }}
                </div>
              </div>
              <div v-else-if="isOverdue(borrowing)" class="alert alert-danger py-2 px-3 border-0 rounded-3 mb-0 small">
                <i class="bi bi-clock-fill me-2"></i>Overdue by {{ getDaysOverdue(borrowing) }} days
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="mt-4">
              <button v-if="borrowing.status === 'borrowed'" @click="confirmReturn(borrowing)"
                class="btn btn-student w-100 rounded-3 py-2 fw-bold shadow-sm" :disabled="returning">
                <i class="bi bi-arrow-return-left me-2"></i>Return Book
              </button>
              <div v-else class="text-center py-2 bg-light rounded-3">
                 <small class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i>Returned</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-4 bg-light rounded-4">
      <i class="bi bi-check2-circle fs-2 text-success"></i>
      <h6 class="mt-2 mb-1">No Current Borrowed Books</h6>
      <p class="text-muted small mb-0">All borrowed books are returned. See your history below.</p>
    </div>

    <!-- History Section -->
    <div v-if="returnedBooks.length > 0" class="mt-5">
      <h5 class="mb-3">
        <i class="bi bi-clock-history me-2 text-success"></i>
        Borrowing History
      </h5>
      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Book</th>
                  <th>Borrowed</th>
                  <th>Returned</th>
                  <th>Fine</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="book in returnedBooks" :key="book.id">
                  <td>
                    <strong>{{ book.book_title }}</strong>
                    <br>
                    <small class="text-muted">{{ book.book_author }}</small>
                  </td>
                  <td>{{ formatDate(book.borrowed_date) }}</td>
                  <td>{{ formatDate(book.returned_date) }}</td>
                  <td>
                    <span v-if="book.fine_amount > 0" class="text-danger">
                      Rs. {{ book.fine_amount }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { useRouter } from 'vue-router'
import { StudentPageTemplate } from '@/components/shared/panels'
import { StatCard, AlertMessage, LoadingSpinner, StudentStatusCardHeader } from '@/components/shared/common'
import studentPanelService from '@/services/student/studentPanelService'
import { formatDate } from '@/utils/formatters'
import { useStudentBase } from '@/composables/student/useStudentBase'
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const router = useRouter()
const { studentId, loadProfile } = useStudentBase()
const loading = ref(true); const returning = ref(false); const borrowings = ref([])
const bookToReturn = ref(null)
const { alert, showSuccess, showError, clearAlert } = useAlert()

const breadcrumbs = [{ name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path }, { name: 'My Borrowed Books' }]

const isOverdue = (b) => b.status === 'borrowed' && new Date(b.due_date) < new Date()
const getDaysOverdue = (b) => Math.floor((new Date() - new Date(b.due_date)) / 86400000)

const handleConfirm = () => { if (bookToReturn.value) returnBook() }

const stats = computed(() => ({
  borrowed: borrowings.value.filter(b => b.status === 'borrowed').length,
  overdue: borrowings.value.filter(b => isOverdue(b)).length,
  totalFines: borrowings.value.reduce((s, b) => s + parseFloat(b.fine_amount || 0), 0).toFixed(2)
}))

const currentBorrowings = computed(() => borrowings.value.filter(b => b.status === 'borrowed'))
const returnedBooks = computed(() => borrowings.value.filter(b => b.status === 'returned'))

const loadBorrowings = async () => {
  loading.value = true
  try {
    borrowings.value = await studentPanelService.getBorrowedBooks({ _t: new Date().getTime() })
  } catch (error) {
    console.error('Error loading borrowings:', error)
  } finally {
    loading.value = false
  }
}

const confirmReturn = (b) => {
  bookToReturn.value = b
  alert.value = { show: true, type: 'warning', message: `Return "${b.book_title}"?`, title: 'Confirm', showConfirm: true, confirmText: 'Yes, Return' }
}

const returnBook = async () => {
  if (!bookToReturn.value) return
  returning.value = true; clearAlert()
  try {
    await studentPanelService.returnBook(bookToReturn.value.id)
    showSuccess('Book returned! Please drop it off.')
    bookToReturn.value = null
    await loadBorrowings()
  } catch (e) {
    showError(e.response?.data?.error || 'Failed to return.')
  } finally { returning.value = false }
}

const getDueDateClass = (b) => {
  if (b.status !== 'borrowed') return 'text-muted'
  if (isOverdue(b)) return 'text-danger fw-bold'
  const diff = Math.floor((new Date(b.due_date) - new Date()) / 86400000)
  return diff <= 2 ? 'text-warning fw-bold' : 'text-success'
}

const getStatusBadgeClass = (b) => {
  if (b.status === 'borrowed' && isOverdue(b)) return 'bg-danger text-white'
  return b.status === 'borrowed' ? 'bg-student text-white' : 'bg-success text-white'
}

onMounted(() => { loadProfile(); loadBorrowings() })
</script>


