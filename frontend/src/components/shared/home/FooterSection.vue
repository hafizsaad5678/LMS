<template>
  <footer class="bg-light text-dark py-5 home-footer border-top">
    <div class="container">
      <div class="row g-4 mb-4">
        <div class="col-lg-4">
          <h6 class="fw-bold mb-3 d-flex align-items-center">
            <i class="bi bi-hexagon-fill me-2 text-primary fs-4"></i>LearnMS
          </h6>
          <p class="text-secondary small mb-3" style="max-width: 250px;">
            Empowering global enterprises through scalable learning operations and intelligent metrics.
          </p>
          <div class="d-flex gap-3 mt-3">
            <a v-for="social in socialLinks" :key="social.icon" href="#" class="text-secondary home-social-link" aria-label="Social Link">
              <i :class="[social.icon, 'fs-5']"></i>
            </a>
          </div>
        </div>
        <div v-for="section in footerSections" :key="section.title" class="col-lg-2 col-md-4 col-6">
          <h6 class="fw-bold mb-3">{{ section.title }}</h6>
          <ul class="list-unstyled small mb-0">
            <li v-for="link in section.links" :key="link.label" class="mb-2">
              <router-link :to="link.path" class="text-secondary text-decoration-none home-footer-link">{{ link.label }}</router-link>
            </li>
          </ul>
        </div>
      </div>
      <hr class="border-light-subtle">
      <div class="row align-items-center">
        <div class="col-md-6 text-center text-md-start">
          <small class="text-secondary">&copy; {{ new Date().getFullYear() }} SaaS Portal Inc. All rights reserved.</small>
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
  { title: 'Product', links: [{ label: 'Features', path: '/features' }, { label: 'Pricing', path: '/pricing' }] },
  { title: 'Resources', links: [{ label: 'Help Center', path: '/help' }] },
  { title: 'Customers', links: [{ label: 'Customers', path: '/customers' }] },
  { title: 'Company', links: [{ label: 'About Us', path: '/about' }, { label: 'Careers', path: '/careers' }, { label: 'Contact Sales', path: '/contact' }] },
]
</script>