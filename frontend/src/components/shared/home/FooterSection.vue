<template>
  <footer class="bg-dark text-light py-5 home-footer border-top border-secondary">
    <div class="container">
      <div class="row g-4 mb-4">
        <div class="col-lg-3">
          <h6 class="fw-bold mb-3 d-flex align-items-center">
            <i class="bi bi-hexagon-fill me-2 text-warning fs-4"></i>SaaS Portal
          </h6>
          <p class="text-light-emphasis small mb-3">
            Empowering global enterprises through scalable learning operations and intelligent metrics.
          </p>
          <div class="d-flex gap-3 mt-3">
            <a v-for="social in socialLinks" :key="social.icon" href="#" class="text-light-emphasis home-social-link" aria-label="Social Link">
              <i :class="[social.icon, 'fs-5']"></i>
            </a>
          </div>
        </div>
        <div v-for="section in footerSections" :key="section.title" class="col-lg-3">
          <h6 class="fw-bold mb-3">{{ section.title }}</h6>
          <ul class="list-unstyled small mb-0">
            <li v-for="link in section.links" :key="link" class="mb-2">
              <a href="#" class="text-light-emphasis text-decoration-none home-footer-link">{{ link }}</a>
            </li>
          </ul>
        </div>
      </div>
      <hr class="border-secondary">
      <div class="row align-items-center">
        <div class="col-md-6 text-center text-md-start">
          <small class="text-light-emphasis">&copy; {{ new Date().getFullYear() }} SaaS Portal Inc. All rights reserved.</small>
        </div>
        <div class="col-md-6 text-center text-md-end">
          <small class="text-light-emphasis">
            <a href="#" class="text-light-emphasis text-decoration-none me-3 home-footer-link">Privacy Policy</a>
            <a href="#" class="text-light-emphasis text-decoration-none me-3 home-footer-link">Terms of Service</a>
            <a href="#" class="text-light-emphasis text-decoration-none home-footer-link">System Status</a>
          </small>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
const socialLinks = [
  { icon: 'bi bi-linkedin' },
  { icon: 'bi bi-twitter-x' },
  { icon: 'bi bi-github' },
  { icon: 'bi bi-youtube' },
]

const footerSections = [
  { title: 'Product', links: ['Features', 'Pricing', 'API Docs', 'Enterprise Solutions'] },
  { title: 'Resources', links: ['Help Center', 'Webinars', 'Case Studies', 'Status Page'] },
  { title: 'Company', links: ['About Us', 'Careers', 'Contact Sales', 'Partner Program'] },
]
</script>