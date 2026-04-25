<template>
  <div class="homescreen-wrapper home-bg-light text-dark min-vh-100">
    <NavbarSection />
    <main class="pt-5 mt-4">
      <!-- Capabilities Hero with Background Image -->
      <section class="position-relative py-5 overflow-hidden home-capability-hero">
        <!-- Background Image with Blur & Overlay -->
        <div class="position-absolute top-0 start-0 w-100 h-100" 
             :style="{ 
               backgroundImage: `url(${usingLms})`, 
               backgroundSize: 'cover', 
               backgroundPosition: 'center',
               filter: 'blur(5px) brightness(0.4)' 
             }">
        </div>
        
        <div class="container position-relative z-1 text-center py-4">
          <div class="col-lg-8 mx-auto">
            <span class="badge bg-warning text-dark mb-3 px-3 py-2 rounded-pill fw-bold" style="font-size: 0.7rem; letter-spacing: 1px;">ADVANCED TOOLS</span>
            <h1 class="display-5 fw-bold text-white mb-3">Powerful Capabilities for Modern Learning</h1>
            <p class="lead text-white-50 mx-auto" style="max-width: 700px; font-size: 1.1rem;">Discover the advanced tools and workflows designed to empower educators, engage students, and streamline administrative tasks.</p>
          </div>
        </div>
      </section>

      <div class="container mb-5 mt-5">
        <div class="row g-4">
          <!-- Role-based secure access -->
          <div class="col-lg-7 d-flex">
            <div class="card bg-white border border-light-subtle h-100 p-4 shadow-sm w-100 home-card-compact">
              <div class="mb-4">
                <span class="d-inline-flex align-items-center justify-content-center bg-white border shadow-sm text-primary rounded" style="width: 40px; height: 40px;">
                  <i class="bi bi-shield-lock-fill fs-5"></i>
                </span>
              </div>
              <h4 class="text-dark fw-bold mb-3">Role-based Secure Access</h4>
              <p class="text-secondary mb-4 small lh-lg">Granular control over who sees what. Define custom roles for administrators, instructors, teaching assistants, and students to ensure data privacy and operational integrity.</p>
              
              <div class="bg-light p-3 rounded d-flex gap-3 align-items-center mt-auto border border-light-subtle w-100">
                <div class="bg-white p-3 rounded shadow-sm w-50 border border-light-subtle">
                  <div class="d-flex align-items-center gap-2 mb-3">
                    <i class="bi bi-person-fill text-secondary"></i>
                    <span class="fw-bold small text-dark">Student</span>
                  </div>
                  <div class="bg-secondary bg-opacity-10 rounded w-100 mb-2" style="height: 4px;"></div>
                  <div class="bg-secondary bg-opacity-10 rounded w-50" style="height: 4px;"></div>
                </div>
                <div class="bg-white p-3 rounded shadow-sm w-50 border border-primary">
                  <div class="d-flex align-items-center gap-2 mb-3">
                    <i class="bi bi-person-badge-fill text-primary"></i>
                    <span class="fw-bold small text-dark">Instructor</span>
                  </div>
                  <div class="bg-primary rounded w-100 mb-2" style="height: 4px;"></div>
                  <div class="bg-primary rounded w-75" style="height: 4px;"></div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Automated Workflows -->
          <div class="col-lg-5 d-flex">
            <div class="card bg-white border border-light-subtle h-100 p-4 shadow-sm w-100 home-card-compact">
              <div class="mb-4">
                <span class="d-inline-flex align-items-center justify-content-center bg-white border shadow-sm text-danger rounded" style="width: 40px; height: 40px;">
                  <i class="bi bi-diagram-3-fill fs-5"></i>
                </span>
              </div>
              <h4 class="text-dark fw-bold mb-3">Automated Workflows</h4>
              <p class="text-secondary mb-4 small lh-lg">Reduce administrative burden. Automate enrollment, grading notifications, and course progressions based on triggers.</p>
              
              <div class="mt-auto px-1">
                <div class="bg-light p-3 rounded mb-0 d-flex align-items-center border border-light-subtle shadow-sm">
                  <i class="bi bi-check-circle-fill text-danger me-2"></i>
                  <span class="small fw-bold text-dark">Assignment Submitted</span>
                </div>
                <!-- Connector Line -->
                <div class="ms-4 border-start border-secondary opacity-50 py-2" style="width: 1px; height: 1.5rem;"></div>
                <!-- Big Red Box -->
                <div class="bg-danger text-white p-3 rounded d-flex align-items-center shadow-sm" style="min-height: 50px;">
                  <!-- Red box is empty in image except perhaps faint text/design -->
                  <i class="bi bi-envelope-fill me-2 opacity-50"></i>
                  <span class="small fw-bold opacity-75">Notify Instructor</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Real-time Insights -->
          <div class="col-lg-4 d-flex">
            <div class="card bg-white border border-light-subtle h-100 p-4 shadow-sm w-100 home-card-compact">
              <div class="mb-4">
                <span class="d-inline-flex align-items-center justify-content-center bg-white border shadow-sm text-success rounded" style="width: 40px; height: 40px;">
                  <i class="bi bi-graph-up-arrow fs-5"></i>
                </span>
              </div>
              <h4 class="text-dark fw-bold mb-3">Real-time Insights</h4>
              <p class="text-secondary small mb-4 lh-lg">Track student engagement and performance instantly. Identify at-risk learners before they fall behind.</p>
              <div class="bg-light p-3 rounded d-flex align-items-end justify-content-between mt-auto border border-light-subtle shadow-inner" style="height: 100px;">
                <div class="bg-success rounded-top w-100 mx-1" style="height: 40%; opacity: 0.6;"></div>
                <div class="bg-success rounded-top w-100 mx-1" style="height: 70%; opacity: 0.8;"></div>
                <div class="bg-success rounded-top w-100 mx-1" style="height: 30%; opacity: 0.5;"></div>
                <div class="bg-success rounded-top w-100 mx-1" style="height: 90%; opacity: 1;"></div>
                <div class="bg-success rounded-top w-100 mx-1" style="height: 55%; opacity: 0.7;"></div>
              </div>
            </div>
          </div>
          
          <!-- Unified Communication -->
          <div class="col-lg-8 d-flex">
            <div class="card bg-white border border-light-subtle h-100 p-4 shadow-sm overflow-hidden position-relative w-100 home-card-compact">
              <div class="row h-100 align-items-center">
                <div class="col-md-6 z-1">
                  <div class="mb-4">
                    <span class="d-inline-flex align-items-center justify-content-center bg-white border shadow-sm text-info rounded" style="width: 40px; height: 40px;">
                      <i class="bi bi-chat-dots-fill fs-5" style="color: #6366f1;"></i>
                    </span>
                  </div>
                  <h4 class="text-dark fw-bold mb-3">Unified Communication</h4>
                  <p class="text-secondary small mb-4 lh-lg">Connect seamlessly through integrated messaging, discussion boards, and video conferencing. Keep all learning interactions centralized within the platform.</p>
                  <a href="#" class="text-dark fw-bold text-decoration-none small">Explore Communication <i class="bi bi-arrow-right ms-1"></i></a>
                </div>
                <div class="col-md-6 position-relative h-100 d-flex align-items-center justify-content-end">
                  <div class="bg-light p-4 rounded-start position-absolute end-0 border border-light-subtle shadow-sm flex-grow-1" style="width: 110%; right: -1.5rem;">
                    <div class="bg-white p-2 rounded shadow-sm w-75 mb-3 border border-light-subtle">
                       <div class="bg-secondary bg-opacity-10 rounded w-100 mb-1" style="height: 6px;"></div>
                       <div class="bg-secondary bg-opacity-10 rounded w-75" style="height: 6px;"></div>
                    </div>
                    <div class="bg-primary bg-opacity-10 p-2 rounded shadow-sm w-75 ms-auto mb-3 border border-primary border-opacity-25" style="background-color: #eef2ff !important; border-color: #c7d2fe !important;">
                       <div class="bg-primary bg-opacity-50 rounded w-100 mb-1" style="height: 6px;"></div>
                       <div class="bg-primary bg-opacity-50 rounded w-50" style="height: 6px;"></div>
                    </div>
                    <div class="bg-white p-2 rounded shadow-sm w-75 border border-light-subtle">
                       <div class="bg-secondary bg-opacity-10 rounded w-100 mb-1" style="height: 6px;"></div>
                       <div class="bg-secondary bg-opacity-10 rounded w-50" style="height: 6px;"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          

          <!-- Platform Showcase -->
          <div class="col-lg-8 mx-auto mt-4">
             <div class="text-center mb-4">
                <h3 class="fw-bold text-dark h4">Platform in Action</h3>
                <p class="text-secondary small">Real-world capture of the LearnMS multi-tenant dashboard.</p>
             </div>
             <div class="bg-white p-2 border shadow-sm overflow-hidden home-card-premium">
                <img :src="usingLms" alt="LearnMS Platform in Action" class="img-fluid rounded-3 border w-100">
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
import usingLms from '@/assets/usinglms.png'
</script>
