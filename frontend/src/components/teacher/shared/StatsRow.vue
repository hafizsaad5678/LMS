<template>
  <div class="row g-4 mb-4">
    <div v-for="stat in stats" :key="stat.label" :class="stat.colClass || 'col-md-3'">
      <div class="stat-card" :class="stat.bgClass">
        <div class="stat-icon">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stat.value }}</h3>
          <p>{{ stat.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Array,
    required: true
  }
})
</script>
