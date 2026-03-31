<template>
  <div>
    <AlertMessage 
      v-if="showAlert"
      type="warning"
      message="You are about to logout. Are you sure?"
      :show-confirm-button="true"
      @close="closeAlert"
      @confirm="logout"
    />
    <nav :class="['navbar navbar-expand-lg navbar-dark shadow-sm fixed-top lms-navbar', headerColor]">
      <div class="container-fluid">
        <!-- Mobile Sidebar Toggle -->
        <button 
          class="btn btn-link text-white d-lg-none me-2 p-0"
          @click="$emit('toggle-sidebar')"
          aria-label="Toggle sidebar"
        >
          <i class="bi bi-list fs-4"></i>
        </button>
        
        <a @click.prevent="goToDashboard" href="#" class="navbar-brand fw-bold d-flex align-items-center gap-2 text-decoration-none text-white" style="cursor: pointer;">
          <div class="bg-white rounded p-2 d-none d-sm-flex" style="width: 40px; height: 40px; align-items: center; justify-content: center;">
            <span class="fs-5">📚</span>
          </div>
          <span class="d-none d-sm-inline">College LMS</span>
          <span class="d-sm-none">LMS</span>
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <!-- Close button for mobile sidebar -->
          <button 
            class="btn btn-link text-white d-lg-none position-absolute mobile-nav-close"
            type="button"
            data-bs-toggle="collapse" 
            data-bs-target="#navbarNav"
            aria-label="Close menu"
          >
            <i class="bi bi-x-lg fs-4"></i>
          </button>
          
          <ul class="navbar-nav ms-auto d-flex align-items-center gap-2 lms-navbar-links">
            <li v-for="link in mainNav" :key="link.name" class="nav-item">
              <router-link :to="link.href" class="nav-link text-white lms-nav-link">{{ link.name }}</router-link>
            </li>
            <!-- User info - visible on all screens -->
            <li v-if="userName" class="nav-item d-flex align-items-center gap-2 nav-user-chip">
              <div class="rounded-circle bg-white d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                <span class="small fw-bold" :class="headerTextColor">{{ userName.charAt(0).toUpperCase() }}</span>
              </div>
              <button
                type="button"
                class="btn btn-link p-0 text-white fw-medium text-decoration-none nav-user-name-btn"
                :class="{ 'disabled pe-none opacity-100': isAdminUser }"
                @click="goToAccount"
                :title="isAdminUser ? 'Admin account' : 'Open my account'"
              >
                {{ userName }}
              </button>
            </li>
            <li class="nav-item">
              <button @click="handleLogoutClick" class="btn btn-outline-light btn-sm d-flex align-items-center gap-2 nav-logout-btn">
                <span>🚪</span>
                <span>Logout</span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/auth'
import { AlertMessage } from '@/components/shared/common'
import { navigateToLogin, navigateToDashboard, navigateToHome } from '@/utils/navigation'
import { ADMIN_ROUTES, TEACHER_ROUTES, STUDENT_ROUTES } from '@/utils/constants/routes'
import { USER_ROLES } from '@/utils/constants/config'

const authStore = useAuth()

defineProps({
  mainNav: {
    type: Array,
    default: () => []
  },
  userName: String,
  headerColor: {
    type: String,
    default: 'bg-primary'
  },
  headerTextColor: {
    type: String,
    default: 'text-primary'
  }
})

defineEmits(['toggle-sidebar'])

const router = useRouter()
const showAlert = ref(false)
const isAdminUser = computed(() => authStore.userRole === USER_ROLES.ADMIN)

const goToDashboard = () => {
  const userRole = authStore.user?.role
  if (userRole) {
    navigateToDashboard(router, userRole)
  } else {
    navigateToHome(router)
  }
}

const handleLogoutClick = () => {
  showAlert.value = true
}

const goToAccount = () => {
  if (isAdminUser.value) return
  if (authStore.userRole === USER_ROLES.TEACHER) {
    router.push({ name: TEACHER_ROUTES.ACCOUNT.name })
    return
  }
  if (authStore.userRole === USER_ROLES.STUDENT) {
    router.push({ name: STUDENT_ROUTES.ACCOUNT.name })
  }
}

const closeAlert = () => {
  showAlert.value = false
}

const logout = async () => {
  authStore.logout()
  navigateToLogin(router)
}
</script>


