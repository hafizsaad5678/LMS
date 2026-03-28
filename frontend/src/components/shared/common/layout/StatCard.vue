<template>
  <div
    class="card border-0 shadow-sm h-100 stat-card transition-all"
    :class="[isGlass ? glassClass : 'bg-white', clickable || role ? 'cursor-pointer' : '']"
    @click="$emit('click')"
  >
    <div class="card-body d-flex align-items-center p-3">
      <div
        class="stat-card-icon rounded-3 d-flex align-items-center justify-content-center me-3 flex-shrink-0"
        :class="[!isGlass ? effectiveIconBg : '']"
        style="width: 48px; height: 48px;"
      >
        <i :class="[icon, 'fs-5', !isGlass ? effectiveIconColor : '']"></i>
      </div>
      <div class="stat-content overflow-hidden">
        <p
          class="stat-card-title text-uppercase ls-1 fw-bold mb-1 small"
          :class="[!isGlass ? 'text-muted' : '']"
        >
          {{ title }}
        </p>
        <h3 class="fw-bold mb-0 text-truncate h4">
          {{ value || 0 }}
        </h3>
        <p v-if="change" class="small mt-1 mb-0" :class="isPositive ? 'text-success' : 'text-danger'">
          <i :class="isPositive ? 'bi bi-arrow-up' : 'bi bi-arrow-down'"></i> {{ change }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const THEMES = {
  admin: { bg: 'bg-admin-glass', iconColor: 'text-admin', iconBg: 'bg-admin-light' },
  teacher: { bg: 'bg-teacher-glass', iconColor: 'text-teacher', iconBg: 'bg-teacher-light' },
  student: { bg: 'bg-student-glass', iconColor: 'text-student', iconBg: 'bg-student-light' },
  course: { bg: 'bg-primary-glass', iconColor: 'text-primary', iconBg: 'bg-primary-light' },
  finance: { bg: 'bg-warning-glass', iconColor: 'text-warning', iconBg: 'bg-warning-light' },
  department: { bg: 'bg-info-glass', iconColor: 'text-info', iconBg: 'bg-info-light' }
}

const KEYWORD_MAPPINGS = [
  { keywords: ['student', 'enrollment'], type: 'student' },
  { keywords: ['teacher', 'faculty', 'staff'], type: 'teacher' },
  { keywords: ['fee', 'revenue', 'payment', 'due', 'cost', 'expense', 'amount', 'salary'], type: 'finance' },
  { keywords: ['department', 'schedule', 'timetable'], type: 'department' },
  { keywords: ['course', 'subject', 'program', 'class'], type: 'course' },
]

const props = defineProps({
  title: String,
  value: [String, Number],
  change: String,
  icon: String,
  role: String,
  type: String, 
  bgColor: { type: String, default: 'bg-primary-light' },
  iconColor: { type: String, default: 'text-primary' },
  variant: { type: String, default: 'standard' },
  glassBgClass: { type: String, default: 'bg-primary' },
  isPositive: { type: Boolean, default: true },
  clickable: { type: Boolean, default: false }
})

// Auto-detect type based on title if not provided
const inferredType = computed(() => {
  if (props.type) return props.type
  if (!props.title) return null
  
  const lowerTitle = props.title.toLowerCase()
  const match = KEYWORD_MAPPINGS.find(m => m.keywords.some(k => lowerTitle.includes(k)))
  return match ? match.type : null
})

// GLASS MODE: Only if explicitly requested via variant='glass' OR if role is provided (legacy dashboard support)
// We DO NOT force glass mode just because we inferred a type.
const isGlass = computed(() => props.role || props.variant === 'glass')

const theme = computed(() => {
  const activeType = inferredType.value
  if (activeType && THEMES[activeType]) return THEMES[activeType]
  if (props.role && THEMES[props.role]) return THEMES[props.role]
  return null
})

const glassClass = computed(() => {
  if (theme.value) return theme.value.bg
  return props.glassBgClass
})

// Compute effective icon color class
const effectiveIconColor = computed(() => {
  // If we have a theme, ALWAYS use the theme's icon color, even in standard mode
  if (theme.value) return theme.value.iconColor
  
  if (!isGlass.value) return props.iconColor
  return props.iconColor
})

// Compute effective icon background class (for standard mode)
const effectiveIconBg = computed(() => {
  if (isGlass.value) return '' // Glass mode handles its own icon bg via CSS
  
  // If we have a theme, use the theme's light background
  if (theme.value && theme.value.iconBg) return theme.value.iconBg
  
  return props.bgColor
})
</script>
