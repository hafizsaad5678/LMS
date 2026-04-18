<template>
  <AdminPageTemplate title="Library Books" subtitle="Manage book inventory" icon="bi bi-book" :breadcrumbs="breadcrumbs" :actions="actions" content-title="Book List">
    <AlertMessage v-if="alert.show" :type="alert.type" :message="alert.message" :title="alert.title" :auto-close="true" :auto-close-duration="3000" @close="alert.show = false" />
    
    <ConfirmDialog
      v-model="showDeleteModal"
      title="Delete Book"
      :message="selectedItem ? `Delete book '${selectedItem.title}'?` : 'Delete this book?'"
      type="danger"
      theme="admin"
      confirm-text="Delete"
      @confirm="handleDelete"
    />
    
    <!-- Stats Section -->
    <template #stats>
      <div class="row g-3 g-lg-4">
        <div class="col-6 col-xl-4">
          <StatCard title="Total Books" :value="data.length" icon="bi bi-book" bg-color="bg-admin-light" icon-color="text-admin" />
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
        v-model="filters.search"
        search-placeholder="Search books by title, author, ISBN..."
        preset="admin-list"
        :show-status-filter="false"
        :loading="loading"
        @refresh="handleRefresh"
        @reset="resetFilters"
      >
        <template #filters>
          <SelectInput
            v-model="filters.category"
            label="Category"
            placeholder="All Categories"
            :options="BOOK_CATEGORY_OPTIONS"
            col-class="col-md-4 col-6"
            :no-margin="true"
            label-class="small fw-semibold text-dark"
          />
        </template>
      </SearchFilter>
    </template>

    <!-- Books Grid (same pattern as Accounts) -->
    <LoadingSpinner v-if="loading" theme="admin" />
    <div v-else-if="filteredData.length === 0" class="text-center py-5">
      <i class="bi bi-book display-1 text-muted"></i>
      <h5 class="text-muted mt-3">No Books Found</h5>
      <button @click="openCreateModal()" class="btn btn-admin-primary mt-3"><i class="bi bi-plus-circle me-2"></i>Add Book</button>
    </div>
    <div v-else class="row g-4">
      <div v-for="book in filteredData" :key="book.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center">
                <div class="avatar-circle avatar-book me-3"><i class="bi bi-book"></i></div>
                <div>
                  <h6 class="mb-0 fw-semibold">{{ book.title }}</h6>
                  <small class="text-muted">{{ book.author }}</small>
                </div>
              </div>
              <span :class="['badge', book.copies_available > 0 ? 'bg-success' : 'bg-danger']">
                {{ book.copies_available > 0 ? 'Available' : 'Unavailable' }}
              </span>
            </div>

            <div class="mb-2"><small class="text-muted">ISBN</small><div class="fw-medium"><code>{{ book.isbn || '-' }}</code></div></div>
            <div class="mb-2"><small class="text-muted">Publisher</small><div class="fw-medium">{{ book.publisher || 'N/A' }}</div></div>
            <div class="mb-2"><small class="text-muted">Category</small><div class="fw-medium text-capitalize">{{ book.category || 'N/A' }}</div></div>

            <div class="border-top pt-3">
              <small class="text-muted">Copies</small>
              <h5 class="mb-0 fw-bold">{{ book.copies_available || 0 }} / {{ book.copies_total || 0 }}</h5>
            </div>
          </div>

          <div class="card-footer bg-transparent border-top-0">
            <div class="d-flex gap-2">
              <button @click="openEditModal(book)" class="btn btn-sm btn-outline-warning flex-grow-1"><i class="bi bi-pencil me-1"></i>Edit</button>
              <button @click="confirmDelete(book)" class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>

  <EntityFormModal
    v-model="showModal"
    :title="editMode ? 'Edit Book' : 'Add Book'"
    icon="bi bi-book"
    :loading="submitting"
    :confirm-text="editMode ? 'Update Book' : 'Add Book'"
    confirm-variant="btn-admin-primary"
    @confirm="handleSubmit()"
    @close="closeModal"
  >
    <form @submit.prevent="handleSubmit()">
      <div class="row">
        <div class="col-md-8 mb-3"><label class="form-label">Title <span class="text-danger">*</span></label><input v-model="form.title" type="text" class="form-control" required></div>
        <div class="col-md-4 mb-3"><label class="form-label">ISBN</label><input v-model="form.isbn" type="text" class="form-control"></div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-3"><label class="form-label">Author <span class="text-danger">*</span></label><input v-model="form.author" type="text" class="form-control" required></div>
        <div class="col-md-6 mb-3"><label class="form-label">Publisher</label><input v-model="form.publisher" type="text" class="form-control"></div>
      </div>
      <div class="row">
        <div class="col-md-4 mb-3">
          <label class="form-label">Category</label>
          <select v-model="form.category" class="form-select">
            <option v-for="opt in BOOK_CATEGORY_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div class="col-md-4 mb-3"><label class="form-label">Total Copies</label><input v-model.number="form.copies_total" type="number" min="0" class="form-control"></div>
        <div class="col-md-4 mb-3"><label class="form-label">Available</label><input v-model.number="form.copies_available" type="number" min="0" class="form-control"></div>
      </div>
    </form>
  </EntityFormModal>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, SearchFilter, SelectInput, AlertMessage, ConfirmDialog, EntityFormModal, LoadingSpinner } from '@/components/shared/common'
import { useEntityList, useCrudModal, useListStats } from '@/composables/shared'
import { libraryBookService } from '@/services/admin/managementService'
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { BOOK_CATEGORY_OPTIONS } from '@/utils/constants/options'

const breadcrumbs = [{ name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path }, { name: 'Library', href: ADMIN_ROUTES.LIBRARY_BOOKS.path }, { name: 'Books' }]

const defaultForm = { title: '', author: '', isbn: '', publisher: '', category: 'science', copies_total: 1, copies_available: 1 }

const fetchBooks = async () => {
  const res = await libraryBookService.getAll()
  return res.data?.results || res.data || []
}

const { loading, data, filteredData, filters, loadData, resetFilters, refresh } = useEntityList({
  searchFields: ['title', 'author', 'isbn'],
  defaultFilters: { category: '' },
  filterSchema: [
    {
      key: 'category',
      itemValue: 'category'
    }
  ],
  customFilter: (list) => list.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
})

const { alert, showModal, showDeleteModal, editMode, submitting, form, selectedItem, openCreateModal, openEditModal, closeModal, handleSubmit, confirmDelete, handleDelete } = useCrudModal({
  entityName: 'Book',
  createFn: (payload) => libraryBookService.create(payload),
  updateFn: (id, payload) => libraryBookService.update(id, payload),
  deleteFn: (id) => libraryBookService.delete(id),
  onSuccess: () => loadData(fetchBooks, false),
  defaultForm
})

const actions = [{ label: 'Add Book', icon: 'bi bi-plus-circle', variant: 'btn-admin-primary', onClick: openCreateModal }]

const listStats = useListStats(data)
const availableCount = listStats.count((book) => book.copies_available > 0)
const totalCopies = listStats.sum((book) => book.copies_total)

const handleRefresh = () => refresh(fetchBooks)

onMounted(() => loadData(fetchBooks))
</script>


