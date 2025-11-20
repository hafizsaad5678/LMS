<template>
  <form @submit.prevent="handleForgotPassword" class="space-y-4">
    <AlertMessage 
      v-if="error" 
      type="error" 
      :message="error"
      @close="error = ''"
    />

    <BaseInput
      v-model="form.email"
      type="email"
      label="Email Address"
      placeholder="Enter your email"
      required
    />

    <BaseButton
      type="submit"
      label="Send Reset Link"
      variant="warning"
      :loading="loading"
      loadingText="Sending..."
    />

    <div class="text-center">
      <router-link to="/login" class="text-decoration-none fw-semibold small">
        Back to Login
      </router-link>
    </div>
  </form>
</template>

<script>
import { authAPI } from '@/services/api'
import AlertMessage from '@/components/common/AlertMessage.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

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
      error: ''
    }
  },
  methods: {
    async handleForgotPassword() {
      if (!this.form.email) {
        this.error = 'Please enter your email'
        return
      }

      this.loading = true
      this.error = ''

      try {
        const response = await authAPI.forgotPassword(this.form)

        this.$emit('forgot-password-success', response.data)
        this.$router.push('/login')

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

