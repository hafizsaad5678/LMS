<template>
  <div class="institution-faculty bg-white min-vh-100">
    <!-- Premium Hero Banner -->
    <div class="faculty-hero mb-0" :style="heroBgStyle">
      <div class="hero-overlay-dark"></div>
      <div class="container h-100">
        <div class="row h-100 align-items-center justify-content-center text-center position-relative z-1">
          <div class="col-lg-8" data-aos="fade-down">

            <h1 class="display-4 fw-bold mb-3 text-white title-font">Academic Leadership</h1>
            <div class="hero-line mx-auto mb-4"></div>
            <p class="lead text-white-50 mx-auto faculty-lead small">
              Meet our distinguished team of educators and industry experts dedicated to academic excellence and student success.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Faculty Directory Section (Per Screenshot) -->
    <div class="container py-5">
      <div class="directory-section mb-5" data-aos="fade-up">
        <div class="row g-5 align-items-start">
          <div class="col-lg-5">
            <div class="directory-image-box rounded-4 overflow-hidden shadow">
              <img src="@/assets/q.png" alt="Faculty" class="img-fluid w-100" />
            </div>
          </div>
          <div class="col-lg-7">
            <div class="directory-content">
              <div class="d-flex align-items-center gap-3 mb-4">
                <h2 class="directory-title text-brand-secondary mb-0">FACULTY DIRECTORY</h2>
                <div class="title-lines flex-grow-1">
                  <div class="line-1"></div>
                  <div class="line-2 mt-1"></div>
                </div>
              </div>
              
              <div class="department-links-grid">
                <div class="row g-3">
                  <div class="col-6 col-md-4" v-for="dept in departments" :key="dept.id">
                    <button 
                      @click="selectDepartment(dept.name)"
                      class="dept-link-btn w-100 text-start border-0 bg-transparent py-2 d-flex align-items-center gap-2"
                      :class="{ 'active': activeDeptFilter === dept.name }"
                    >
                      <i class="bi bi-arrow-right-short fs-4"></i>
                      <span class="dept-name-text">{{ dept.name }}</span>
                    </button>
                  </div>
                  <div class="col-12 mt-4">
                    <button 
                      @click="activeDeptFilter = null"
                      class="btn btn-sm btn-outline-secondary rounded-pill px-4"
                      v-if="activeDeptFilter"
                    >
                      Show All Faculty
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container pb-5">

      
      <!-- Faculty Grid -->
      <div id="faculty-grid" v-if="filteredFaculty && filteredFaculty.length > 0" class="row g-5 justify-content-center">
        <div 
          v-for="(teacher, index) in filteredFaculty" 
          :key="teacher.id" 
          class="col-12 col-sm-6 col-lg-4"
          data-aos="fade-up"
          :data-aos-delay="index * 50"
        >
          <!-- Modern Professional Card -->
          <div class="faculty-modern-card border-0 rounded-4 overflow-hidden shadow-hover">
            <div class="card-image-section position-relative">
              <div class="image-wrapper h-100">
                <img 
                  v-if="teacher.profile_image" 
                  :src="getFileUrl(teacher.profile_image)" 
                  :alt="teacher.full_name"
                  class="faculty-img"
                />
                <div v-else class="faculty-placeholder">
                  <i class="bi bi-person-fill"></i>
                </div>
              </div>
            </div>
            
            <div class="card-body p-4 text-center">
              <div class="mb-3">
                <!-- Department Badge moved here to avoid overlap -->
                <div class="dept-badge-inline mb-2">
                  <span class="badge rounded-pill dept-badge-custom small px-3">
                    Department of {{ teacher.department_name ? teacher.department_name.replace(/\bDepartment\b/gi, '').trim() : 'Faculty' }}
                  </span>
                </div>
                <h4 class="h5 fw-bold mb-1 name-text title-font text-dark">{{ teacher.full_name }}</h4>
                <div class="designation-pill d-inline-block px-3 py-1 rounded-pill small mb-2">
                  {{ teacher.designation || 'Lecturer' }}
                </div>
              </div>


            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-5 mt-5" data-aos="zoom-in">
        <div class="empty-state-icon mb-4 mx-auto shadow-sm">
          <i class="bi bi-person-slash text-brand"></i>
        </div>
        <h3 class="fw-bold text-dark mb-2">No results found</h3>
        <p class="text-secondary mx-auto mb-4 faculty-lead">
          We couldn't find any faculty member matching "{{ searchQuery }}".
        </p>
        <button @click="searchQuery = ''" class="btn btn-brand-primary rounded-pill px-5 py-3">
          Explore Full Directory
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getFileUrl } from '@/utils/constants/config'
import qImage from '@/assets/q.png'

const props = defineProps({
  faculty: {
    type: Array,
    default: () => []
  },
  departments: {
    type: Array,
    default: () => []
  }
})

const route = useRoute()
const searchQuery = ref('')
const activeDeptFilter = ref(null)

const selectDepartment = (deptName) => {
  activeDeptFilter.value = deptName
  document.getElementById('faculty-grid')?.scrollIntoView({ behavior: 'smooth' })
}

const departmentsCount = computed(() => {
  const depts = new Set(props.faculty.map(f => f.department_name).filter(Boolean))
  return depts.size || 1
})

const filteredFaculty = computed(() => {
  let list = props.faculty
  
  if (activeDeptFilter.value) {
    list = list.filter(f => f.department_name === activeDeptFilter.value)
  }

  if (!searchQuery.value) return list
  
  const query = searchQuery.value.toLowerCase().trim()
  return list.filter(teacher => 
    (teacher.full_name && teacher.full_name.toLowerCase().includes(query)) || 
    (teacher.department_name && teacher.department_name.toLowerCase().includes(query)) ||
    (teacher.designation && teacher.designation.toLowerCase().includes(query))
  )
})

const heroBgStyle = computed(() => ({
  backgroundImage: `url(${qImage})`
}))
</script>

<style scoped>
/* Styles migrated to custom.css */
</style>

