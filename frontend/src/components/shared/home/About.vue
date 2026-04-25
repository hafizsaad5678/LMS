<template>
  <div class="homescreen-wrapper bg-white text-dark min-vh-100">
    <NavbarSection />
    
    <main class="pt-5 mt-4">
      <!-- About Hero -->
      <section class="py-4 bg-light border-bottom">
        <div class="container py-4 text-center">
          <div class="col-lg-8 mx-auto">
            <span class="badge bg-primary-subtle text-primary mb-2 px-2 py-1 rounded-pill fw-bold" style="font-size: 0.7rem;">OUR MISSION</span>
            <h1 class="h2 fw-bold text-dark mb-3">Bridging Learning & Technology</h1>
            <p class="lead text-secondary mb-0 small">LearnMS is a state-of-the-art SaaS Learning Management System built to bridge the gap between traditional manual workflows and an AI-driven educational future.</p>
          </div>
        </div>
      </section>

      <!-- Mission & Story -->
      <section class="py-4">
        <div class="container py-3">
          <div class="row align-items-center g-4">
            <div class="col-lg-6">
              <h3 class="fw-bold text-dark mb-3">Our Vision</h3>
              <p class="text-secondary small lh-base mb-3">
                Our vision is to introduce advanced Artificial Intelligence directly into your classrooms. From automated quiz grading to a 24/7 support chatbot, we want to scale your institution's digital capabilities exponentially without adding administrative overhead.
              </p>
              <div class="row g-3">
                <div class="col-sm-6">
                  <div class="p-3 bg-light border border-light-subtle home-card-compact">
                    <i class="bi bi-cpu text-primary fs-4 mb-2 d-block"></i>
                    <h6 class="fw-bold text-dark small mb-1">AI-Assisted</h6>
                    <p class="text-secondary mb-0" style="font-size: 0.75rem;">Automated workflows for grading and insights.</p>
                  </div>
                </div>
                <div class="col-sm-6">
                  <div class="p-3 bg-light border border-light-subtle home-card-compact">
                    <i class="bi bi-layers text-primary fs-4 mb-2 d-block"></i>
                    <h6 class="fw-bold text-dark small mb-1">Multi-Tenant</h6>
                    <p class="text-secondary mb-0" style="font-size: 0.75rem;">Secure, isolated environments for every client.</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-lg-6">
              <div class="bg-light p-4 rounded-4 border shadow-sm position-relative overflow-hidden">
                <div class="position-absolute top-0 end-0 p-3 opacity-10">
                   <i class="bi bi-quote fs-1"></i>
                </div>
                <p class="h5 fw-medium text-dark lh-base mb-3 position-relative">
                  "At LearnMS, we believe that education should not be constrained by administrative friction. We build tools that let educators focus on teaching."
                </p>
                <div class="d-flex align-items-center">
                   <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3 shadow-sm" style="width: 40px; height: 40px;">
                      <span class="fw-bold small">HS</span>
                   </div>
                   <div>
                      <h6 class="mb-0 fw-bold small">HS Ansari</h6>
                      <small class="text-primary fw-semibold text-uppercase" style="font-size: 0.6rem; letter-spacing: 0.5px;">Founder & EdTech VP</small>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Team Section -->
      <section class="py-4 bg-light">
        <div class="container py-3">
          <div class="text-center mb-4">
            <h3 class="fw-bold text-dark">Leadership</h3>
            <p class="text-secondary small">Innovators shaping the future of educational infrastructure.</p>
          </div>
          <div class="row g-4 justify-content-center">
            <div class="col-md-5 col-lg-4">
              <div class="card border-0 shadow-sm h-100 bg-white overflow-hidden home-card-premium">
                <div class="p-4 text-center">
                  <div class="bg-warning text-dark rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3 shadow-sm home-avatar-ring" style="width:80px; height:80px;">
                    <h4 class="mb-0 fw-bold">HSA</h4>
                  </div>
                  <h5 class="fw-bold text-dark mb-1">HS Ansari</h5>
                  <p class="text-primary fw-bold text-uppercase mb-2" style="font-size: 0.65rem; letter-spacing: 0.7px;">Founder & EdTech VP</p>
                  <p class="text-secondary mb-3" style="font-size: 0.8rem;">Driving the strategic vision and AI integration across the entire LearnMS ecosystem.</p>
                  <div class="d-flex justify-content-center gap-3 mt-auto">
                    <a href="#" class="text-secondary hover-primary"><i class="bi bi-linkedin small"></i></a>
                    <a href="#" class="text-secondary hover-primary"><i class="bi bi-twitter-x small"></i></a>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-5 col-lg-4">
              <div class="card border-0 shadow-sm h-100 bg-white overflow-hidden home-card-premium">
                <div class="p-4 text-center">
                  <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3 shadow-sm home-avatar-ring" style="width:80px; height:80px;">
                    <h4 class="mb-0 fw-bold">VK</h4>
                  </div>
                  <h5 class="fw-bold text-dark mb-1">Vicky Kamran</h5>
                  <p class="text-primary fw-bold text-uppercase mb-2" style="font-size: 0.65rem; letter-spacing: 0.7px;">Operations Director</p>
                  <p class="text-secondary mb-3" style="font-size: 0.8rem;">Ensuring seamless multi-tenant delivery and operational excellence for global partners.</p>
                  <div class="d-flex justify-content-center gap-3 mt-auto">
                    <a href="#" class="text-secondary hover-primary"><i class="bi bi-linkedin small"></i></a>
                    <a href="#" class="text-secondary hover-primary"><i class="bi bi-twitter-x small"></i></a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
    
    <FooterSection />
  </div>
</template>

<script setup>
import NavbarSection from '@/components/shared/home/NavbarSection.vue'
import FooterSection from '@/components/shared/home/FooterSection.vue'
</script>
