<template>
  <form @submit.prevent="handleLogin" class="space-y-4">
    <AlertMessage 
      v-if="error" 
      type="error" 
      :message="error"
      @close="error = ''"
    />

    <BaseInput
      v-model="form.username"
      type="email"
      label="Email"
      placeholder="Enter your email"
      required
    />

    <BaseInput
      v-model="form.password"
      type="password"
      label="Password"
      placeholder="Enter your password"
      required
    />

    <div class="d-flex justify-content-between align-items-center mb-4">
      <div class="form-check">
        <input 
          v-model="form.remember" 
          class="form-check-input" 
          type="checkbox" 
          id="rememberMe"
        >
        <label class="form-check-label small" for="rememberMe">
          Remember me
        </label>
      </div>
      <router-link to="/forgot-password" class="text-decoration-none small fw-semibold">
        Forgot password?
      </router-link>
    </div>

    <BaseButton
      type="submit"
      label="Login"
      variant="primary"
      :loading="loading"
      loadingText="Signing in..."
    />

    <div class="text-center">
      <p class="text-muted small">
        Don't have an account? 
        <router-link to="/signup" class="text-decoration-none fw-semibold">
          Sign up here
        </router-link>
      </p>
    </div>
  </form>
</template>

<script>
import { authAPI } from '@/services/api'
import AlertMessage from '@/components/common/AlertMessage.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

export default {
  name: 'LoginForm',
  components: {
    AlertMessage,
    BaseInput,
    BaseButton
  },
  emits: ['login-success', 'login-error'],
  data() {
    return {
      form: {
        username: '',
        password: '',
        remember: false
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      if (!this.form.username || !this.form.password) {
        this.error = 'Please fill in all fields'
        return
      }

      this.loading = true
      this.error = ''
      
      try {
        const response = await authAPI.login(this.form)
        
        console.log(response)
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        localStorage.setItem('userRole', response.data.role)
        localStorage.setItem('username', response.data.username)
        
        // Emit success with full response data
        this.$emit('login-success', {
          role: response.data.role,
          data: response.data
        })
      } catch (err) {
        const message = err.response?.data?.error || 'Login failed. Please check your credentials.'
        this.error = message
        this.$emit('login-error', message)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

