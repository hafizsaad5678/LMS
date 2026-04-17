<template>
  <BasePageTemplate
    :title="title"
    :subtitle="subtitle"
    :icon="icon"
    :breadcrumbs="breadcrumbs"
    :show-actions="showActions"
    :actions="actions"
    :show-content-card="showContentCard"
    :content-title="contentTitle"
    :content-class="contentClass"
    theme="admin"
    @action-click="$emit('action-click', $event)"
  >
    <template v-if="$slots.actions" #actions>
      <slot name="actions"></slot>
    </template>
    <template v-if="$slots.stats" #stats>
      <slot name="stats"></slot>
    </template>
    <template v-if="$slots.filters" #filters>
      <slot name="filters"></slot>
    </template>
    <template #default>
      <slot></slot>
    </template>
    <template v-if="$slots.footer && showFooter" #footer>
      <slot name="footer"></slot>
    </template>
  </BasePageTemplate>
</template>

<script setup>
import BasePageTemplate from '../layout/BasePageTemplate.vue'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: '' },
  breadcrumbs: { type: Array, default: () => [] },
  showActions: { type: Boolean, default: true },
  actions: { type: Array, default: () => [] },
  showContentCard: { type: Boolean, default: true },
  contentTitle: { type: String, default: '' },
  contentClass: { type: String, default: '' },
  showFooter: { type: Boolean, default: false }
})

defineEmits(['action-click'])
</script>

<!-- Theme styles moved to assets/css/components.css -->
