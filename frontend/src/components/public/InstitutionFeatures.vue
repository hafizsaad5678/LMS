<template>
  <div class="institution-features">
    <div v-if="items.length" class="row g-4 justify-content-center">
      <div v-for="(feature, index) in items" :key="feature.id" class="col-sm-6 col-md-4 col-lg-3" data-aos="fade-up" :data-aos-delay="index * 100">
        <div class="feature-card h-100 p-5 text-center transition-all">
          <div class="feature-icon-box mb-4 mx-auto d-flex align-items-center justify-content-center">
            <i :class="feature.icon || 'bi bi-stars'" class="fs-1"></i>
          </div>
          <h3 class="h5 fw-bold mb-3 text-dark">{{ feature.title }}</h3>
          <p class="text-secondary small mb-0 lh-lg">
            {{ feature.description || 'Dedicated to excellence in student life and academic achievement.' }}
          </p>
        </div>
      </div>
    </div>
    <div v-else class="card border-0 bg-light rounded-4 border-dashed p-5 text-center shadow-sm">
      <p class="text-secondary mb-0">{{ emptyMessage }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  },
  emptyMessage: {
    type: String,
    default: 'No highlights have been added yet.'
  }
})
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

