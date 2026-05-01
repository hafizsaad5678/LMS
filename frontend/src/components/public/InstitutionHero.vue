<template>
  <section class="institution-hero position-relative overflow-hidden" :style="heroHeight">
    <!-- Background Layer -->
    <div 
      class="hero-bg position-absolute top-0 start-0 w-100 h-100" 
      :style="coverStyle"
    ></div>
    
    <!-- Content Overlay -->
    <div class="hero-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center">
      <div class="container position-relative z-1">
        <div class="row align-items-center g-5">
          <div class="col-lg-7" data-aos="fade-right">
            <div class="hero-text-content py-5">
              <div class="d-flex align-items-center gap-2 mb-3">
                <div class="hero-accent-line"></div>
                <span class="text-uppercase tracking-widest fw-bold text-brand small">
                  Excellence in Education
                </span>
              </div>
              <h1 class="display-2 fw-bold mb-4 hero-title text-dark">
                {{ institution.name }}
              </h1>
              <p class="lead mb-5 text-secondary hero-description">
                {{ institution.tagline || 'Shape your future with world-class academic programs and a vibrant campus community designed for success.' }}
              </p>
              <div class="d-flex flex-wrap gap-3">
                <a href="#departments" class="btn btn-brand-lg rounded-pill px-5 py-3 fw-bold shadow-lg">
                  Explore Programs
                </a>
                <router-link :to="{ name: 'InstitutionFaculty', params: { slug: route.params.slug } }" class="btn btn-outline-dark-lg rounded-pill px-5 py-3 fw-bold">
                  Meet Faculty
                </router-link>
              </div>
            </div>
          </div>
          <div class="col-lg-5 d-none d-lg-block" data-aos="fade-left">
            <!-- Floating Stats Cards -->
            <div class="position-relative">
              <div class="stats-card-floating card-1 shadow-lg p-4 rounded-4 bg-white border-0">
                <h3 class="fw-bold mb-0 text-brand">50+</h3>
                <p class="text-muted small mb-0">Academic Programs</p>
              </div>
              <div class="stats-card-floating card-2 shadow-lg p-4 rounded-4 bg-white border-0">
                <h3 class="fw-bold mb-0 text-success">100%</h3>
                <p class="text-muted small mb-0">Career Placement</p>
              </div>
              <div class="stats-card-floating card-3 shadow-lg p-4 rounded-4 bg-white border-0">
                <h3 class="fw-bold mb-0 text-info">20+</h3>
                <p class="text-muted small mb-0">Years of Legacy</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const props = defineProps({
  institution: {
    type: Object,
    required: true
  },
  coverStyle: {
    type: Object,
    default: () => ({})
  }
})

const heroHeight = computed(() => {
  return props.coverStyle?.backgroundImage ? 'height: clamp(500px, 70vh, 800px);' : 'height: 400px;'
})
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

