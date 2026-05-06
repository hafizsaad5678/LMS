<template>
  <div class="institution-landing" :style="themeStyle">
    <div v-if="loading" class="min-vh-100 d-flex flex-column align-items-center justify-content-center bg-light">
      <div class="spinner mb-3"></div>
      <p class="text-secondary fw-medium">Loading institution profile...</p>
    </div>

    <div v-else-if="error" class="min-vh-100 d-flex flex-column align-items-center justify-content-center bg-light">
      <h2 class="text-danger mb-2">Institution not available</h2>
      <p class="text-secondary">{{ error }}</p>
      <router-link to="/" class="btn btn-outline-secondary mt-3">Return to Home</router-link>
    </div>

    <div v-else>
      <InstitutionNavbar :institution="institution" :logoUrl="logoUrl" />

      <main style="min-height: calc(100vh - 80px);" class="bg-white">
        <router-view 
          :institution="institution"
          :coverStyle="coverStyle"
          :departments="departments"
          :galleryItems="galleryItems"
          :features="features"
          :events="events"
          :admissions="admissions"
          :faculty="faculty"
          :testimonials="testimonials"
          :logoUrl="logoUrl"
          :fileUrl="fileUrl"
        />
      </main>

      <InstitutionContactFooter :contacts="allContacts" :institution="institution" :logoUrl="logoUrl" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { institutionService } from '@/services/shared'
import { getFileUrl } from '@/utils/constants/config'

import InstitutionNavbar from '@/components/public/InstitutionNavbar.vue'
import InstitutionContactFooter from '@/components/public/InstitutionContactFooter.vue'

const route = useRoute()
const slug = computed(() => route.params.slug)

const loading = ref(true)
const error = ref('')
const institution = ref(null)

const loadInstitution = async () => {
  if (!slug.value) return
  loading.value = true
  error.value = ''

  try {
    institution.value = await institutionService.getInstitutionProfileBySlug(slug.value)
  } catch (err) {
    const status = err?.response?.status
    error.value = status === 404
      ? 'We could not find this institution. Please check the URL slug.'
      : 'Failed to load institution profile. Please try again.'
    institution.value = null
  } finally {
    loading.value = false
  }
}

watch(slug, loadInstitution, { immediate: true })

const themeColor = computed(() => institution.value?.theme_color || '#0f766e')
const coverUrl = computed(() => getFileUrl(institution.value?.cover_image))
const logoUrl = computed(() => getFileUrl(institution.value?.logo))
const departments = computed(() => institution.value?.departments || [])
const galleryItems = computed(() => institution.value?.gallery || [])
const features = computed(() => institution.value?.features || [])
const events = computed(() => institution.value?.events || [])
const admissions = computed(() => institution.value?.admissions || null)
const allContacts = computed(() => institution.value?.all_contacts || [])
const faculty = computed(() => institution.value?.faculty || [])
const testimonials = computed(() => institution.value?.testimonials || [])

const contactInfo = computed(() => {
  const contact = institution.value?.contact || {}
  return {
    title: contact.title || 'Contact',
    description: contact.description || '',
    email: contact.email || institution.value?.email || '',
    phone: contact.phone || institution.value?.phone || '',
    website: contact.website || institution.value?.website || '',
    address: contact.address || institution.value?.address || ''
  }
})

const toRgba = (hex, alpha) => {
  if (!hex || typeof hex !== 'string' || !hex.startsWith('#')) {
    return `rgba(15, 118, 110, ${alpha})`
  }
  let cleaned = hex.replace('#', '')
  if (cleaned.length === 3) {
    cleaned = cleaned.split('').map((ch) => ch + ch).join('')
  }
  if (cleaned.length !== 6) {
    return `rgba(15, 118, 110, ${alpha})`
  }
  const num = parseInt(cleaned, 16)
  const r = (num >> 16) & 255
  const g = (num >> 8) & 255
  const b = num & 255
  return { r, g, b, rgba: `rgba(${r}, ${g}, ${b}, ${alpha})` }
}

const themeStyle = computed(() => {
  const rgb = toRgba(themeColor.value, 1)
  return {
    '--brand': themeColor.value,
    '--brand-rgb': `${rgb.r}, ${rgb.g}, ${rgb.b}`,
    '--brand-soft': toRgba(themeColor.value, 0.12).rgba,
    '--brand-strong': toRgba(themeColor.value, 0.2).rgba
  }
})

const coverStyle = computed(() => {
  if (coverUrl.value) {
    return {
      backgroundImage: `linear-gradient(120deg, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.1)), url('${coverUrl.value}')`
    }
  }

  return {
    backgroundImage: 'linear-gradient(120deg, #f1f5f9, #ffffff 65%, #e2e8f0)'
  }
})

const fileUrl = (url) => getFileUrl(url)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

.institution-landing {
  font-family: 'Manrope', 'Segoe UI', sans-serif;
  color: #0f172a;
}

.spinner {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 4px solid rgba(15, 23, 42, 0.15);
  border-top-color: var(--brand);
  animation: spin 0.8s linear infinite;
}



@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

<style>
/* Global reset for landing pages to remove default body padding from custom.css */
body {
  padding-top: 0 !important;
}
</style>
