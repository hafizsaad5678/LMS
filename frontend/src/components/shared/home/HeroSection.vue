<template>
  <section id="hero" class="py-5 pt-5 bg-dark bg-gradient min-vh-100 d-flex align-items-center position-relative overflow-hidden home-hero">
    <span class="home-orb home-orb-one" aria-hidden="true"></span>
    <span class="home-orb home-orb-two" aria-hidden="true"></span>
    <div class="container">
      <div class="row align-items-center g-5 py-5">
        <div class="col-lg-6">
          <div class="ps-md-4 home-hero-copy">
            <span class="badge bg-info text-dark mb-3 px-3 py-2">Built for high-performance SaaS</span>
            <h1 class="display-3 fw-bold mb-4 text-white">
              Teach Smarter,
              <span class="text-warning d-block">Manage Faster</span>
            </h1>
            <p class="lead text-white mb-5 opacity-75 lh-lg">
              One unified LMS platform for admissions, training operations, communication, and real-time insights across organizations.
            </p>
            <div class="d-flex flex-wrap gap-3 mb-5">
              <button @click="$emit('primary-action')" class="btn btn-warning btn-lg px-5 rounded-pill fw-semibold shadow">
                <i :class="[primaryActionIcon, 'me-2']"></i>{{ primaryActionLabel }}
              </button>
              <button @click="$emit('scroll-features')" class="btn btn-outline-light btn-lg px-5 rounded-pill fw-semibold">
                <i class="bi bi-arrow-down-circle me-2"></i>See Features
              </button>
            </div>
            <div class="row g-4">
              <div v-for="item in heroHighlights" :key="item.title" class="col-md-6">
                <div class="p-3 rounded-3 border border-light border-opacity-10 h-100 home-highlight">
                  <p class="text-light fw-semibold mb-1">
                    <i :class="[item.icon, 'me-2 text-info']"></i>{{ item.title }}
                  </p>
                  <p class="text-light opacity-75 small mb-0">{{ item.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-6 text-center pe-md-4">
          <div class="position-relative p-2 rounded-4 home-hero-media">
            <img :src="heroImage" alt="SaaS Dashboard" class="img-fluid rounded-4 shadow-lg w-100 home-hero-image">
            <div class="position-absolute top-0 start-0 mt-3 ms-3">
              <span class="badge bg-success bg-opacity-90 text-white px-3 py-2">Platform Live</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import heroImage from '@/assets/progress.png'

defineProps({
  primaryActionLabel: { type: String, required: true },
  primaryActionIcon: { type: String, required: true }
})
defineEmits(['primary-action', 'scroll-features'])

const heroHighlights = [
  { icon: 'bi bi-shield-check', title: 'Role-based secure access', description: 'Students, teachers, and admins each get focused permissions.' },
  { icon: 'bi bi-graph-up-arrow', title: 'Real-time progress insights', description: 'Track SaaS metrics, class performance, and outcomes seamlessly.' },
]
</script>