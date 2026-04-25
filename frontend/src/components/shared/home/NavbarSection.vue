<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white fixed-top border-bottom border-secondary shadow-sm home-nav">
    <div class="container">
      <router-link class="navbar-brand fw-bold fs-4 d-flex align-items-center text-dark" to="/">
        <i class="bi bi-hexagon-fill me-2" style="color: #0f172a;"></i><span style="color: #0f172a;">Learn</span>MS
      </router-link>
      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse justify-content-center" id="navbarNav">
        <ul class="navbar-nav mx-auto">
          <li v-for="link in navLinks" :key="link.path" class="nav-item">
            <router-link :class="['nav-link', 'home-nav-link']" active-class="active" :to="link.path">{{ link.label }}</router-link>
          </li>
        </ul>
        <div class="d-flex align-items-center">
          <template v-if="isLoggedIn">
            <div class="d-flex align-items-center gap-2 px-3 py-2 me-2 rounded-pill border border-secondary bg-light home-user-chip">
              <div class="rounded-circle bg-dark d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                <span class="small fw-bold text-white">{{ userInitial }}</span>
              </div>
              <span class="text-dark fw-medium">{{ userName }}</span>
            </div>
            <button @click="goToDashboard" class="btn btn-dark btn-sm px-4 rounded fw-semibold text-white" style="background-color: #0f172a;">
              <i class="bi bi-speedometer2 me-2"></i>Go to Dashboard
            </button>
          </template>
          <template v-else>
            <button @click="goToLogin" class="btn btn-link text-dark text-decoration-none fw-semibold me-3">
              Login
            </button>
            <button @click="goToSignup" class="btn btn-dark btn-sm px-4 py-2 rounded fw-semibold text-white border-0 shadow-sm" style="background-color: #0f172a;">
              Get Started
            </button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/auth'
import { navigateToLogin, navigateToSignup, navigateToDashboard } from '@/utils/navigation'

const router = useRouter()
const authStore = useAuth()

const navLinks = [
  { path: '/', label: 'Platform' },
  { path: '/capabilities', label: 'Capabilities' },
  { path: '/solutions', label: 'Solutions' },
  { path: '/pricing', label: 'Pricing' },
  { path: '/about', label: 'About Us' },
]

const isLoggedIn = computed(() => authStore.isAuthenticated)
const userName = computed(() => authStore.userName || authStore.user?.username || 'User')
const userRole = computed(() => authStore.user?.role || '')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())

const goToLogin = () => navigateToLogin(router)
const goToSignup = () => router.push('/get-started')

const goToDashboard = () => {
  if (userRole.value) {
    navigateToDashboard(router, userRole.value)
    return
  }
  goToLogin()
}
</script>