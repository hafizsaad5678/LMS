<template>
  <form @submit.prevent="handleSignup" class="space-y-4">
    <AlertMessage 
      v-if="error" 
      type="error" 
      :message="error"
      @close="error = ''"
    />

    <div class="row">
      <div class="col-md-6">
        <BaseInput
          v-model="form.first_name"
          type="text"
          label="First Name"
          placeholder="Enter first name"
          required
        />
      </div>
      <div class="col-md-6">
        <BaseInput
          v-model="form.last_name"
          type="text"
          label="Last Name"
          placeholder="Enter last name"
          required
        />
      </div>
    </div>

    <BaseInput
      v-model="form.email"
      type="email"
      label="Email"
      placeholder="Enter your email"
      required
    />

    <BaseInput
      v-model="form.password"
      type="password"
      label="Password"
      placeholder="Create password"
      required
    />

    <BaseButton
      type="submit"
      label="Create Student Account"
      variant="primary"
      :loading="loading"
      loadingText="Creating Account..."
    />

    <div class="text-center">
      <p class="text-muted small">
        Already have an account?
        <router-link to="/login" class="text-decoration-none fw-semibold">
          Sign in here
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
  name: 'SignupForm',
  components: {
    AlertMessage,
    BaseInput,
    BaseButton
  },
  emits: ['signup-success', 'signup-error'],
  data() {
    return {
      form: {
        first_name: '',
        last_name: '',
        email: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleSignup() {
      if (!this.form.first_name || !this.form.last_name || !this.form.email || !this.form.password) {
        this.error = 'Please fill in all fields'
        return
      }

      this.loading = true
      this.error = ''

      try {
        const response = await authAPI.signup(this.form)

        this.$emit('signup-success', response.data)
        this.$router.push('/login')

      } catch (err) {
        const errors = err.response?.data?.errors || err.response?.data
        let errorMessage = 'Registration failed'

        if (errors) {
          errorMessage = Object.values(errors).flat().join(', ')
        }

        this.error = errorMessage
        this.$emit('signup-error', errorMessage)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

