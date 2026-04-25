<template>
  <div class="homescreen-wrapper bg-light text-dark min-vh-100">
    <NavbarSection />
    <main class="pt-5 mt-5 pb-5">
      <div class="container text-center mb-5">
        <h1 class="display-4 fw-bold text-primary">Our Customers</h1>
        <p class="lead text-secondary">Trusted by over 500+ institutions globally</p>
      </div>

      <div class="container mb-5">
        <h3 class="fw-bold mb-4 border-bottom border-light-subtle pb-2">User Types</h3>
        <div class="row g-4 text-center">
          <div class="col-md-4">
            <div class="p-4 bg-white border border-light-subtle rounded h-100">
              <i class="bi bi-people-fill display-4 text-primary mb-3"></i>
              <h4>Teachers</h4>
              <p class="text-secondary small">Focus on teaching, not administration.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="p-4 bg-white border border-light-subtle rounded h-100">
              <i class="bi bi-mortarboard-fill display-4 text-info mb-3"></i>
              <h4>Students</h4>
              <p class="text-secondary small">Learn exactly what you need at your own pace.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="p-4 bg-white border border-light-subtle rounded h-100">
              <i class="bi bi-shield-lock-fill display-4 text-success mb-3"></i>
              <h4>Enterprise Admin</h4>
              <p class="text-secondary small">Control the platform with global settings and analytics.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="container">
        <h3 class="fw-bold mb-4 border-bottom border-light-subtle pb-2">Testimonials</h3>
        <div class="row g-4">
          <div class="col-md-6">
            <div class="p-4 bg-white border border-light-subtle rounded text-center">
              <p class="fst-italic text-secondary">"Deploying this LMS cut our SaaS onboarding in half, and the AI chatbot is a game changer for our students."</p>
              <h5 class="text-primary mt-3">Vicky Kamran</h5>
              <small>Operations Director</small>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-4 bg-white border border-light-subtle rounded text-center">
              <p class="fst-italic text-secondary">"The fast AI quiz generation saves my staff over 20 hours a month in grading."</p>
              <h5 class="text-primary mt-3">Sefraz Chugtai</h5>
              <small>Corporate Trainer</small>
            </div>
          </div>
        </div>
      </div>
    </main>
    <FooterSection />
  </div>
</template>

<script setup>
import NavbarSection from '@/components/shared/home/NavbarSection.vue'
import FooterSection from '@/components/shared/home/FooterSection.vue'
</script>
