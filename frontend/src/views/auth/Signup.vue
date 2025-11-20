<template>
  <div class="min-vh-100 bg-gradient-light d-flex align-items-center justify-content-center p-3">
    <div class="w-100" style="max-width: 1000px;">
      <div class="card shadow-lg border-0 overflow-hidden">
        <div class="row g-0">
          <!-- Left Side - Form -->
          <div class="col-lg-6 p-5 p-lg-5">
            <div class="text-center text-lg-start mb-5">
              <h1 class="h3 fw-bold text-dark mb-2">College LMS</h1>
              <p class="text-muted">Learning Management System</p>
            </div>

            <!-- Signup Form Component -->
            <SignupForm 
              @signup-success="handleSignupSuccess"
              @signup-error="handleSignupError"
            />
          </div>

          <!-- Right Side - Illustration -->
          <div class="col-lg-6 bg-gradient-success text-white d-none d-lg-flex align-items-center justify-content-center p-5">
            <div class="text-center">
              <div class="display-1 mb-4">
                <i class="bi bi-person-check"></i>
              </div>
              <h2 class="h3 fw-bold mb-4">Join Us!</h2>
              <p class="lead">
                Create your student account and start your learning journey. Access courses, assignments, and resources all in one place.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SignupForm from '@/components/auth/SignupForm.vue'

export default {
  name: 'Signup',
  components: {
    SignupForm
  },
  methods: {
    handleSignupSuccess(data) {
      console.log('Signup successful:', data)
    },
    handleSignupError(error) {
      console.error('Signup error:', error)
    }
  }
}
</script>
