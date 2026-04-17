<template>
  <form @submit.prevent="handleForgotPassword" class="forgot-form">
    <div class="mb-4">
      <h2 class="h4 fw-bold text-dark mb-2">Reset your password</h2>
      <p class="text-muted mb-0 small">Enter your account email and we will send a secure reset link.</p>
    </div>

    <AlertMessage
      v-if="successMessage"
      type="success"
      :message="successMessage"
      @close="successMessage = ''"
    />

    <AlertMessage 
      v-if="error" 
      type="error" 
      :message="error"
      @close="error = ''"
    />

    <div class="mb-3">
      <BaseInput
        v-model="form.email"
        type="email"
        label="Email Address"
        placeholder="you@example.com"
        required
      />
    </div>

    <div class="info-chip mb-3">
      <i class="bi bi-info-circle me-2"></i>
      If this email is registered, you will receive reset instructions shortly.
    </div>

    <div class="d-grid mb-3">
      <BaseButton
        type="submit"
        label="Send Reset Link"
        variant="warning"
        :loading="loading"
        :disabled="loading"
        loadingText="Sending..."
      />
    </div>

    <div class="text-center">
      <router-link :to="{ name: 'Login' }" class="text-decoration-none fw-semibold small back-link">
        Back to Login
      </router-link>
    </div>
  </form>
</template>

<script>
import { authAPI } from '@/services/shared'
import { AlertMessage, BaseInput, BaseButton } from '@/components/shared/common'

export default {
  name: 'ForgotPasswordForm',
  components: {
    AlertMessage,
    BaseInput,
    BaseButton
  },
  emits: ['forgot-password-success', 'forgot-password-error'],
  data() {
    return {
      form: {
        email: ''
      },
      loading: false,
      error: '',
      successMessage: ''
    }
  },
  watch: {
    'form.email'() {
      if (this.error) this.error = ''
    }
  },
  methods: {
    async handleForgotPassword() {
      const normalizedEmail = String(this.form.email || '').trim().toLowerCase()

      if (!normalizedEmail) {
        this.error = 'Please enter your email'
        return
      }

      if (this.loading) return

      this.loading = true
      this.error = ''
      this.successMessage = ''

      try {
        const response = await authAPI.forgotPassword({ email: normalizedEmail })

        this.$emit('forgot-password-success', response.data)
        this.successMessage = response?.data?.message || 'If the email exists, a reset link has been sent.'
        this.form.email = normalizedEmail

      } catch (err) {
        const message = err.response?.data?.error || 'Failed to send reset email'
        this.error = message
        this.$emit('forgot-password-error', message)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>


