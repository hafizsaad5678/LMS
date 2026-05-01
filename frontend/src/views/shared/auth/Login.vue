<template>
  <div class="login-page min-vh-100 d-flex align-items-center justify-content-center py-3 mt-1">
    <div class="w-100 max-w-1200">
      <div class="card shadow-lg border-0 overflow-hidden login-card">
        <div class="row g-0">
          <!-- Left Side - Form -->
          <div class="col-lg-6 p-4 p-lg-5">
            <div class="text-center text-lg-start mb-4 mb-lg-5">
              <div class="badge bg-primary-subtle text-primary-emphasis border border-primary-subtle mb-3 px-3 py-2 fw-semibold">
                Account Access
              </div>
              <h1 class="h3 fw-bold text-dark mb-2">LearnMS</h1>
              <p class="text-muted mb-0">Sign in to continue your classes and coursework.</p>
            </div>

            <!-- Login Form Component -->
            <LoginForm 
              @login-success="handleLoginSuccess"
              @login-error="handleLoginError"
            />
          </div>

          <!-- Right Side - Illustration -->
          <div class="col-lg-6 text-white d-none d-lg-flex align-items-center justify-content-center p-5 login-hero-panel">
            <div class="text-center login-hero-content">
              <div class="display-1 mb-4 login-hero-icon">
                <i class="bi bi-mortarboard"></i>
              </div>
              <h2 class="h3 fw-bold mb-4">Welcome Back!</h2>
              <p class="lead mb-4">
                Continue your learning journey with our comprehensive Learning Management System. 
                Access your courses, assignments, and resources all in one place.
              </p>
              <div class="small fw-semibold opacity-75">
                <i class="bi bi-shield-lock me-2"></i>
                Your session is protected with secure authentication.
              </div>
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
