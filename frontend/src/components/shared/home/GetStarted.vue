<template>
  <div class="homescreen-wrapper bg-light text-dark min-vh-100 d-flex flex-column">
    <NavbarSection />
    <main class="flex-grow-1 d-flex align-items-center justify-content-center py-5 mt-5">
      <div class="container text-center">
        <div class="p-5 bg-white rounded-5 shadow-sm border border-light-subtle mx-auto" style="max-width: 600px;">
          <div class="mb-4">
             <i class="bi bi-whatsapp display-1 text-success"></i>
          </div>
          <h1 class="display-5 fw-bold text-dark mb-4">Start Your Journey</h1>
          <p class="lead text-secondary mb-5">To get started with LearnMS or schedule a demo, please contact our team via WhatsApp or direct call.</p>
          
          <div class="bg-light p-4 rounded-4 border border-success border-opacity-10 d-inline-block shadow-sm">
            <h2 class="display-6 fw-bold text-dark mb-0">
               <i class="bi bi-telephone-fill me-2 text-success" style="font-size: 1.5rem;"></i>
               +92 312 3456789
            </h2>
          </div>
          
          <div class="mt-5 pt-4 border-top">
            <div class="d-flex justify-content-center gap-3">
               <a href="tel:+923123456789" class="btn btn-outline-dark px-4 py-2 rounded-pill fw-bold">
                  Call Now
               </a>
               <a href="https://wa.me/923123456789" target="_blank" class="btn btn-success px-4 py-2 rounded-pill fw-bold">
                   Message WhatsApp
               </a>
            </div>
            <p class="small text-muted mt-4 mb-0">Our support team is available to assist you in setting up your workspace.</p>
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
