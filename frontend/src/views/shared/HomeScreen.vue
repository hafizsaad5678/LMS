<template>
  <div class="home-container home-screen">
    <!-- Navbar Component -->
    <NavbarSection 
      :navLinks="navLinks"
      :isLoggedIn="isLoggedIn"
      :userInitial="userInitial"
      :userName="userName"
      @go-dashboard="goToDashboard"
      @go-login="goToLogin"
      @go-signup="goToSignup"
    />

    <!-- Hero Component -->
    <HeroSection 
      :primaryActionLabel="primaryActionLabel"
      :primaryActionIcon="primaryActionIcon"
      @primary-action="goToPrimaryAction"
      @scroll-features="scrollTo('features')"
    />

    <!-- Dynamic Stats Component -->
    <StatsSection />

    <!-- Features & Workflow -->
    <FeaturesSection />

    <!-- Role Cards & Testimonials -->
    <RoleCardsSection />

    <!-- Contact & Real-time Feedback -->
    <ContactFeedbackSection />

    <!-- CTA Section -->
    <section id="about" class="py-5 bg-dark bg-gradient border-top border-secondary home-cta">
      <div class="container">
        <div class="row align-items-center g-4">
          <div class="col-lg-8">
            <h3 class="display-5 fw-bold mb-3 text-white">Scale Your Infrastructure Today</h3>
            <p class="lead text-white mb-0 opacity-75">
              Deploy secure, multi-tenant learning environments in minutes using our SaaS architecture.
            </p>
          </div>
          <div class="col-lg-4 text-lg-end">
            <div class="d-flex flex-column flex-md-row gap-3 justify-content-lg-end">
              <button @click="goToLogin" class="btn btn-outline-light btn-lg px-4 rounded-pill fw-semibold shadow">
                <i class="bi bi-person-fill-check me-2"></i>Sign In
              </button>
              <button @click="goToSignup" class="btn btn-warning btn-lg px-4 rounded-pill fw-semibold">
                <i class="bi bi-arrow-right-circle-fill me-2"></i>Start Free Trial
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer Component -->
    <FooterSection />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/auth'
import { navigateToLogin, navigateToSignup, navigateToDashboard } from '@/utils/navigation'

// Components
import NavbarSection from '@/components/shared/home/NavbarSection.vue'
import HeroSection from '@/components/shared/home/HeroSection.vue'
import StatsSection from '@/components/shared/home/StatsSection.vue'
import FeaturesSection from '@/components/shared/home/FeaturesSection.vue'
import RoleCardsSection from '@/components/shared/home/RoleCardsSection.vue'
import ContactFeedbackSection from '@/components/shared/home/ContactFeedbackSection.vue'
import FooterSection from '@/components/shared/home/FooterSection.vue'

const router = useRouter()
const authStore = useAuth()

const navLinks = [
  { id: 'hero', label: 'Platform' },
  { id: 'features', label: 'Capabilities' },
  { id: 'workflow', label: 'Solutions' },
  { id: 'users', label: 'Customers' },
  { id: 'contact', label: 'Contact Sales' },
]

const isLoggedIn = computed(() => authStore.isAuthenticated)
const userName = computed(() => authStore.userName || authStore.user?.username || 'User')
const userRole = computed(() => authStore.user?.role || '')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())
const primaryActionLabel = computed(() => (isLoggedIn.value ? 'Open Workspace' : 'Start Trial'))
const primaryActionIcon = computed(() => (isLoggedIn.value ? 'bi bi-speedometer2' : 'bi bi-rocket-fill'))

const goToLogin = () => navigateToLogin(router)
const goToSignup = () => navigateToSignup(router)

const goToDashboard = () => {
  if (userRole.value) {
    navigateToDashboard(router, userRole.value)
    return
  }
  goToLogin()
}

const goToPrimaryAction = () => {
  if (isLoggedIn.value) {
    goToDashboard()
    return
  }
  goToSignup()
}

const scrollTo = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>


