<template>
  <div class="home-container home-screen">
    <!-- Navbar Component -->
    <NavbarSection />

    <!-- Hero Component -->
    <HeroSection 
      :primaryActionLabel="primaryActionLabel"
      :primaryActionIcon="primaryActionIcon"
      @primary-action="goToPrimaryAction"
      @scroll-features="scrollTo('features')"
    />

    <!-- Features & Workflow -->
    <FeaturesSection />

    <!-- Role Cards & Testimonials -->
    <RoleCardsSection />
    
    <!-- Dynamic Stats Component -->
    <StatsSection />


    <!-- Contact & Real-time Feedback -->
    <ContactFeedbackSection />

    <!-- CTA Component -->
    <CTASection 
      @login="goToLogin"
      @signup="goToSignup"
    />

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
import CTASection from '@/components/shared/home/CTASection.vue'
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
const primaryActionLabel = computed(() => (isLoggedIn.value ? 'Go to Dashboard' : 'Get Started'))
const primaryActionIcon = computed(() => (isLoggedIn.value ? 'bi bi-speedometer2' : 'bi bi-rocket-fill'))

const goToLogin = () => navigateToLogin(router)
const goToSignup = () => router.push('/get-started')

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


