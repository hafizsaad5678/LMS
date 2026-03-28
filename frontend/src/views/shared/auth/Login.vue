<template>
  <div class="min-vh-100 bg-gradient-light d-flex align-items-center justify-content-center p-3">
    <div class="w-100 max-w-1200">
      <div class="card shadow-lg border-0 overflow-hidden">
        <div class="row g-0">
          <!-- Left Side - Form -->
          <div class="col-lg-6 p-5 p-lg-5">
            <div class="text-center text-lg-start mb-5">
              <h1 class="h3 fw-bold text-dark mb-2">College LMS</h1>
              <p class="text-muted">Learning Management System</p>
            </div>

            <!-- Login Form Component -->
            <LoginForm 
              @login-success="handleLoginSuccess"
              @login-error="handleLoginError"
            />
          </div>

          <!-- Right Side - Illustration -->
          <div class="col-lg-6 bg-gradient-primary text-white d-none d-lg-flex align-items-center justify-content-center p-5">
            <div class="text-center">
              <div class="display-1 mb-4">
                <i class="bi bi-mortarboard"></i>
              </div>
              <h2 class="h3 fw-bold mb-4">Welcome Back!</h2>
              <p class="lead">
                Continue your learning journey with our comprehensive Learning Management System. 
                Access your courses, assignments, and resources all in one place.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LoginForm from '@/components/shared/auth/LoginForm.vue'

export default {
  name: 'Login',
  components: {
    LoginForm
  },
  methods: {
    handleLoginSuccess(data) {
      // Auth store handles token storage and redirect
      if (import.meta.env.DEV) console.debug('Login successful - User role:', data.role)
    },
    handleLoginError(error) {
      console.error('Login error:', error)
    }
  }
}
</script>
