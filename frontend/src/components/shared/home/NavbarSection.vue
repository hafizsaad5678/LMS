<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top border-bottom border-secondary shadow-sm home-nav">
    <div class="container">
      <a class="navbar-brand fw-bold fs-4 d-flex align-items-center" href="#hero">
        <i class="bi bi-hexagon-fill me-2 text-warning"></i><span class="text-warning">SaaS</span> Portal
      </a>
      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li v-for="link in navLinks" :key="link.id" class="nav-item">
            <a :class="['nav-link', 'home-nav-link', { active: link.id === 'hero' }]" :href="`#${link.id}`">{{ link.label }}</a>
          </li>
        </ul>
        <div class="d-flex align-items-center">
          <template v-if="isLoggedIn">
            <div class="d-flex align-items-center gap-2 px-3 py-2 me-2 rounded-pill border border-info-subtle bg-info bg-opacity-10 home-user-chip">
              <div class="rounded-circle bg-info d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                <span class="small fw-bold text-white">{{ userInitial }}</span>
              </div>
              <span class="text-white fw-medium">{{ userName }}</span>
            </div>
            <button @click="$emit('go-dashboard')" class="btn btn-info btn-sm px-4 rounded-pill fw-semibold">
              <i class="bi bi-speedometer2 me-2"></i>Workspace
            </button>
          </template>
          <template v-else>
            <button @click="$emit('go-login')" class="btn btn-outline-light btn-sm px-4 rounded-pill fw-semibold me-2">
              <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
            </button>
            <button @click="$emit('go-signup')" class="btn btn-info btn-sm px-4 rounded-pill fw-semibold border-0 bg-gradient text-dark shadow-sm">
              <i class="bi bi-person-plus-fill me-2"></i>Free Trial
            </button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
const props = defineProps({
  navLinks: { type: Array, required: true },
  isLoggedIn: { type: Boolean, required: true },
  userInitial: { type: String, default: 'U' },
  userName: { type: String, default: 'User' }
})

defineEmits(['go-dashboard', 'go-login', 'go-signup'])
</script>