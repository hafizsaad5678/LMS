<template>
  <div>
    <InstitutionHero :institution="institution" :coverStyle="coverStyle" />

    <!-- Academic Programs -->
    <InstitutionDepartments 
      v-if="departments && departments.length > 0" 
      :departments="departments" 
      :is-home="true"
    />


    <section id="features" class="pt-10 pb-2 bg-white">
      <div class="container">
        <div class="section-header text-center mb-5" data-aos="fade-up">
          <p class="subtitle text-brand fw-bold text-uppercase mb-3">Campus Excellence</p>
          <h2 class="display-5 fw-bold title-font">World-Class Facilities</h2>
          <div class="header-line mx-auto"></div>
        </div>
        <InstitutionFeatures :items="displayFeatures" />
      </div>
    </section>

    <!-- About Section -->
    <InstitutionAbout :institution="institution" :logoUrl="logoUrl" />

    <!-- Testimonials -->
    <InstitutionTestimonials 
      v-if="displayTestimonials && displayTestimonials.length > 0" 
      :testimonials="displayTestimonials" 
    />

  </div>
</template>

<script setup>
import { computed } from 'vue'
import InstitutionHero from '@/components/public/InstitutionHero.vue'
import InstitutionFeatures from '@/components/public/InstitutionFeatures.vue'
import InstitutionAbout from '@/components/public/InstitutionAbout.vue'
import InstitutionTestimonials from '@/components/public/InstitutionTestimonials.vue'
import InstitutionDepartments from '@/components/public/InstitutionDepartments.vue'
import InstitutionEvents from '@/components/public/InstitutionEvents.vue'
import { getFileUrl } from '@/utils/constants/config'

const props = defineProps({
  institution: Object,
  coverStyle: Object,
  departments: Array,
  features: Array,
  events: Array,
  faculty: Array,
  logoUrl: String,
  testimonials: Array,
  galleryItems: Array,
  fileUrl: Function
})

// Fallback Sample Data for Features
const SAMPLE_FEATURES = [
  { id: 'f1', title: 'Digital Library', description: 'Access to over 50,000+ digital resources and research journals.', icon: 'bi bi-book' },
  { id: 'f2', title: 'High-Tech Labs', description: 'State-of-the-art computer and science laboratories for hands-on learning.', icon: 'bi bi-cpu' },
  { id: 'f3', title: 'Sports Complex', description: 'Modern athletic facilities for physical development and competitive sports.', icon: 'bi bi-trophy' },
  { id: 'f4', title: 'Smart Classrooms', description: 'Interactive learning spaces equipped with the latest multimedia technology.', icon: 'bi bi-display' }
]

const SAMPLE_EVENTS = [
  { id: 'e1', title: 'Annual Convocation 2026', description: 'Celebrating our graduates and their academic achievements.', event_date: '2026-06-15', location: 'Main Auditorium' },
  { id: 'e2', title: 'Tech Innovation Expo', description: 'Showcasing student projects and industry partnerships.', event_date: '2026-05-20', location: 'Science Block' }
]

const SAMPLE_TESTIMONIALS = [
  { id: 't1', name: 'Zainab Ahmed', role: 'Computer Science Graduate', content: 'The academic environment here is unmatched. The faculty genuinely cares about student success and career growth.', rating: 5 },
  { id: 't2', name: 'Ahmad Raza', role: 'Business Student', content: 'Our college provides amazing industry exposure through workshops and seminars. Proud to be part of this community.', rating: 5 }
]

const displayFeatures = computed(() => (props.features && props.features.length > 0) ? props.features : SAMPLE_FEATURES)
const displayEvents = computed(() => (props.events && props.events.length > 0) ? props.events : SAMPLE_EVENTS)
const displayTestimonials = computed(() => (props.testimonials && props.testimonials.length > 0) ? props.testimonials : SAMPLE_TESTIMONIALS)
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

