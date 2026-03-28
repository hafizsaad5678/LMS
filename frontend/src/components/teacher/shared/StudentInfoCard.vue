<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body p-4">
      <div class="row align-items-center">
        <div class="col-auto">
          <div class="profile-avatar profile-avatar-teacher">
            {{ studentInfo.name?.charAt(0)?.toUpperCase() || 'S' }}
          </div>
        </div>
        <div class="col">
          <h4 class="mb-1 fw-bold">{{ studentInfo.name || 'Student' }}</h4>
          <p class="text-muted mb-2">
            <i class="bi bi-hash me-1"></i>{{ studentInfo.roll_no || 'N/A' }}
          </p>
          <div class="d-flex flex-wrap gap-2">
            <span class="badge bg-info-light text-teacher px-3 py-2">
              <i class="bi bi-mortarboard me-1"></i>{{ studentInfo.program_name || 'N/A' }}
            </span>
            <span class="badge bg-success-light text-success px-3 py-2">
              <i class="bi bi-building me-1"></i>{{ studentInfo.department_name || 'N/A' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  studentInfo: {
    type: Object,
    required: true
  }
})
</script>
