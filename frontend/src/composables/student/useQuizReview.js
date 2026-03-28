export function useQuizReview() {
  const formatMarks = (value) => {
    const num = Number(value || 0)
    return Number.isFinite(num) ? num.toFixed(2).replace(/\.00$/, '') : '0'
  }

  const getQuestionTypeLabel = (questionType) => {
    if (questionType === 'mcq') return 'Multiple choice'
    if (questionType === 'short_answer') return 'Short answer'
    if (questionType === 'essay') return 'Essay'
    return 'Question'
  }

  const normalizeAnswerText = (value, fallback = 'Not answered') => {
    const text = String(value ?? '').trim()
    return text || fallback
  }

  const getSelectedOptionText = (question) => {
    const selectedId = question?.user_answer?.selected_option
    if (!selectedId) return 'Not answered'

    const matched = (question.options || []).find((opt) => String(opt.id) === String(selectedId))
    return matched?.option_text || 'Not answered'
  }

  const getUserAnswerText = (question) => {
    if (question.question_type === 'mcq') {
      return getSelectedOptionText(question)
    }
    return normalizeAnswerText(question?.user_answer?.answer_text)
  }

  const getCorrectAnswerText = (question) => {
    if (question.question_type === 'mcq') {
      return normalizeAnswerText(question.correct_option_text, 'Not provided')
    }
    return normalizeAnswerText(question.correct_answer_text, 'Not provided')
  }

  const getReviewOptionClass = (question, optionId) => {
    const userAnswer = question.user_answer || {}
    const userSelected = String(userAnswer.selected_option || '') === String(optionId)
    const isCorrect = String(question.correct_option_id || '') === String(optionId)

    if (isCorrect) return 'is-correct'
    if (userSelected && !isCorrect) return 'is-wrong'
    return ''
  }

  return {
    formatMarks,
    getQuestionTypeLabel,
    getUserAnswerText,
    getCorrectAnswerText,
    getReviewOptionClass
  }
}
