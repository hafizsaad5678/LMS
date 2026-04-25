<template>
  <div class="homescreen-wrapper bg-light text-dark min-vh-100">
    <NavbarSection />
    <main class="pt-5 mt-5 pb-5">
      <div class="container text-center mb-5">
        <h1 class="display-4 fw-bold text-primary">Careers</h1>
        <p class="lead text-secondary">Join us in building the unified educational enterprise</p>
      </div>

      <div class="container">
        <div class="row justify-content-center mb-5">
          <div class="col-lg-8">
            <h3 class="fw-bold mb-4 border-bottom border-light-subtle pb-2">Open Roles</h3>
            <div class="list-group">
              <a href="#" class="list-group-item list-group-item-action bg-white border-light-subtle p-4 mb-3 rounded">
                <div class="d-flex w-100 justify-content-between">
                  <h5 class="mb-1 text-primary">Frontend Developer</h5>
                  <small class="text-secondary">Remote / On-site</small>
                </div>
                <p class="mb-1 text-dark">Help us craft stunning Vue.js UI components and fluid animations.</p>
                <small class="text-success"><i class="bi bi-briefcase-fill me-1"></i> Full Time</small>
              </a>
              <a href="#" class="list-group-item list-group-item-action bg-white border-light-subtle p-4 mb-3 rounded">
                <div class="d-flex w-100 justify-content-between">
                  <h5 class="mb-1 text-primary">Backend Developer</h5>
                  <small class="text-secondary">Remote</small>
                </div>
                <p class="mb-1 text-dark">Optimize our Django APIs, handle caching, and engineer database scaling strategies.</p>
                <small class="text-success"><i class="bi bi-briefcase-fill me-1"></i> Full Time</small>
              </a>
              <a href="#" class="list-group-item list-group-item-action bg-white border-light-subtle p-4 mb-3 rounded">
                <div class="d-flex w-100 justify-content-between">
                  <h5 class="mb-1 text-primary">AI Engineer</h5>
                  <small class="text-secondary">Hybrid</small>
                </div>
                <p class="mb-1 text-dark">Research and integrate the latest LLM models into our scalable Python environment.</p>
                <small class="text-success"><i class="bi bi-briefcase-fill me-1"></i> Full Time</small>
              </a>
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
