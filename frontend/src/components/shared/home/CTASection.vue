<template>
  <section id="about" class="py-5 bg-white">
    <div class="container py-4">
      <div class="p-5 rounded-5 shadow-lg position-relative overflow-hidden home-cta-box" 
           style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
        <!-- Background Orbs -->
        <div class="position-absolute top-0 end-0 bg-warning opacity-10 rounded-circle" style="width: 200px; height: 200px; filter: blur(80px); margin-top: -100px; margin-right: -100px;"></div>
        <div class="position-absolute bottom-0 start-0 bg-primary opacity-10 rounded-circle" style="width: 150px; height: 150px; filter: blur(60px); margin-bottom: -75px; margin-left: -75px;"></div>
        
        <div class="row align-items-center g-4 position-relative z-1">
          <div class="col-lg-7 text-center text-lg-start">
            <span class="badge bg-warning text-dark mb-3 px-3 py-2 rounded-pill fw-bold" style="font-size: 0.75rem; letter-spacing: 0.5px;">READY TO SCALE?</span>
            <h3 class="display-5 fw-bold mb-3 text-white">Join 500+ Institutions Building the Future</h3>
            <p class="lead mb-0 text-white opacity-75" style="max-width: 550px;">
              Deploy secure, multi-tenant learning environments in minutes. Reach out to our team to transform your digital infrastructure.
            </p>
          </div>
          <div class="col-lg-5 text-center text-lg-end">
            <div class="d-flex flex-column flex-sm-row gap-3 justify-content-lg-end align-items-center">
              <button @click="$emit('login')" class="btn btn-outline-light px-5 py-3 rounded-pill fw-bold transition-all hover-lift">
                Member Sign In
              </button>
              <button @click="$emit('signup')" class="btn btn-warning px-5 py-3 rounded-pill fw-bold text-dark shadow-lg transition-all hover-scale" style="background-color: #facc15; border: none;">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineEmits(['login', 'signup'])
</script>
