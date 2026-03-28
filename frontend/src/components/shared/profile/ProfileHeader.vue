<template>
  <div class="card border-0 shadow-sm mb-4">
    <div class="card-body p-4">
      <div class="row align-items-center">
        <div class="col-auto">
          <div :class="['profile-avatar', avatarClass]">
            {{ avatarInitial }}
          </div>
        </div>
        <div class="col">
          <h3 class="mb-1 fw-bold">{{ name }}</h3>
          <p class="text-muted mb-2">
            <i class="bi bi-hash me-1"></i>{{ identifier }}
          </p>
          <div class="d-flex flex-wrap gap-2">
            <span :class="['badge', isActive ? 'bg-success' : 'bg-warning']">
              {{ isActive ? 'Active' : 'Inactive' }}
            </span>
            <span v-for="(badge, index) in badges" :key="index" :class="['badge', badge.class || 'bg-info']">
              {{ badge.text }}
            </span>
          </div>
        </div>
        <div v-if="showEditButton" class="col-auto">
          <button @click="$emit('edit')" :class="['btn', editButtonClass]">
            <i class="bi bi-pencil me-2"></i>Edit Profile
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  identifier: {
    type: String,
    required: true
  },
  isActive: {
    type: Boolean,
    default: true
  },
  badges: {
    type: Array,
    default: () => []
  },
  theme: {
    type: String,
    default: 'admin',
    validator: (value) => ['admin', 'teacher', 'student'].includes(value)
  },
  showEditButton: {
    type: Boolean,
    default: true
  }
})

defineEmits(['edit'])

const avatarInitial = computed(() => {
  return props.name?.charAt(0)?.toUpperCase() || '?'
})

const avatarClass = computed(() => {
  const themeMap = {
    admin: 'profile-avatar-admin',
    teacher: 'profile-avatar-teacher',
    student: 'profile-avatar-student'
  }
  return themeMap[props.theme] || 'profile-avatar-admin'
})

const editButtonClass = computed(() => {
  const themeMap = {
    admin: 'btn-admin-primary',
    teacher: 'btn-teacher-primary',
    student: 'btn-student-primary'
  }
  return themeMap[props.theme] || 'btn-admin-primary'
})
</script>
