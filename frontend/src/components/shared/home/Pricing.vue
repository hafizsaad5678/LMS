<template>
  <div class="homescreen-wrapper bg-light text-dark min-vh-100">
    <NavbarSection />
    <main class="pt-5 mt-5 pb-5">
      <div class="container text-center mb-5 mt-4">
        <h1 class="display-4 fw-bold text-dark mb-3">Simple, transparent pricing</h1>
        <p class="lead text-muted mx-auto" style="max-width: 600px;">Choose the perfect plan to accelerate your team's professional growth. No hidden fees, scalable to your needs.</p>
      </div>

      <div class="container mb-5">
        <div class="row justify-content-center">
          <div class="col-lg-10">
            <div class="row g-4 justify-content-center">
              <div class="col-md-4">
                <div class="card bg-white border h-100 p-4 shadow-sm" style="border-radius: 12px; border-color: #e2e8f0 !important;">
                  <h4 class="text-dark mb-3">Basic</h4>
                  <h2 class="text-dark fw-bold mb-4">$29<span class="fs-6 text-muted fw-normal">/user/mo</span></h2>
                  <p class="text-muted small mb-4">For individuals and small teams starting their learning journey.</p>
                  <ul class="list-unstyled text-start mb-4 flex-grow-1">
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Up to 50 active learners</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Core course builder</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Standard analytics dashboard</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Email support</li>
                  </ul>
                  <router-link to="/get-started" class="btn btn-light w-100 fw-semibold" style="background-color: #f1f5f9; color: #475569;">Get Started</router-link>
                </div>
              </div>
              <div class="col-md-4">
                <div class="card bg-white border border-dark border-2 shadow h-100 p-4 position-relative" style="border-radius: 12px;">
                  <span class="badge bg-dark text-white position-absolute top-0 start-50 translate-middle rounded-pill px-3" style="font-size: 0.75rem;">Most Popular</span>
                  <h4 class="text-dark mb-3 mt-1">Professional</h4>
                  <h2 class="text-dark fw-bold mb-4">$79<span class="fs-6 text-muted fw-normal">/user/mo</span></h2>
                  <p class="text-muted small mb-4">Advanced tools and reporting for growing organizations.</p>
                  <ul class="list-unstyled text-start mb-4 flex-grow-1">
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Up to 500 active learners</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Advanced assessments & quizzes</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Custom reporting & automated exports</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Priority 24/7 support</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> White-labeling options</li>
                  </ul>
                  <router-link to="/get-started" class="btn btn-dark w-100 fw-semibold" style="background-color: #0f172a;">Get Started</router-link>
                </div>
              </div>
              <div class="col-md-4">
                <div class="card bg-white border h-100 p-4 shadow-sm" style="border-radius: 12px; border-color: #e2e8f0 !important;">
                  <h4 class="text-dark mb-3">Enterprise</h4>
                  <h2 class="text-dark fw-bold mb-4">Custom</h2>
                  <p class="text-muted small mb-4">Maximum performance, security, and control for large scale.</p>
                  <ul class="list-unstyled text-start mb-4 flex-grow-1">
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Unlimited active learners</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Dedicated success manager</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> SSO & API access</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> Custom integrations</li>
                    <li class="mb-2 small fw-medium"><i class="bi bi-check-circle-fill text-dark me-2"></i> SLA guarantees</li>
                  </ul>
                  <router-link to="/get-started" class="btn btn-outline-dark w-100 fw-semibold" style="border-color: #94a3b8; color: #475569;">Contact Sales</router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Compare Features Section -->
      <div class="container text-center mt-5 pt-5 pb-4 border-top">
         <h3 class="fw-bold text-dark mb-5">Compare Features</h3>
         <div class="row justify-content-center">
            <div class="col-lg-10 text-start">
               <!-- Reduced complexity version of feature table matching styles visually -->
               <div class="table-responsive">
                 <table class="table table-borderless table-striped-columns align-middle" style="background: transparent;">
                   <thead>
                     <tr class="border-bottom border-dark border-3">
                       <th class="py-3 fs-5">Features</th>
                       <th class="py-3 fs-5 bg-white text-center">Basic</th>
                       <th class="py-3 fs-5 bg-light text-center border-start border-end" style="border-top: 3px solid #0f172a !important;">Professional</th>
                       <th class="py-3 fs-5 bg-white text-center">Enterprise</th>
                     </tr>
                   </thead>
                   <tbody class="text-muted small">
                     <tr><td colspan="4" class="fw-bold py-3 text-dark text-uppercase border-bottom" style="font-size: 0.70rem; letter-spacing: 0.05rem;">Core Capabilities</td></tr>
                     <tr class="border-bottom">
                       <td class="py-3">Learner Capacity</td>
                       <td class="text-center py-3">50</td>
                       <td class="text-center py-3 fw-bold text-dark bg-light border-start border-end">500</td>
                       <td class="text-center py-3">Unlimited</td>
                     </tr>
                     <tr class="border-bottom">
                       <td class="py-3">Course Builder</td>
                       <td class="text-center py-3"><i class="bi bi-check2 text-dark"></i></td>
                       <td class="text-center py-3 bg-light border-start border-end"><i class="bi bi-check2 text-dark"></i></td>
                       <td class="text-center py-3"><i class="bi bi-check2 text-dark"></i></td>
                     </tr>
                   </tbody>
                 </table>
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
