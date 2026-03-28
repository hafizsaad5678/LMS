<template>
  <div class="quiz-palette card border-0 shadow-sm">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0 fw-bold">Question Palette</h6>
        <span class="badge bg-warning-subtle text-warning-emphasis">Flagged: {{ flaggedCount }}</span>
      </div>

      <div class="quiz-palette-grid">
        <button
          v-for="(question, index) in questions"
          :key="question.id"
          type="button"
          class="btn quiz-palette-btn"
          :class="getButtonClass(question.id, index)"
          @click="$emit('jump', index)"
        >
          {{ index + 1 }}
          <i v-if="getState(question.id).is_flagged" class="bi bi-flag-fill quiz-flag-dot"></i>
        </button>
      </div>

      <div class="quiz-palette-legend mt-3">
        <small class="d-block"><span class="legend-box not-visited"></span>Not Visited</small>
        <small class="d-block"><span class="legend-box visited"></span>Visited</small>
        <small class="d-block"><span class="legend-box answered"></span>Answered</small>
        <small class="d-block"><span class="legend-box flagged"></span>Flagged marker</small>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  questions: {
    type: Array,
    default: () => []
  },
  currentIndex: {
    type: Number,
    default: 0
  },
  states: {
    type: Object,
    default: () => ({})
  },
  flaggedCount: {
    type: Number,
    default: 0
  }
})

defineEmits(['jump'])

const getState = (questionId) => {
  return props.states[String(questionId)] || { status: 'not_visited', is_flagged: false }
}

const getButtonClass = (questionId, index) => {
  if (index === props.currentIndex) return 'is-current'

  const state = getState(questionId)
  if (state.status === 'answered') return 'is-answered'
  if (state.status === 'visited') return 'is-visited'
  return 'is-not-visited'
}
</script>
