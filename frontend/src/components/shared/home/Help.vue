<template>
  <div class="homescreen-wrapper bg-light text-dark min-vh-100">
    <NavbarSection />
    <main class="pt-5 mt-5 pb-5">
      <div class="container text-center mb-5">
        <h1 class="display-4 fw-bold text-primary">Help Center</h1>
        <p class="lead text-secondary">Frequently Asked Questions</p>
      </div>

      <div class="container mb-5" style="max-width: 800px;">
        <div class="accordion accordion-flush" id="faqAccordion">
          <div class="accordion-item bg-white border-light-subtle">
            <h2 class="accordion-header">
              <button class="accordion-button bg-white text-primary border-light-subtle collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne">
                Login kaise kare?
              </button>
            </h2>
            <div id="collapseOne" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
              <div class="accordion-body text-secondary">
                Top right corner me 'Login' button par click kare. Apna email aur password enter karke dashboard access kare.
              </div>
            </div>
          </div>
          <div class="accordion-item bg-white border-light-subtle">
            <h2 class="accordion-header">
              <button class="accordion-button bg-white text-primary border-light-subtle collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo">
                Quiz kaise attempt kare?
              </button>
            </h2>
            <div id="collapseTwo" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
              <div class="accordion-body text-secondary">
                Student dashboard me jao, apne course section me 'Assignments' par click karo aur quiz start karo.
              </div>
            </div>
          </div>
          <div class="accordion-item bg-white border-light-subtle">
            <h2 class="accordion-header">
              <button class="accordion-button bg-white text-primary border-light-subtle collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree">
                Teacher course kaise upload kare?
              </button>
            </h2>
            <div id="collapseThree" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
              <div class="accordion-body text-secondary">
                Teacher portal me 'Courses' tab par jao, 'Add New' par click karo, aur drag-and-drop feature use karke PDFs or videos attach karo.
              </div>
            </div>
          </div>
          <div class="accordion-item bg-white border-light-subtle">
            <h2 class="accordion-header">
              <button class="accordion-button bg-white text-primary border-light-subtle collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFour">
                Chatbot ka use kaise kare?
              </button>
            </h2>
            <div id="collapseFour" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
              <div class="accordion-body text-secondary">
                Bottom right corner pe chat icon diya gaya hai. Uspe click karo aur apna sawaal type karo 24/7 answers ke liye.
              </div>
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
