<template>
  <StudentPageTemplate title="Library Catalog" subtitle="Browse and search available books" icon="bi bi-book"
    :breadcrumbs="breadcrumbs">
    <!-- Alert Message -->
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true"
      :auto-close-duration="3000" @close="alert.show = false" />

    <ConfirmDialog v-model="showBorrowDialog" title="Borrow Duration" type="info" theme="student" confirm-text="Confirm Borrow"
      :loading="borrowing" @confirm="confirmBorrowRequest" @cancel="resetBorrowDialog">
      <template #content>
        <p class="confirm-message mb-2">
          How many days do you need this book? (1-{{ borrowPolicy.max_request_days }})
        </p>
        <p class="confirm-message small text-muted mb-3">
          First {{ borrowPolicy.free_days }} days are free. After that Rs. {{ borrowPolicy.fine_per_day }}/day fine applies.
        </p>
        <input v-model.number="requestedDaysInput" type="number" class="form-control" min="1"
          :max="borrowPolicy.max_request_days" />
      </template>
    </ConfirmDialog>

    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 mb-4">
        <div class="col-md-4 col-6">
          <StatCard title="Total Books" :value="stats.total" icon="bi bi-book" bg-color="bg-student-light"
            icon-color="text-success" />
        </div>
        <div class="col-md-4 col-6">
          <StatCard title="Available" :value="stats.available" icon="bi bi-book-fill" bg-color="bg-success-light"
            icon-color="text-success" />
        </div>
        <div class="col-md-4 col-6">
          <StatCard title="My Borrowed" :value="stats.myBorrowed" icon="bi bi-bookmark-fill" bg-color="bg-info-light"
            icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <div class="px-2 pt-1 pb-2">
      <SearchFilter v-model="filters.search" :show-card="false" :show-status-filter="false" :show-refresh="true"
        :show-reset="true" :show-labels="false" search-placeholder="Search by title, author, ISBN..."
        search-col-size="col-md-5" actions-col-size="col-md-3" theme="student" @refresh="loadBooks" @reset="resetFilters">
        <template #filters>
          <div class="col-md-4">
            <SelectInput v-model="filters.category" :options="categoryOptions" placeholder="All Categories"
              :no-margin="true" />
          </div>
        </template>
      </SearchFilter>
    </div>

    <!-- Books Grid -->
    <LoadingSpinner v-if="loading" text="Loading books..." theme="student" class="py-5" />

    <div v-else-if="filteredBooks.length === 0" class="text-center py-5">
      <i class="bi bi-book display-1 text-muted"></i>
      <h4 class="text-muted mt-3">No Books Found</h4>
      <p class="text-muted">Try adjusting your search or filters</p>
    </div>

    <div v-else class="row g-4">
      <div v-for="book in filteredBooks" :key="book.id" class="col-md-6 col-lg-4">
        <div class="book-card card border-0 shadow-sm rounded-4 h-100 overflow-hidden hover-lift"
          :class="{ 'border-top border-danger border-4': book.copies_available === 0 }">
          <StudentStatusCardHeader
            :header-class="book.copies_available > 0 ? 'bg-student-light' : 'bg-danger-light'"
            :icon-class="book.copies_available > 0 ? 'bi bi-book-half fs-4 text-student' : 'bi bi-book-half fs-4 text-danger'"
            :badge-class="book.copies_available > 0 ? 'bg-success text-white px-3 py-2' : 'bg-danger text-white px-3 py-2'"
            :badge-text="book.copies_available > 0 ? 'Available' : 'Out of Stock'"
            title-class="text-dark"
            subtitle-class="text-muted"
          >
            <template #title>{{ book.title }}</template>
            <template #subtitle>
              <i class="bi bi-person me-1"></i>{{ book.author }}
            </template>
          </StudentStatusCardHeader>

          <div class="card-body p-4 d-flex flex-column">
            <div class="book-meta row g-3 mb-4 pb-3 border-bottom">
              <div class="col-6">
                <small class="text-muted d-block text-uppercase letter-spacing-1 text-xxs-65">Category</small>
                <span class="small fw-bold text-dark">{{ book.category || 'General' }}</span>
              </div>
              
            </div>

            <div class="flex-grow-1">
              <div class="d-flex flex-wrap gap-2 mb-3">
                <span class="badge bg-light text-dark border small fw-normal">
                  <i class="bi bi-building me-1 text-info"></i>{{ book.publisher || 'Unknown Publisher' }}
                </span>
                <span v-if="book.isbn" class="badge bg-light text-dark border small fw-normal">
                  ISBN: {{ book.isbn }}
                </span>
              </div>

              <div class="alert py-2 px-3 border-0 rounded-3 mb-0 small d-flex align-items-center"
                :class="book.copies_available > 0 ? 'alert-success' : 'alert-danger'">
                <i :class="book.copies_available > 0 ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'" class="fs-5 me-2"></i>
                <div>
                  <span class="fw-bold">Stock:</span> {{ book.copies_available }} / {{ book.copies_total }} available
                </div>
              </div>
            </div>

            <div class="mt-4">
              <button @click="requestBorrow(book)" class="btn btn-student w-100 rounded-3 py-2 fw-bold shadow-sm"
                :disabled="book.copies_available === 0 || borrowing || isAlreadyBorrowed(book)">
                <i class="bi bi-bookmark-plus me-2"></i>
                {{ getBorrowButtonLabel(book) }}
              </button>
              <p class="small text-muted mt-2 mb-0 text-center">
                Free {{ borrowPolicy.free_days }} days, then Rs. {{ borrowPolicy.fine_per_day }}/day fine
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </StudentPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlert } from '@/composables/shared'
import { StudentPageTemplate } from '@/components/shared/panels'
import { StatCard, AlertMessage, SearchFilter, SelectInput, LoadingSpinner, StudentStatusCardHeader, ConfirmDialog } from '@/components/shared/common'
import studentPanelService from '@/services/student/studentPanelService'
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { smartSearch } from '@/utils'

const breadcrumbs = [
  { name: 'Dashboard', href: STUDENT_ROUTES.DASHBOARD.path },
  { name: 'Library Catalog' }
]

const loading = ref(true)
const borrowing = ref(false)
const books = ref([])
const myBorrowings = ref([])
const borrowPolicy = ref({ free_days: 5, fine_per_day: 10, max_request_days: 30 })
const showBorrowDialog = ref(false)
const selectedBook = ref(null)
const requestedDaysInput = ref(5)
const filters = ref({ search: '', category: '' })

const { alert, showSuccess, showError } = useAlert()

const categoryOptions = computed(() => {
  const cats = [...new Set(books.value.map(b => b.category).filter(Boolean))]
  return cats.sort().map(c => ({ value: c, label: c }))
})

const stats = computed(() => ({
  total: books.value.length,
  available: books.value.filter(b => b.copies_available > 0).length,
  myBorrowed: myBorrowings.value.filter(b => b.status === 'borrowed').length
}))

const filteredBooks = computed(() => {
  let result = books.value

  if (filters.value.search) {
    const searchFields = ['title', 'author', 'isbn', 'category', 'publisher']
    result = result.filter(b => smartSearch(b, filters.value.search, searchFields))
  }

  if (filters.value.category) {
    result = result.filter(b => b.category === filters.value.category)
  }

  return result
})

const isAlreadyBorrowed = (book) => {
  if (!book?.id) return false
  return myBorrowings.value.some(b => b.status === 'borrowed' && String(b.book) === String(book.id))
}

const getBorrowButtonLabel = (book) => {
  if (isAlreadyBorrowed(book)) return 'Already Borrowed'
  if (book.copies_available === 0) return 'Not Available'
  if (borrowing.value) return 'Processing...'
  return 'Request to Borrow'
}

const loadBooks = async () => {
  loading.value = true
  try {
    books.value = await studentPanelService.getLibraryBooks({ _t: new Date().getTime() })
  } catch (error) {
    console.error('Error loading books:', error)
  } finally {
    loading.value = false
  }
}

const loadMyBorrowings = async () => {
  try {
    myBorrowings.value = await studentPanelService.getBorrowedBooks({ _t: new Date().getTime() })
  } catch (error) {
    console.error('Error loading borrowings:', error)
  }
}

const loadBorrowPolicy = async () => {
  try {
    borrowPolicy.value = await studentPanelService.getBorrowPolicy({ _t: new Date().getTime() })
  } catch (error) {
    console.error('Error loading borrow policy:', error)
  }
}

const resetBorrowDialog = () => {
  showBorrowDialog.value = false
  selectedBook.value = null
  requestedDaysInput.value = Number(borrowPolicy.value?.free_days || 5)
}

const requestBorrow = async (book) => {
  if (book.copies_available === 0 || isAlreadyBorrowed(book)) return

  selectedBook.value = book
  requestedDaysInput.value = Number(borrowPolicy.value?.free_days || 5)
  showBorrowDialog.value = true
}

const confirmBorrowRequest = async () => {
  const book = selectedBook.value
  if (!book) {
    resetBorrowDialog()
    return
  }

  const maxDays = Number(borrowPolicy.value?.max_request_days || 30)
  const requestedDays = Number(requestedDaysInput.value)
  if (!Number.isInteger(requestedDays) || requestedDays < 1 || requestedDays > maxDays) {
    showError(`Please enter valid days between 1 and ${maxDays}.`)
    return
  }

  borrowing.value = true
  try {
    await studentPanelService.requestBookBorrow(book.id, requestedDays)

    const freeDays = Number(borrowPolicy.value?.free_days || 5)
    const fine = Number(borrowPolicy.value?.fine_per_day || 10)
    const note = requestedDays > freeDays
      ? ` You requested ${requestedDays} days. After ${freeDays} days, fine will be Rs. ${fine}/day.`
      : ''

    showSuccess(`Book borrowed successfully! Please collect it from the library.${note}`)

    resetBorrowDialog()
    await Promise.all([loadBooks(), loadMyBorrowings()])
  } catch (error) {
    console.error('Error borrowing book:', error)
    const errorMsg = error.response?.data?.error || 'Failed to borrow book. Please try again or contact the library.'

    showError(errorMsg)
  } finally {
    borrowing.value = false
  }
}

const resetFilters = () => {
  filters.value = { search: '', category: '' }
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

onMounted(() => {
  loadBooks()
  loadMyBorrowings()
  loadBorrowPolicy()
})
</script>


