<template>
  <div class="homescreen-wrapper bg-light text-dark min-vh-100">
    <NavbarSection />
    <main class="pt-5 mt-5 pb-5">
      <div class="container text-center mb-5">
        <h1 class="display-4 fw-bold text-primary">Vertical Solutions</h1>
        <p class="lead text-secondary">Tailored LMS implementations for every scale</p>
      </div>

      <div class="container">
        <div class="row g-5">
          <div class="col-lg-6">
            <div class="p-4 border border-light-subtle rounded bg-white h-100">
              <h3 class="text-primary mb-3">University Use Case</h3>
              <p class="text-secondary"><strong>Problem:</strong> Managing thousands of enrollments, diverse departments, and heavy manual grading loads.</p>
              <p class="text-secondary"><strong>Solution:</strong> Automated course blueprints, single sign-on (SSO), and AI bulk grading assessments.</p>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="p-4 border border-light-subtle rounded bg-white h-100">
              <h3 class="text-info mb-3">School Use Case</h3>
              <p class="text-secondary"><strong>Problem:</strong> Lack of parent visibility, disconnected parent-teacher communication, and unengaging materials.</p>
              <p class="text-secondary"><strong>Solution:</strong> Real-time progress trackers, interactive AI tools, and seamless announcement hubs.</p>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="p-4 border border-light-subtle rounded bg-white h-100">
              <h3 class="text-success mb-3">Coaching Center Use Case</h3>
              <p class="text-secondary"><strong>Problem:</strong> High administrative costs, lack of premium test creation capabilities.</p>
              <p class="text-secondary"><strong>Solution:</strong> Instantly generated quizzes, automated billing portals, and deep performance analytics.</p>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="p-4 border border-light-subtle rounded bg-white h-100">
              <h3 class="text-danger mb-3">Self-Learning Use Case</h3>
              <p class="text-secondary"><strong>Problem:</strong> Stalled motivation, missing direct mentor feedback, and rigid curriculum.</p>
              <p class="text-secondary"><strong>Solution:</strong> 24/7 AI chatbot assistant, personalized learning pathways, and adaptive quizzes.</p>
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
