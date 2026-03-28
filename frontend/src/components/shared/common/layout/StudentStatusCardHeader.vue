<template>
  <div class="student-status-card-header p-4" :class="headerClass">
    <div class="d-flex justify-content-between align-items-start mb-3">
      <slot name="icon">
        <div class="student-status-icon">
          <i :class="iconClass"></i>
        </div>
      </slot>

      <slot name="badges">
        <span class="badge rounded-pill" :class="badgeClass">
          {{ badgeText }}
        </span>
      </slot>
    </div>

    <h5 class="student-status-title mt-3 mb-1 fw-bold" :class="titleClass">
      <slot name="title" />
    </h5>

    <p class="student-status-subtitle mb-0 small" :class="subtitleClass">
      <slot name="subtitle" />
    </p>
  </div>
</template>

<script setup>
defineProps({
  headerClass: { type: [String, Array, Object], default: '' },
  iconClass: { type: [String, Array, Object], default: 'bi bi-card-text' },
  badgeClass: { type: [String, Array, Object], default: 'bg-secondary text-white' },
  badgeText: { type: String, default: '' },
  titleClass: { type: [String, Array, Object], default: 'text-dark' },
  subtitleClass: { type: [String, Array, Object], default: 'text-muted' }
})
</script>