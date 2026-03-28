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
        :show-status-filter="false"
        search-col-size="col-md-5 col-12"
        actions-col-size="col-md-3 col-6"
        :loading="loading"
        @refresh="() => refresh(fetchBooks)"
        @reset="resetFilters"
      >
        <template #filters>
          <div class="col-md-4 col-6">
            <label class="form-label small fw-semibold text-dark">Category</label>
            <select v-model="filters.category" class="form-select">
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
    <DataTable :columns="tableColumns" :data="filteredData" :loading="loading" loading-text="Loading books..." empty-icon="bi bi-book" empty-title="No books found" empty-subtitle="Add your first book to get started">
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
        <ActionButtons :item="row" :show-view="false" @edit="openEditModal(row)" @delete="confirmDelete(row)" />
      </template>
    </DataTable>

    <!-- Add/Edit Book Modal -->
    <div v-if="showModal" class="modal show d-block modal-backdrop-custom" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">{{ editMode ? 'Edit Book' : 'Add Book' }}</h5><button type="button" class="btn-close" @click="closeModal"></button></div>
          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <div class="row">
                <div class="col-md-8 mb-3"><label class="form-label">Title <span class="text-danger">*</span></label><input v-model="form.title" type="text" class="form-control" required></div>
                <div class="col-md-4 mb-3"><label class="form-label">ISBN</label><input v-model="form.isbn" type="text" class="form-control"></div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Author <span class="text-danger">*</span></label><input v-model="form.author" type="text" class="form-control" required></div>
                <div class="col-md-6 mb-3"><label class="form-label">Publisher</label><input v-model="form.publisher" type="text" class="form-control"></div>
              </div>
              <div class="row">
                <div class="col-md-4 mb-3"><label class="form-label">Category</label><select v-model="form.category" class="form-select"><option value="science">Science</option><option value="technology">Technology</option><option value="arts">Arts</option><option value="literature">Literature</option><option value="history">History</option></select></div>
                <div class="col-md-4 mb-3"><label class="form-label">Total Copies</label><input v-model.number="form.copies_total" type="number" class="form-control"></div>
                <div class="col-md-4 mb-3"><label class="form-label">Available</label><input v-model.number="form.copies_available" type="number" class="form-control"></div>
              </div>
              <div class="d-flex gap-2 justify-content-end">
                <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                <button type="submit" class="btn btn-admin-primary" :disabled="submitting">{{ editMode ? 'Update' : 'Add' }} Book</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AdminPageTemplate>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { AdminPageTemplate } from '@/components/shared/panels'
import { StatCard, DataTable, SearchFilter, ActionButtons, AlertMessage, ConfirmDialog } from '@/components/shared/common'
import { useEntityList, useCrudModal } from '@/composables/shared'
import { libraryBookService } from '@/services/admin/managementService'
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const breadcrumbs = [{ name: 'Dashboard', href: ADMIN_ROUTES.DASHBOARD.path }, { name: 'Library', href: ADMIN_ROUTES.LIBRARY_BOOKS.path }, { name: 'Books' }]

const tableColumns = [
  { key: 'title', label: 'Book' },
  { key: 'author', label: 'Author', hideOnMobile: true },
  { key: 'category', label: 'Category', hideOnMobile: true },
  { key: 'isbn', label: 'ISBN', hideOnMobile: true },
  { key: 'copies', label: 'Copies' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions', center: true }
]

const defaultForm = { title: '', author: '', isbn: '', publisher: '', category: 'science', copies_total: 1, copies_available: 1 }

const fetchBooks = async () => {
  const res = await libraryBookService.getAll()
  return res.data?.results || res.data || []
}

const { loading, data, filteredData, filters, loadData, resetFilters, refresh } = useEntityList({
  searchFields: ['title', 'author', 'isbn'],
  defaultFilters: { category: '' },
  customFilter: (list, f) => {
    if (f.category) list = list.filter(b => b.category === f.category)
    return list.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
  }
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

const availableCount = computed(() => data.value.filter(b => b.copies_available > 0).length)
const totalCopies = computed(() => data.value.reduce((sum, b) => sum + (b.copies_total || 0), 0))

onMounted(() => loadData(fetchBooks))
</script>


