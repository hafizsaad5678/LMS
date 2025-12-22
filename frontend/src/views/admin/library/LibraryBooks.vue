<template>
  <AdminPageTemplate title="Library Books" subtitle="Manage book inventory" icon="bi bi-book" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Book List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-4">
          <StatCard title="Total Books" :value="books.length" icon="bi bi-book" bg-color="bg-admin-light" icon-color="text-admin" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Available" :value="availableCount" icon="bi bi-book-fill" bg-color="bg-success-light" icon-color="text-success" />
        </div>
        <div class="col-6 col-xl-4">
          <StatCard title="Total Copies" :value="totalCopies" icon="bi bi-stack" bg-color="bg-info-light" icon-color="text-info" />
        </div>
      </div>
    </template>

    <!-- Filters Section -->
    <template #filters>
      <SearchFilter
        v-model="searchQuery"
        search-placeholder="Search books by title, author, ISBN..."
        :show-status-filter="false"
        search-col-size="col-md-5 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="loadBooks"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4 col-6">
            <label class="form-label small fw-semibold text-dark">Category</label>
            <select v-model="categoryFilter" class="form-select" @change="loadBooks">
              <option value="">All Categories</option>
              <option value="science">Science</option>
              <option value="technology">Technology</option>
              <option value="arts">Arts</option>
              <option value="literature">Literature</option>
              <option value="history">History</option>
            </select>
          </div>
        </template>
      </SearchFilter>
    </template>

    <!-- Main Content -->
    <DataTable :columns="tableColumns" :data="filteredBooks" :loading="loading" loading-text="Loading books..." empty-icon="bi bi-book" empty-title="No books found" empty-subtitle="Add your first book to get started">
      <template #cell-title="{ row }">
        <div class="d-flex align-items-center">
          <div class="avatar-circle avatar-book me-2"><i class="bi bi-book"></i></div>
          <div>
            <div class="fw-semibold text-dark">{{ row.title }}</div>
            <small class="text-muted">{{ row.publisher }}</small>
          </div>
        </div>
      </template>

      <template #cell-category="{ value }">
        <span class="badge bg-info">{{ value }}</span>
      </template>

      <template #cell-isbn="{ value }">
        <code>{{ value || '-' }}</code>
      </template>

      <template #cell-copies="{ row }">
        {{ row.copies_available || 0 }} / {{ row.copies_total || 0 }}
      </template>

      <template #cell-status="{ row }">
        <span :class="['badge', row.copies_available > 0 ? 'bg-success' : 'bg-danger']">
          {{ row.copies_available > 0 ? 'Available' : 'Unavailable' }}
        </span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons :item="row" :show-view="false" @edit="editBook(row)" @delete="deleteBook(row)" />
      </template>
    </DataTable>

    <!-- Add/Edit Book Modal -->
    <div v-if="showModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">{{ editingBook ? 'Edit Book' : 'Add Book' }}</h5><button type="button" class="btn-close" @click="closeModal"></button></div>
          <div class="modal-body">
            <form @submit.prevent="saveBook">
              <div class="row">
                <div class="col-md-8 mb-3"><label class="form-label">Title <span class="text-danger">*</span></label><input v-model="bookForm.title" type="text" class="form-control" required></div>
                <div class="col-md-4 mb-3"><label class="form-label">ISBN</label><input v-model="bookForm.isbn" type="text" class="form-control"></div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Author <span class="text-danger">*</span></label><input v-model="bookForm.author" type="text" class="form-control" required></div>
                <div class="col-md-6 mb-3"><label class="form-label">Publisher</label><input v-model="bookForm.publisher" type="text" class="form-control"></div>
              </div>
              <div class="row">
                <div class="col-md-4 mb-3"><label class="form-label">Category</label><select v-model="bookForm.category" class="form-select"><option value="science">Science</option><option value="technology">Technology</option><option value="arts">Arts</option><option value="literature">Literature</option><option value="history">History</option></select></div>
                <div class="col-md-4 mb-3"><label class="form-label">Total Copies</label><input v-model.number="bookForm.copies_total" type="number" class="form-control"></div>
                <div class="col-md-4 mb-3"><label class="form-label">Available</label><input v-model.number="bookForm.copies_available" type="number" class="form-control"></div>
              </div>
              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary">{{ editingBook ? 'Update' : 'Add' }} Book</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AdminPageTemplate from '@/components/navbar/AdminPageTemplate.vue'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage } from '@/components/common'
import { libraryBookService } from '@/services/managementService'

const breadcrumbs = [{ name: 'Dashboard', href: '/admin-dashboard' }, { name: 'Library', href: '/admin-dashboard/library/books' }, { name: 'Books' }]
const actions = [{ label: 'Add Book', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: () => showModal.value = true }]

const tableColumns = [
  { key: 'title', label: 'Book' },
  { key: 'author', label: 'Author', hideOnMobile: true },
  { key: 'category', label: 'Category', hideOnMobile: true },
  { key: 'isbn', label: 'ISBN', hideOnMobile: true },
  { key: 'copies', label: 'Copies' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const alert = ref({ show: false, type: 'success', title: '', message: '' })
const loading = ref(false)
const books = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')
const showModal = ref(false)
const editingBook = ref(null)
const bookForm = ref({ title: '', author: '', isbn: '', publisher: '', category: 'science', copies_total: 1, copies_available: 1 })

const availableCount = computed(() => books.value.filter(b => b.copies_available > 0).length)
const totalCopies = computed(() => books.value.reduce((sum, b) => sum + (b.copies_total || 0), 0))

const filteredBooks = computed(() => {
  let list = books.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(b => b.title?.toLowerCase().includes(q) || b.author?.toLowerCase().includes(q) || b.isbn?.toLowerCase().includes(q))
  }
  if (categoryFilter.value) list = list.filter(b => b.category === categoryFilter.value)
  return list.sort((a, b) => a.title.localeCompare(b.title))
})

const loadBooks = async () => {
  loading.value = true
  try {
    const response = await libraryBookService.getAll()
    books.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading books:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to load books' }
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
}

const editBook = (book) => {
  editingBook.value = book
  bookForm.value = { title: book.title, author: book.author, isbn: book.isbn, publisher: book.publisher, category: book.category, copies_total: book.copies_total, copies_available: book.copies_available }
  showModal.value = true
}

const deleteBook = async (book) => {
  if (confirm(`Delete book "${book.title}"?`)) {
    try {
      await libraryBookService.delete(book.id)
      books.value = books.value.filter(b => b.id !== book.id)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Book deleted' }
    } catch (error) {
      console.error('Error deleting book:', error)
      alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to delete book' }
    }
  }
}

const saveBook = async () => {
  try {
    if (editingBook.value) {
      await libraryBookService.update(editingBook.value.id, bookForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Book updated' }
    } else {
      await libraryBookService.create(bookForm.value)
      alert.value = { show: true, type: 'success', title: 'Success', message: 'Book added' }
    }
    closeModal()
    loadBooks()
  } catch (error) {
    console.error('Error saving book:', error)
    alert.value = { show: true, type: 'danger', title: 'Error', message: 'Failed to save book' }
  }
}

const closeModal = () => {
  showModal.value = false
  editingBook.value = null
  bookForm.value = { title: '', author: '', isbn: '', publisher: '', category: 'science', copies_total: 1, copies_available: 1 }
}

let searchTimeout
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadBooks, 300)
})

onMounted(loadBooks)
</script>


