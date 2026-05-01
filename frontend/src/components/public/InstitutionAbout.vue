<template>
  <section id="about" class="pt-2 pb-5 bg-white overflow-hidden">
    <div class="container position-relative">
      <div class="row g-4 align-items-start">
        <!-- Image Column -->
        <div class="col-lg-4 text-center text-lg-start">
          <div class="position-relative d-inline-block w-100">
            <!-- Principal Image -->
            <div v-if="principalImageUrl" class="principal-portrait shadow-sm border rounded-2 overflow-hidden">
              <img 
                :src="principalImageUrl" 
                class="img-fluid principal-img" 
                alt="Principal" 
              />
            </div>
            
            <div v-else class="bg-light rounded-2 shadow-sm d-flex align-items-center justify-content-center logo-placeholder">
              <i class="bi bi-person-circle text-secondary placeholder-icon"></i>
            </div>
          </div>
        </div>
        
        <!-- Content Column -->
        <div class="col-lg-8">
          <div class="ps-lg-4">
            <h2 class="mb-3 fw-bold h3 message-title">Principal's Message</h2>
            
            <div class="message-content text-secondary">
              <div class="description-text">{{ institution.principal_message || 'Welcome to our institution. We are dedicated to providing excellence in education and fostering a supportive learning environment for all our students.' }}</div>
              
              <div class="signature-block mt-4 pt-2">
                <h3 class="h5 fw-bold message-signature mb-0">{{ institution.principal_name || 'Prof. Dr. Muhammad Akram Virk.' }}</h3>
                <p class="text-muted small mb-0">Principal, {{ institution.name }}</p>
              </div>
            </div>
            
            <!-- Mission/Vision (Keep for extra info if needed, or remove if user wants strict copy) -->
            <div class="row g-4 mt-5" v-if="institution.mission || institution.vision">
              <div class="col-md-6" v-if="institution.mission">
                <div class="p-4 rounded-3 h-100 border-start border-4 border-primary bg-light">
                  <h5 class="fw-bold mb-2 d-flex align-items-center small text-uppercase letter-spacing-1">
                    <i class="bi bi-bullseye me-2 text-primary"></i> Mission
                  </h5>
                  <p class="text-secondary small mb-0">{{ institution.mission }}</p>
                </div>
              </div>
              <div class="col-md-6" v-if="institution.vision">
                <div class="p-4 rounded-3 h-100 border-start border-4 border-info bg-light">
                  <h5 class="fw-bold mb-2 d-flex align-items-center small text-uppercase letter-spacing-1">
                    <i class="bi bi-eye me-2 text-info"></i> Vision
                  </h5>
                  <p class="text-secondary small mb-0">{{ institution.vision }}</p>
                </div>
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

const props = defineProps({
  institution: {
    type: Object,
    required: true
  },
  logoUrl: {
    type: String,
    default: ''
  }
})

const principalImageUrl = computed(() => {
  if (!props.institution.principal_image) {
    // Professional Placeholder for Principal
    return 'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=800'
  }
  if (props.institution.principal_image.startsWith('http')) return props.institution.principal_image
  return `${import.meta.env.VITE_API_BASE_URL.replace('/api', '')}${props.institution.principal_image}`
})
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

