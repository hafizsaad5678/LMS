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
    <nav :class="['navbar navbar-expand-lg navbar-dark shadow-sm fixed-top', headerColor]">
      <div class="container-fluid">
        <router-link to="/" class="navbar-brand fw-bold d-flex align-items-center gap-2 text-decoration-none text-white">
          <div class="bg-white rounded p-2" style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
            <span class="fs-5">📚</span>
          </div>
          <span>College LMS</span>
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto d-flex align-items-center gap-3">
            <li v-for="link in mainNav" :key="link.name" class="nav-item">
              <router-link :to="link.href" class="nav-link text-white">{{ link.name }}</router-link>
            </li>
            <li v-if="userName" class="nav-item d-none d-md-flex align-items-center gap-2 px-3 py-2" style="background-color: rgba(255, 255, 255, 0.2); border-radius: 8px;">
              <div class="rounded-circle bg-white d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                <span class="small fw-bold" :class="headerTextColor">{{ userName.charAt(0).toUpperCase() }}</span>
              </div>
              <span class="text-white fw-medium">{{ userName }}</span>
            </li>
            <li class="nav-item">
              <button @click="handleLogoutClick" class="btn btn-outline-light btn-sm d-flex align-items-center gap-2">
                <span>🚪</span>
                <span class="d-none d-md-inline">Logout</span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AlertMessage from '../common/AlertMessage.vue'

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

const router = useRouter()
const showAlert = ref(false)

const handleLogoutClick = () => {
  showAlert.value = true
}

const closeAlert = () => {
  showAlert.value = false
}

const logout = async () => {
  // Clear all auth data from localStorage
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('username')
  localStorage.removeItem('userRole')
  
  // Redirect to login
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  transition: all 0.3s ease;
}

.navbar-brand {
  font-size: 1.25rem;
  letter-spacing: 0.5px;
}

.nav-link {
  transition: all 0.3s ease;
  position: relative;
}

.nav-link:hover {
  opacity: 0.8;
}

.btn-outline-light:hover {
  background-color: rgba(255, 255, 255, 0.2);
}
</style>
