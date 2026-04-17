<template>
  <div class="card border-0 shadow-sm h-100 info-card">
    <div class="card-header bg-white border-bottom">
      <h6 class="mb-0 fw-semibold">
        <i :class="[icon, 'me-2', iconColorClass]"></i>{{ title }}
      </h6>
    </div>
    <div class="card-body">
      <div v-for="(item, index) in items" :key="index" :class="['info-row', { 'info-row-multiline': shouldUseMultiline(item) }]">
        <span class="info-label">{{ item.label }}</span>
        <span class="info-value" :class="item.class">
          <a v-if="item.href" :href="item.href">{{ formatTextValue(item.value) }}</a>
          <span v-else-if="shouldRenderAsHtml(item)" v-html="sanitizeHtml(item.value)"></span>
          <span v-else :class="{ 'text-capitalize': item.capitalize }">{{ formatTextValue(item.value) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: 'bi bi-info-circle'
  },
  iconColor: {
    type: String,
    default: 'admin'
  },
  items: {
    type: Array,
    required: true,
    validator: (value) => value.every(item => 'label' in item)
  }
})

const iconColorClass = computed(() => {
  const colorMap = {
    admin: 'text-admin',
    teacher: 'text-teacher',
    student: 'text-student',
    success: 'text-success',
    info: 'text-info',
    warning: 'text-warning',
    danger: 'text-danger'
  }
  return colorMap[props.iconColor] || 'text-admin'
})

const shouldUseMultiline = (item) => {
  if (!item) return false
  if (item.multiline) return true

  const label = String(item.label || '').trim().toLowerCase()
  const value = String(item.value || '').trim()
  const longText = value.length > 70 || value.includes('\n')
  const likelyMultilineLabel = ['description', 'vision', 'mission', 'address', 'notes', 'bio'].some((key) => label.includes(key))

  return longText && likelyMultilineLabel
}

const formatTextValue = (value) => {
  if (value === null || value === undefined || value === '') return 'N/A'
  return String(value)
}

const shouldRenderAsHtml = (item) => {
  if (!item || item.href) return false
  if (item.renderHtml === false) return false
  if (item.renderHtml === true) return true

  const value = String(item.value || '').trim()
  if (!value) return false

  // Auto-detect simple HTML content from rich-text fields.
  return /<\/?[a-z][\s\S]*>/i.test(value)
}

const sanitizeHtml = (value) => {
  if (value === null || value === undefined || value === '') return 'N/A'
  let clean = String(value)
  clean = clean.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gim, '')
  clean = clean.replace(/ on\w+="[^"]*"/g, '')
  clean = clean.replace(/ on\w+='[^']*'/g, '')
  clean = clean.replace(/javascript:/gim, '')
  return clean
}
</script>
