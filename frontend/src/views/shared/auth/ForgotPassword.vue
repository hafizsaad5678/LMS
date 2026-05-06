<template>
  <div class="forgot-password-page min-vh-100 d-flex align-items-center justify-content-center py-5">
    <div class="w-100 max-w-900 mt-5">
      <div class="card shadow-lg border-0 overflow-hidden forgot-card">
        <div class="row g-0">
          <!-- Left Side - Form -->
          <div class="col-lg-6 p-4 p-lg-5">
            <div class="text-center text-lg-start mb-4 mb-lg-5">
              <div class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle mb-3 px-3 py-2 fw-semibold">
                Account Recovery
              </div>
              <h1 class="h3 fw-bold text-dark mb-2">LearnMS</h1>
              <p class="text-muted mb-0">Securely recover your account access in a few steps.</p>
            </div>

            <!-- Forgot Password Form Component -->
            <ForgotPasswordForm 
              @forgot-password-success="handleForgotPasswordSuccess"
              @forgot-password-error="handleForgotPasswordError"
            />
          </div>

          <!-- Right Side - Illustration -->
          <div class="col-lg-6 bg-gradient-warning text-dark d-none d-lg-flex align-items-center justify-content-center p-5 right-panel">
            <div class="text-center right-panel-content">
              <div class="display-1 mb-4 key-icon-wrap">
                <i class="bi bi-key"></i>
              </div>
              <h2 class="h3 fw-bold mb-4">Forgot Password?</h2>
              <p class="lead mb-4">
                No worries! Enter your email address and we'll send you a link to reset your password.
              </p>
              <div class="small fw-semibold opacity-75">
                <i class="bi bi-shield-check me-2"></i>
                Reset links expire for your account safety.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ForgotPasswordForm from '@/components/shared/auth/ForgotPasswordForm.vue'

export default {
  name: 'ForgotPassword',
  components: {
    ForgotPasswordForm
  },
  methods: {
    handleForgotPasswordSuccess(data) {
      if (import.meta.env.DEV) console.debug('Forgot password request successful:', data)
    },
    handleForgotPasswordError(error) {
      console.error('Forgot password error:', error)
    }
  }
}
</script>
