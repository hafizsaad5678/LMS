<template>
  <div class="card question-card border-0 shadow-sm rounded-4">
    <div class="card-body p-4">
      <!-- Question Header -->
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div class="d-flex align-items-center gap-3">
          <div class="question-number">{{ index + 1 }}</div>
          <span :class="['type-badge', question.type === 'mcq' ? 'type-mcq' : 'type-answer']">
            {{ question.type === 'mcq' ? 'Multiple Choice' : 'Short Answer' }}
          </span>
        </div>
        <button class="btn btn-link text-danger p-1 ms-2" title="Remove" @click="$emit('remove')">
          <i class="bi bi-trash"></i>
        </button>
      </div>

      <!-- Question Text Editor -->
      <div class="mb-4">
        <label class="form-label fw-bold small text-muted">QUESTION TEXT</label>
        <RichTextEditor v-model="question.text" placeholder="Enter your question here..." min-height="100px" />
      </div>

      <!-- Options for MCQ -->
      <div v-if="question.type === 'mcq'" class="mb-4">
        <label class="form-label fw-bold small text-muted">OPTIONS & CORRECT ANSWER</label>
        <div class="d-flex flex-column gap-2">
          <div v-for="(opt, oIndex) in question.options" :key="oIndex" class="option-input-group d-flex align-items-center gap-3">
            <input type="radio" :name="'correct-' + question.tempId" class="option-radio form-check-input" :checked="opt.isCorrect" @change="setCorrectOption(oIndex)">
            <input v-model="opt.text" type="text" class="form-control border-0 bg-transparent py-2" placeholder="Option text...">
            <button v-if="question.options.length > 2" class="btn btn-link text-danger p-0" @click="removeOption(oIndex)">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>
        <button class="btn btn-add-option mt-2" @click="addOption">
          <i class="bi bi-plus-circle"></i> Add Option
        </button>
      </div>

      <!-- Correct Answer for Short Answer -->
      <div v-if="question.type === 'short_answer'" class="mb-4">
        <label class="form-label fw-bold small text-muted">CORRECT ANSWER KEY</label>
        <input v-model="question.correctAnswer" type="text" class="form-control rounded-3 p-3 bg-light border-0" placeholder="The exact answer expected (not case sensitive)...">
      </div>

      <!-- Marks & Explanation -->
      <div class="row g-3">
        <div class="col-md-3">
          <label class="form-label fw-bold small text-muted">MARKS</label>
          <input v-model.number="question.marks" type="number" class="form-control rounded-3" min="1">
        </div>
        <div class="col-md-9">
          <label class="form-label fw-bold small text-muted">EXPLANATION (OPTIONAL)</label>
          <input v-model="question.explanation" type="text" class="form-control rounded-3" placeholder="Explain why the answer is correct...">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RichTextEditor } from '@/components/shared/common'

const props = defineProps({
  question: { type: Object, required: true },
  index: { type: Number, required: true }
})

defineEmits(['remove'])

const setCorrectOption = (oIndex) => {
  props.question.options.forEach((opt, idx) => { opt.isCorrect = idx === oIndex })
}

const addOption = () => {
  props.question.options.push({ text: '', isCorrect: false })
}

const removeOption = (oIndex) => {
  props.question.options.splice(oIndex, 1)
  if (!props.question.options.some(o => o.isCorrect)) {
    props.question.options[0].isCorrect = true
  }
}
</script>
