<template>
  <footer id="contact" class="pt-4 pb-3 footer-main">
    <div class="container-fluid px-lg-5">
      <div class="row g-4 align-items-start">
        
        <!-- Left Side: Department Directory (3 Columns) -->
        <div class="col-lg-8">
          <h2 class="text-white mb-4 fw-bold h6 text-uppercase tracking-widest opacity-50">Contact Directory</h2>
          
          <div class="contact-list row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-3 g-2">
            <template v-if="deptContacts.length > 0">
              <div v-for="contact in deptContacts" :key="contact.id" class="col">
                <div class="contact-item p-2 h-100">
                  <h4 class="footer-dept-title mb-1">{{ contact.displayTitle }}</h4>
                  <div v-if="contact.phone" class="d-flex align-items-center gap-2">
                    <i class="bi bi-telephone-fill text-white-50 extra-extra-small"></i>
                    <span class="text-white opacity-90 extra-extra-small">{{ contact.phone }}</span>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="col-12">
                <p class="text-white-50 extra-small italic">Department contacts will appear here.</p>
              </div>
            </template>
          </div>

          <!-- Social Links -->
          <div class="d-flex gap-2 mt-4">
            <a v-if="institution.facebook_url" :href="institution.facebook_url" target="_blank" class="social-icon">
              <i class="bi bi-facebook"></i>
            </a>
            <a v-if="institution.twitter_url" :href="institution.twitter_url" target="_blank" class="social-icon">
              <i class="bi bi-twitter"></i>
            </a>
            <a v-if="institution.linkedin_url" :href="institution.linkedin_url" target="_blank" class="social-icon">
              <i class="bi bi-linkedin"></i>
            </a>
            <a v-if="institution.instagram_url" :href="institution.instagram_url" target="_blank" class="social-icon">
              <i class="bi bi-instagram"></i>
            </a>
          </div>
        </div>

        <!-- Right Side: Branding and Main Office (Compact) -->
        <div class="col-lg-4">
          <div class="branding-office-card p-3 rounded-4 shadow-sm">
            <div class="text-start mb-3">
              <!-- Circular Crest (Small) -->
              <div v-if="logoUrl" class="crest-circle shadow-sm mb-3">
                <img :src="logoUrl" :alt="`${institution.name} crest`" class="footer-crest-img" />
              </div>
              
              <h3 class="h5 fw-bold text-white mb-1">{{ institution.name }}</h3>
              <p class="text-white-50 extra-extra-small mb-0 tracking-wide">
                {{ institution.footer_text || institution.tagline || 'Excellence in Education' }}
              </p>
            </div>

            <!-- Main Office Contact -->
            <div class="main-office-section pt-3 border-top border-light border-opacity-10 text-start">
              <h4 class="extra-small fw-bold text-white mb-2 text-uppercase tracking-wider">College Office</h4>
              
              <div class="d-flex flex-column gap-2">
                <div v-if="institution.phone" class="d-flex align-items-center gap-2">
                  <i class="bi bi-telephone-fill text-white extra-small"></i>
                  <span class="text-white fw-bold extra-small">{{ institution.phone }}</span>
                </div>
                
                <div v-if="institution.email" class="d-flex align-items-center gap-2">
                  <i class="bi bi-envelope-fill text-white extra-small"></i>
                  <span class="text-white opacity-90 extra-small">{{ institution.email }}</span>
                </div>
                
                <div v-if="institution.address" class="d-flex align-items-start gap-2">
                   <i class="bi bi-geo-alt-fill text-white extra-small mt-1"></i>
                   <span class="text-white-50 extra-small">{{ institution.address }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <hr class="mt-4 mb-3 border-light opacity-10">

      <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
        <p class="extra-small text-white-50 mb-0">&copy; {{ new Date().getFullYear() }} {{ institution.name }}</p>
        <p class="extra-small text-white-50 mb-0">Powered by <span class="text-white fw-semibold">LearnMS</span></p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  contacts: {
    type: Array,
    default: () => []
  },
  institution: {
    type: Object,
    required: true
  },
  logoUrl: {
    type: String,
    default: ''
  }
})

const deptContacts = computed(() => {
  return props.contacts
    .filter(c => c.id.startsWith('dept-'))
    .map(c => {
      const baseName = c.title.replace(/\bDepartment\b/gi, '').trim()
      const formattedName = baseName.charAt(0).toUpperCase() + baseName.slice(1).toLowerCase()
      return {
        ...c,
        displayTitle: `Department of ${formattedName}`
      }
    })
})
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

