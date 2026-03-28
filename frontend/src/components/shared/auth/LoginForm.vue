<template>
  <form @submit.prevent="handleLogin" class="space-y-4">
    <AlertMessage v-if="error" type="error" :message="error" @close="error = ''" />

    <BaseInput v-model="form.username" type="email" label="Email" placeholder="Enter your email" required />

    <BaseInput v-model="form.password" type="password" label="Password" placeholder="Enter your password" required />

    <div class="d-flex justify-content-between align-items-center mb-4">
      <div class="form-check">
        <input v-model="form.remember" class="form-check-input" type="checkbox" id="rememberMe">
        <label class="form-check-label small" for="rememberMe">
          Remember me
        </label>
      </div>
      <router-link :to="{ name: 'ForgotPassword' }" class="text-decoration-none small fw-semibold">
        Forgot password?
      </router-link>
    </div>

    <BaseButton type="submit" label="Login" variant="primary" :loading="loading" :disabled="loading"
      loadingText="Signing in..." />
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuth } from '@/store/auth'
import { AlertMessage, BaseInput, BaseButton } from '@/components/shared/common'

const emit = defineEmits(['login-success', 'login-error'])

const authStore = useAuth()
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    error.value = 'Please fill in all fields'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const data = await authStore.login({
      username: form.username,
      password: form.password,
      remember: form.remember
    })

    // Emit success
    emit('login-success', data)
  } catch (err) {
    const message = err.response?.data?.error || 'Login failed. Please check your credentials.'
    error.value = message
    emit('login-error', message)
  } finally {
    loading.value = false
  }
}
</script>
