<template>
  <div class="not-found-container d-flex align-items-center justify-content-center min-vh-100 bg-light">
    <div class="text-center">
      <h1 class="display-1 fw-bold text-muted">404</h1>
      <h2 class="mb-3">Page Not Found</h2>
      <p class="text-muted mb-4">The page you're looking for doesn't exist or has been moved.</p>
      <button @click="goBack" class="btn btn-primary me-2">
        <i class="bi bi-arrow-left me-2"></i>Go Back
      </button>
      <router-link :to="{ name: 'Home' }" class="btn btn-outline-secondary">
        <i class="bi bi-house me-2"></i>Home
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const goBack = () => router.go(-1)
</script>
