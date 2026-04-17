<template>
  <form @submit.prevent="handleLogin" class="login-form">
    <div class="mb-4">
      <h2 class="h4 fw-bold text-dark mb-2">Sign in to your account</h2>
      <p class="text-muted small mb-0">Use your registered email and password.</p>
    </div>

    <AlertMessage v-if="error" type="error" :message="error" @close="error = ''" />

    <div class="mb-3">
      <BaseInput v-model="form.username" type="email" label="Email" placeholder="Enter your email" required />
    </div>

    <div class="mb-3">
      <BaseInput v-model="form.password" type="password" label="Password" placeholder="Enter your password" required />
    </div>

    <div class="d-flex justify-content-between align-items-center mb-4">
      <div class="form-check">
        <input v-model="form.remember" class="form-check-input" type="checkbox" id="rememberMe">
        <label class="form-check-label small" for="rememberMe">
          Remember me
        </label>
      </div>
      <router-link :to="{ name: 'ForgotPassword' }" class="text-decoration-none small fw-semibold login-forgot-link">
        Forgot password?
      </router-link>
    </div>

    <div class="login-assist-text mb-3">
      <i class="bi bi-info-circle me-2"></i>
      Use the Forgot password option if you cannot access your account.
    </div>

    <div class="d-grid">
      <BaseButton type="submit" label="Login" variant="primary" :loading="loading" :disabled="loading"
        loadingText="Signing in..." />
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuth } from '@/store/auth'
import { AlertMessage, BaseInput, BaseButton } from '@/components/shared/common'
import { safeStorage } from '@/utils/security'
import { STORAGE_KEYS } from '@/utils/constants/storage'

const emit = defineEmits(['login-success', 'login-error'])

const authStore = useAuth()
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: '',
  remember: false
})

onMounted(() => {
  const savedEmail = safeStorage.get(STORAGE_KEYS.USER_EMAIL)
  const savedUsername = safeStorage.get(STORAGE_KEYS.USERNAME)
  const prefillValue = savedEmail || savedUsername || ''

  if (prefillValue) {
    form.username = prefillValue
    form.remember = true
  }
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
