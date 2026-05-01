<template>
  <section v-if="testimonials && testimonials.length > 0" class="py-5 position-relative overflow-hidden testimonial-section">
    <!-- Background Decoration -->
    <div class="position-absolute top-0 end-0 p-5 opacity-10">
      <i class="bi bi-chat-quote display-1 icon-brand"></i>
    </div>

    <div class="container py-4">
      <div class="text-center mb-5">
        <p class="text-uppercase fw-bold mb-2 testimonial-subtitle">Testimonials</p>
        <h2 class="mb-0 testimonial-title">Student & Parent Stories</h2>
        <p class="text-secondary mt-3 mx-auto testimonial-lead">Hear directly from our community about their experiences and successes with our institution.</p>
      </div>

      <div class="row g-4 justify-content-center">
        <div v-for="testimonial in testimonials" :key="testimonial.id" class="col-md-6 col-lg-4">
          <div class="card h-100 border-0 shadow-sm rounded-4 position-relative p-4 bg-white hover-lift transition-all">
            <div class="mb-3 d-flex align-items-center justify-content-between">
              <div class="d-flex">
                <i v-for="n in 5" :key="n" class="bi star-icon" :class="n <= (testimonial.rating || 5) ? 'bi-star-fill text-warning' : 'bi-star text-muted opacity-25'"></i>
              </div>
              <i class="bi bi-quote text-secondary opacity-25 fs-1"></i>
            </div>
            
            <p class="text-secondary mb-4 position-relative z-1 testimonial-content">
              "{{ testimonial.content }}"
            </p>
            
            <div class="mt-auto pt-4 border-top d-flex align-items-center gap-3">
              <div class="position-relative">
                <img 
                  v-if="testimonial.profile_image" 
                  :src="getFileUrl(testimonial.profile_image)" 
                  class="rounded-circle object-fit-cover shadow-sm border border-2 border-white profile-img" 
                  alt="Profile"
                />
                <div v-else class="rounded-circle bg-light d-flex align-items-center justify-content-center text-secondary border border-2 border-white profile-placeholder">
                  <i class="bi bi-person-fill fs-4"></i>
                </div>
              </div>
              
              <div>
                <h6 class="mb-0 fw-bold text-dark">{{ testimonial.name }}</h6>
                <p class="small text-muted mb-0 role-text">{{ testimonial.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { getFileUrl } from '@/utils/constants/config'

defineProps({
  testimonials: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

