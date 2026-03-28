<template>
  <div v-if="totalPages > 1" class="d-flex justify-content-center mt-4">
    <nav>
      <ul class="pagination mb-0">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" :class="textClass" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">
            <i class="bi bi-chevron-left"></i>
          </button>
        </li>
        <li v-for="page in displayPages" :key="page" class="page-item" :class="{ active: page === currentPage }">
          <button class="page-link" :class="page === currentPage ? activeClass : textClass" @click="changePage(page)">
            {{ page }}
          </button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <button class="page-link" :class="textClass" @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">
            <i class="bi bi-chevron-right"></i>
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  theme: { type: String, default: 'admin' } // admin, teacher, student
})

const emit = defineEmits(['change'])

const textClass = computed(() => {
  const classes = { admin: 'text-danger', teacher: 'text-primary', student: 'text-success' }
  return classes[props.theme] || 'text-danger'
})

const activeClass = computed(() => {
  const classes = { admin: 'bg-danger border-danger text-white', teacher: 'bg-primary border-primary text-white', student: 'bg-success border-success text-white' }
  return classes[props.theme] || 'bg-danger border-danger text-white'
})

const displayPages = computed(() => {
  const pages = []
  const start = Math.max(1, props.currentPage - 2)
  const end = Math.min(props.totalPages, props.currentPage + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const changePage = (page) => {
  if (page >= 1 && page <= props.totalPages && page !== props.currentPage) {
    emit('change', page)
  }
}
</script>
