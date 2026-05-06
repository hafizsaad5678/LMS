<template>
  <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden position-relative admission-card-hover-popup">
    <!-- Accent Bar -->
    <div 
      class="position-absolute top-0 start-0 w-100" 
      :style="{ height: '4px', backgroundColor: isClosed ? '#6c757d' : 'var(--brand, var(--admin-primary, #0d6efd))' }"
    ></div>
    
    <div class="card-body p-4 d-flex flex-column h-100" :class="{ 'opacity-75': isClosed }">
      <!-- Badges Row -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <!-- Main Status Badge (Unified Style) -->
        <template v-if="isClosed">
          <span class="badge rounded-pill bg-secondary text-white px-3 py-2 small fw-bold shadow-sm">
            <i class="bi bi-x-circle-fill me-1"></i> Admission Closed
          </span>
        </template>
        <template v-else>
          <span 
            class="badge rounded-pill px-3 py-2 small fw-bold shadow-sm"
            style="background-color: var(--brand, var(--admin-primary, #0d6efd)); color: #ffffff;"
          >
            <i class="bi bi-stars text-warning me-1"></i> {{ item.badge_text || 'Admissions Open' }}
          </span>
        </template>

        <!-- Secondary Tag (Top Right) -->
        <span v-if="type === 'promo'" class="badge bg-light text-brand border px-2 py-1 small rounded-3 fw-semibold">
          Featured
        </span>
        <span v-else class="badge bg-light text-dark border px-2 py-1 small rounded-3 fw-semibold">
          {{ formatLevel(item.program_level) }}
        </span>
      </div>
      
      <!-- Title & Subtitle -->
      <h5 class="fw-bold mb-2">{{ item.name || item.title }}</h5>
      <p class="small text-brand fw-medium mb-3">
        <i :class="type === 'promo' ? 'bi bi-award' : 'bi bi-building'" class="me-1"></i>
        {{ type === 'promo' ? 'Special Program' : item.department_name }}
      </p>
      
      <!-- Description -->
      <div 
        v-if="item.description" 
        v-html="item.description" 
        class="text-secondary small mb-3 line-clamp-2"
      ></div>
      <p v-else class="text-secondary small mb-3 line-clamp-2">
        {{ type === 'promo' ? 'Apply now for this special program.' : `Enroll in the ${item.name} program to build a strong academic foundation.` }}
      </p>
      
      <!-- Media Actions -->
      <div v-if="hasImage" class="mb-3 d-flex flex-wrap gap-2">
        <button 
          @click="$emit('preview', item.image || item.cover_image)" 
          class="btn btn-sm btn-outline-brand rounded-pill px-3 flex-grow-1" 
          :disabled="isClosed"
        >
          <i class="bi bi-image me-1"></i> See Ad
        </button>
        <button 
          @click="$emit('download', item.image || item.cover_image, item.name || item.title)" 
          class="btn btn-sm btn-outline-secondary rounded-pill px-3 flex-grow-1" 
        >
          <i class="bi bi-download me-1"></i> Download
        </button>
      </div>
      
      <!-- Footer Info -->
      <div class="mt-auto pt-3 border-top mb-4">
        <p class="small text-muted mb-0">
          <template v-if="type === 'promo'">
            <i class="bi bi-info-circle me-2"></i>
            <template v-if="item.admission_start_date && item.admission_end_date">
               <strong>Timeline:</strong> {{ formatDate(item.admission_start_date) }} - {{ formatDate(item.admission_end_date) }}
            </template>
            <template v-else>
               <strong>Status:</strong> {{ isClosed ? 'Admission Closed' : 'Open for Registration' }}
            </template>
          </template>
          <template v-else>
            <i class="bi bi-calendar-event me-2"></i>
            <strong>Deadline:</strong> {{ deadline }}
          </template>
        </p>
      </div>
      
      <!-- Action Button -->
      <button 
        v-if="!isClosed"
        @click="$emit('apply', item)" 
        class="btn btn-brand rounded-pill px-4 py-2 fw-bold w-100 shadow-sm text-center"
        data-bs-toggle="modal" 
        data-bs-target="#applyModal"
      >
        Apply Now <i class="bi bi-arrow-right ms-1"></i>
      </button>
      <button 
        v-else
        class="btn btn-secondary rounded-pill px-4 py-2 fw-bold w-100 shadow-sm text-center opacity-75"
        disabled
      >
        Admission Closed <i class="bi bi-lock-fill ms-1"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    default: 'program' // 'promo' or 'program'
  },
  deadline: {
    type: String,
    default: 'TBA'
  },
  isClosed: {
    type: Boolean,
    default: false
  }
})

defineEmits(['apply', 'preview', 'download'])

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const hasImage = computed(() => {
  const img = props.item.image || props.item.cover_image
  if (!img) return false
  if (typeof img === 'string' && (img === 'null' || img === 'undefined' || img.trim() === '')) return false
  return true
})

const formatLevel = (level) => {
  if (!level) return 'Degree'
  const labels = {
    'bachelor': 'Bachelor (BS)',
    'master': 'Master (MS)',
    'phd': 'Doctorate (PhD)',
    'intermediate': 'Intermediate',
    'diploma': 'Diploma'
  }
  return labels[level.toLowerCase()] || level.charAt(0).toUpperCase() + level.slice(1)
}
</script>

<style scoped>
.text-brand {
  color: var(--brand, var(--admin-primary, #0d6efd)) !important;
}
.btn-brand {
  background-color: var(--brand, var(--admin-primary, #0d6efd));
  color: #ffffff;
  border: none;
}
.btn-brand:hover {
  filter: brightness(0.9);
  color: #ffffff;
}
.btn-outline-brand {
  color: var(--brand, var(--admin-primary, #0d6efd));
  border-color: var(--brand, var(--admin-primary, #0d6efd));
  background-color: transparent;
}
.btn-outline-brand:hover {
  background-color: var(--brand, var(--admin-primary, #0d6efd));
  color: #ffffff;
}
.admission-card-hover-popup {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.admission-card-hover-popup:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;  
  overflow: hidden;
}
</style>
