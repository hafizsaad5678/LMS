<template>
  <form @submit.prevent="handleResetPassword" class="space-y-4 bg-warning-subtle p-4 rounded">
    <AlertMessage 
      v-if="error" 
      type="error" 
      :message="error"
      @close="error = ''"
    />

    <BaseInput
      v-model="form.password"
      type="password"
      label="New Password"
      placeholder="Enter new password"
      required
    />
    <BaseInput
        v-model="form.confirmPassword"
        type="password"
        label="Confirm Password"
        placeholder="Re-enter password"
        required
      />

    <BaseButton
      type="submit"
      label="Reset Password"
      variant="warning"
      :loading="loading"
      loadingText="Resetting..."
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
  name: 'ResetPasswordForm',
  components: {
    AlertMessage,
    BaseInput,
    BaseButton
  },
  emits: ['reset-password-success', 'reset-password-error'],
  props: {
    uidb64: {
      type: String,
      required: true
    },
    token: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      form: {
        password: '',
        confirmPassword: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleResetPassword() {
      if (!this.form.password) {
        this.error = 'Please enter a new password'
        return
      }
      if (this.form.password !== this.form.confirmPassword) {
        this.error = 'Passwords do not match'
        return
      }

      this.loading = true
      this.error = ''

      try {
        const response = await authAPI.resetPassword(this.uidb64, this.token, this.form)

        this.$emit('reset-password-success', response.data)
        this.$router.push('/login')

      } catch (err) {
        const message = err.response?.data?.error || 'Failed to reset password'
        this.error = message
        this.$emit('reset-password-error', message)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

