import { computed, onMounted, onUnmounted, ref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'

export function useQuizSessionGuards({ showReviewMode, submitting, flushAllSaves, showError, onAutoSubmit, requestLeaveConfirmation }) {
  const timeRemaining = ref(0)
  const warningFiveMinuteShown = ref(false)
  const warningOneMinuteShown = ref(false)
  let timer = null

  const formattedTime = computed(() => {
    const total = Math.max(timeRemaining.value, 0)
    const hours = Math.floor(total / 3600)
    const minutes = Math.floor((total % 3600) / 60)
    const seconds = total % 60

    if (hours > 0) {
      return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
    }
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  })

  const timerVariantClass = computed(() => {
    if (timeRemaining.value <= 60) return 'is-danger'
    if (timeRemaining.value <= 300) return 'is-warning'
    return 'is-safe'
  })

  const stopTimer = () => {
    if (!timer) return
    clearInterval(timer)
    timer = null
  }

  const setTimeRemaining = (seconds) => {
    timeRemaining.value = Number(seconds || 0)
    warningFiveMinuteShown.value = false
    warningOneMinuteShown.value = false
  }

  const startTimer = () => {
    stopTimer()

    timer = setInterval(() => {
      if (timeRemaining.value > 0) {
        timeRemaining.value -= 1

        if (timeRemaining.value <= 300 && !warningFiveMinuteShown.value) {
          warningFiveMinuteShown.value = true
          showError('Only 5 minutes remaining for this quiz.', 'Time Warning')
        }

        if (timeRemaining.value <= 60 && !warningOneMinuteShown.value) {
          warningOneMinuteShown.value = true
          showError('Only 1 minute left. Quiz will auto-submit.', 'Final Warning')
        }

        return
      }

      stopTimer()
      if (!submitting.value && !showReviewMode.value) {
        onAutoSubmit()
      }
    }, 1000)
  }

  const beforeUnloadHandler = (event) => {
    if (showReviewMode.value) return
    event.preventDefault()
    event.returnValue = ''
  }

  onBeforeRouteLeave(async (to, from, next) => {
    if (showReviewMode.value) {
      next()
      return
    }

    const proceed = typeof requestLeaveConfirmation === 'function'
      ? await requestLeaveConfirmation()
      : window.confirm('Quiz is in progress. Leave page? Your answers are saved but timer will continue.')

    if (!proceed) {
      next(false)
      return
    }

    try {
      await flushAllSaves()
    } finally {
      next()
    }
  })

  onMounted(() => {
    window.addEventListener('beforeunload', beforeUnloadHandler)
  })

  onUnmounted(() => {
    window.removeEventListener('beforeunload', beforeUnloadHandler)
    stopTimer()
  })

  return {
    timeRemaining,
    formattedTime,
    timerVariantClass,
    setTimeRemaining,
    startTimer,
    stopTimer
  }
}
