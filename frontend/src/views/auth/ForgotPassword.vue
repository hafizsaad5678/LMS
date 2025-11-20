<template>
  <div class="min-vh-100 bg-gradient-light d-flex align-items-center justify-content-center p-3">
    <div class="w-100" style="max-width: 900px;">
      <div class="card shadow-lg border-0 overflow-hidden">
        <div class="row g-0">
          <!-- Left Side - Form -->
          <div class="col-lg-6 p-5 p-lg-5">
            <div class="text-center text-lg-start mb-5">
              <h1 class="h3 fw-bold text-dark mb-2">College LMS</h1>
              <p class="text-muted">Learning Management System</p>
            </div>

            <!-- Forgot Password Form Component -->
            <ForgotPasswordForm 
              @forgot-password-success="handleForgotPasswordSuccess"
              @forgot-password-error="handleForgotPasswordError"
            />
          </div>

          <!-- Right Side - Illustration -->
          <div class="col-lg-6 bg-gradient-warning text-dark d-none d-lg-flex align-items-center justify-content-center p-5">
            <div class="text-center">
              <div class="display-1 mb-4">
                <i class="bi bi-key"></i>
              </div>
              <h2 class="h3 fw-bold mb-4">Forgot Password?</h2>
              <p class="lead">
                No worries! Enter your email address and we'll send you a link to reset your password.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ForgotPasswordForm from '@/components/auth/ForgotPasswordForm.vue'

export default {
  name: 'ForgotPassword',
  components: {
    ForgotPasswordForm
  },
  methods: {
    handleForgotPasswordSuccess(data) {
      console.log('Forgot password request successful:', data)
    },
    handleForgotPasswordError(error) {
      console.error('Forgot password error:', error)
    }
  }
}
</script>
