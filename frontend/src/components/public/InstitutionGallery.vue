<template>
  <div class="gallery-page pb-5">
    <!-- Breadcrumb Header -->
    <div class="bg-light py-4 border-bottom mb-5">
      <div class="container text-center">
        <p class="text-uppercase fw-bold mb-2 text-brand tracking-wider small">Campus Life</p>
        <h1 class="display-5 fw-bold title-font mb-0">Photo Gallery</h1>
        <div class="header-line mx-auto mt-3"></div>
      </div>
    </div>

    <div class="container">
      <!-- Category Tabs -->
      <div class="d-flex justify-content-center mb-5 overflow-auto pb-2">
        <div class="btn-group rounded-pill bg-light p-1 shadow-sm">
          <button 
            v-for="cat in categories" 
            :key="cat"
            class="btn rounded-pill px-4 py-2 fw-semibold transition-all border-0"
            :class="activeCategory === cat ? 'btn-brand text-white shadow' : 'text-secondary'"
            @click="activeCategory = cat"
          >
            {{ cat.charAt(0).toUpperCase() + cat.slice(1) }}
          </button>
        </div>
      </div>

      <div v-if="filteredGallery.length" class="row g-4">
        <div v-for="(item, index) in filteredGallery" :key="item.id" class="col-sm-6 col-md-4 col-lg-3">
          <div 
            class="gallery-item-card h-100 border-0 shadow-sm rounded-4 overflow-hidden position-relative"
            @click="openLightbox(index)"
          >
            <div class="ratio ratio-1x1 bg-light cursor-pointer">
              <img 
                :src="fileUrl(item.image)" 
                :alt="item.caption || 'Gallery image'" 
                class="object-fit-cover w-100 h-100 transition-all" 
              />
            </div>
            <!-- Category Badge -->
            <div v-if="item.category" class="position-absolute top-0 start-0 m-3 z-2">
              <span class="badge bg-white text-dark shadow-sm rounded-pill px-3 py-2 opacity-90 fw-bold extra-small">
                {{ item.category.toUpperCase() }}
              </span>
            </div>
            <div class="gallery-overlay d-flex flex-column justify-content-end p-3">
              <p class="text-white small mb-0 fw-medium text-truncate-2">{{ item.caption || 'Campus moment' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="py-5 text-center my-5">
        <div class="empty-state-icon mx-auto mb-4">
          <i class="bi bi-images display-1 text-muted opacity-25"></i>
        </div>
        <h4 class="text-secondary fw-bold">No Photos Available</h4>
        <p class="text-muted">No photos found in the "{{ activeCategory }}" category.</p>
        <button v-if="activeCategory !== 'all'" @click="activeCategory = 'all'" class="btn btn-brand rounded-pill mt-3 px-4 shadow">
          View All Photos
        </button>
        <button v-else @click="$router.back()" class="btn btn-outline-secondary mt-3 px-4 rounded-pill">
          <i class="bi bi-arrow-left me-2"></i>Go Back
        </button>
      </div>
    </div>

    <!-- Simple Lightbox (Modal) -->
    <div v-if="lightbox.show" class="gallery-lightbox" @click.self="closeLightbox">
      <button class="lightbox-close" @click="closeLightbox">
        <i class="bi bi-x-lg"></i>
      </button>
      <button class="lightbox-nav prev" @click="prevImage" v-if="galleryItems.length > 1">
        <i class="bi bi-chevron-left"></i>
      </button>
      <button class="lightbox-nav next" @click="nextImage" v-if="filteredGallery.length > 1">
        <i class="bi bi-chevron-right"></i>
      </button>
      
      <div class="lightbox-content animate__animated animate__zoomIn">
        <img :src="fileUrl(activeImage.image)" :alt="activeImage.caption" class="img-fluid rounded shadow-lg" />
        <div class="lightbox-caption bg-dark bg-opacity-75 text-white p-3 rounded-bottom">
          <div v-if="activeImage.category" class="badge bg-brand mb-2">{{ activeImage.category.toUpperCase() }}</div>
          <p class="mb-0">{{ activeImage.caption || 'Campus moment' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  galleryItems: {
    type: Array,
    default: () => []
  },
  fileUrl: {
    type: Function,
    required: true
  }
})

const activeCategory = ref('all')

// Dynamically extract unique categories from real data
const categories = computed(() => {
  const cats = new Set(['all'])
  
  props.galleryItems.forEach(item => {
    if (item.category) cats.add(item.category.toLowerCase())
  })
  
  return Array.from(cats)
})

const filteredGallery = computed(() => {
  if (activeCategory.value === 'all') return props.galleryItems
  
  return props.galleryItems.filter(item => item.category?.toLowerCase() === activeCategory.value)
})


const lightbox = ref({
  show: false,
  index: 0
})

const activeImage = computed(() => filteredGallery.value[lightbox.value.index] || {})

const openLightbox = (index) => {
  lightbox.value.index = index
  lightbox.value.show = true
  document.body.style.overflow = 'hidden' // Prevent scroll
}

const closeLightbox = () => {
  lightbox.value.show = false
  document.body.style.overflow = '' // Restore scroll
}

const nextImage = () => {
  lightbox.value.index = (lightbox.value.index + 1) % filteredGallery.value.length
}

const prevImage = () => {
  lightbox.value.index = (lightbox.value.index - 1 + filteredGallery.value.length) % filteredGallery.value.length
}
</script>

<style scoped>
/* Component styles are extracted to institution.css */
</style>

