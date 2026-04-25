<template>
  <div class="min-vh-100 bg-gradient-light d-flex align-items-center justify-content-center p-3">
    <div class="w-100 max-w-900">
      <div class="card shadow-lg border-0 overflow-hidden">
        <div class="row g-0">
          <!-- Left Side - Form -->
          <div class="col-lg-6 p-5 p-lg-5">
            <div class="text-center text-lg-start mb-5">
              <h1 class="h3 fw-bold text-dark mb-2">LearnMS</h1>
              <p class="text-muted">Learning Management System</p>
            </div>

            <!-- Reset Password Form Component -->
            <ResetPasswordForm 
              :uidb64="uidb64"
              :token="token"
              @reset-password-success="handleResetPasswordSuccess"
              @reset-password-error="handleResetPasswordError"
            />
          </div>

          <!-- Right Side - Illustration -->
          <div class="col-lg-6 bg-gradient-success text-white d-none d-lg-flex align-items-center justify-content-center p-5">
            <div class="text-center">
              <div class="display-1 mb-4">
                <i class="bi bi-shield-check"></i>
              </div>
              <h2 class="h3 fw-bold mb-4">Secure Password</h2>
              <p class="lead">
                Create a strong new password to secure your account. Make sure it's unique and difficult to guess.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ResetPasswordForm from '@/components/shared/auth/ResetPasswordForm.vue'

export default {
  name: 'ResetPassword',
  components: {
    ResetPasswordForm
  },
  computed: {
    uidb64() {
      return this.$route.params.uidb64
    },
    token() {
      return this.$route.params.token
    }
  },
  methods: {
    handleResetPasswordSuccess(data) {
      if (import.meta.env.DEV) console.debug('Password reset successful:', data)
    },
    handleResetPasswordError(error) {
      console.error('Password reset error:', error)
    }
  }
}
</script>
