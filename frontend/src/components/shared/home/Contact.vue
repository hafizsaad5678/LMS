<template>
  <div class="homescreen-wrapper bg-light text-dark min-vh-100">
    <NavbarSection />
    <main class="pt-5 mt-5 pb-5">
      <ContactFeedbackSection />
    </main>
    <FooterSection />
  </div>
</template>

<script setup>
import NavbarSection from '@/components/shared/home/NavbarSection.vue'
import FooterSection from '@/components/shared/home/FooterSection.vue'
import ContactFeedbackSection from '@/components/shared/home/ContactFeedbackSection.vue'
</script>
