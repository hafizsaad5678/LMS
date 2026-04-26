<template>
  <section id="hero" class="py-5 pt-5 home-hero home-bg-dark-navy home-hero-compact">
    <div class="container mt-5 pt-4">
      <div class="row align-items-center g-5">
        <!-- Text Content (Left Side) -->
        <div class="col-lg-6 text-start">
          <h1 class="display-4 fw-bold mb-4 text-white">
            Teach Smarter, <br>Manage Faster
          </h1>
          <p class="lead text-white mb-5 opacity-75" style="max-width: 500px; font-size: 1.1rem;">
            A unified platform to streamline admissions, elevate training, and empower educators with data-driven insights.
          </p>
          <div class="d-flex justify-content-start gap-3 flex-wrap mb-4">
            <button @click="$emit('primary-action')" class="btn btn-warning px-5 py-2 rounded-pill fw-bold shadow-sm text-dark home-bg-warning">
              {{ primaryActionLabel }}
            </button>
            <router-link to="/features" class="btn btn-outline-light px-4 py-2 rounded-pill fw-semibold border-white border-opacity-25">
              See Features
            </router-link>
            <router-link to="/presentation" class="btn btn-outline-warning px-4 py-2 rounded-pill fw-semibold">
              <i class="bi bi-easel me-1"></i>Presentation
            </router-link>
          </div>
          
          <!-- Key Highlights -->
          <div class="row g-3 mt-4">
            <div v-for="highlight in heroHighlights" :key="highlight.title" class="col-md-6">
              <div class="d-flex align-items-start text-white-50">
                <i :class="[highlight.icon, 'text-warning me-2 fs-5']"></i>
                <div>
                  <h6 class="text-white mb-1 small fw-bold">{{ highlight.title }}</h6>
                  <p class="mb-0 overflow-hidden" style="font-size: 0.75rem;">{{ highlight.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Image Content (Right Side) -->
        <div class="col-lg-6">
          <div class="position-relative">
            <!-- Background Glow -->
            <div class="home-glow-aura" style="width: 350px; height: 350px;"></div>
            
            <div class="card bg-transparent border-0 shadow-lg position-relative z-1 home-card-premium overflow-hidden">
              <div class="p-2 bg-white bg-opacity-10 border border-white border-opacity-10 home-card-compact">
                 <img :src="heroImage" alt="LearnMS Dashboard Preview" class="img-fluid rounded-3 shadow-sm border border-white border-opacity-10">
              </div>
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