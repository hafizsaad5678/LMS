<template>
  <header class="navbar navbar-expand-lg bg-white sticky-top shadow-sm py-1">
    <div class="container">
      <div class="d-flex align-items-center gap-2">
        <div v-if="logoUrl" class="nav-logo-wrap">
          <img :src="logoUrl" :alt="`${institution.name} logo`" class="img-fluid nav-logo" />
        </div>
        <div class="d-flex flex-column text-dark nav-title-block">
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-light text-muted fw-normal border badge-govt" v-if="institution.type === 'government'">GOVT</span>
            <span class="fw-bold nav-name">{{ institution.name }}</span>
          </div>
          <span class="text-muted nav-subtitle">
            <span v-if="institution.established_year" class="fw-medium">ESTD {{ institution.established_year }}</span>
            <span v-if="institution.established_year && institution.city" class="mx-2 opacity-50">|</span>
            <span v-if="institution.city">{{ institution.city }}</span>
          </span>
        </div>
      </div>

      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#institutionNavbar" aria-controls="institutionNavbar" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse justify-content-end" id="institutionNavbar">
        <ul class="navbar-nav gap-1 gap-lg-2 mt-3 mt-lg-0 align-items-lg-center">
          <li class="nav-item">
            <router-link :to="`/i/${slug}`" class="nav-link fw-bold text-dark text-uppercase nav-hover-brand nav-link-custom" exact-active-class="active">HOME</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="`/i/${slug}/programs`" class="nav-link fw-bold text-dark text-uppercase nav-hover-brand nav-link-custom" active-class="active">COURSES</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="`/i/${slug}/faculty`" class="nav-link fw-bold text-dark text-uppercase nav-hover-brand nav-link-custom" active-class="active">FACULTY</router-link>
          </li>
          <li class="nav-item" v-if="institution.show_admissions">
            <router-link :to="`/i/${slug}/admissions`" class="nav-link fw-bold text-dark text-uppercase nav-hover-brand nav-link-custom" active-class="active">ADMISSIONS</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="`/i/${slug}/gallery`" class="nav-link fw-bold text-dark text-uppercase nav-hover-brand nav-link-custom" active-class="active">GALLERY</router-link>
          </li>
          <li class="nav-item ms-lg-2 mt-2 mt-lg-0">
            <router-link to="/login" class="btn btn-sm rounded-pill px-3 py-1 fw-bold text-white shadow-sm btn-login">Login</router-link>
          </li>
        </ul>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const slug = computed(() => route.params.slug)
defineProps({
  institution: {
    type: Object,
    required: true
  },
  logoUrl: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

