import { computed, onUnmounted, ref } from 'vue'
import studentPanelService from '@/services/student/studentPanelService'

const QUIZ_STATUSES = {
  NOT_VISITED: 'not_visited',
  VISITED: 'visited',
  ANSWERED: 'answered'
}

export function useQuizAttempt() {
  const attemptId = ref('')
  const attemptState = ref(null)
  const submitting = ref(false)
  const saveError = ref('')

  const answersMap = ref({})
  const saveQueue = new Map()
  const lastSavedSnapshots = new Map()

  const buildSavePayload = (questionId, item) => ({
    question_id: String(questionId),
    selected_option: item?.selected_option ?? null,
    answer_text: item?.answer_text ?? '',
    is_flagged: Boolean(item?.is_flagged),
    status: item?.status || QUIZ_STATUSES.NOT_VISITED
  })

  const toSnapshot = (payload) => JSON.stringify(payload)

  const setAttemptState = (payload) => {
    attemptState.value = payload || null
    attemptId.value = payload?.id || ''
    answersMap.value = payload?.answers || {}

    lastSavedSnapshots.clear()
    Object.entries(answersMap.value).forEach(([questionId, answer]) => {
      const normalized = buildSavePayload(questionId, answer)
      lastSavedSnapshots.set(String(questionId), toSnapshot(normalized))
    })
  }

  const flaggedCount = computed(() =>
    Object.values(answersMap.value).filter(item => item?.is_flagged).length
  )

  const answeredCount = computed(() =>
    Object.values(answersMap.value).filter(item => item?.status === QUIZ_STATUSES.ANSWERED).length
  )

  const getQuestionState = (questionId) => {
    return answersMap.value[String(questionId)] || {
      question_id: String(questionId),
      selected_option: null,
      answer_text: '',
      is_flagged: false,
      status: QUIZ_STATUSES.NOT_VISITED
    }
  }

  const patchQuestionState = (questionId, patch) => {
    const key = String(questionId)
    const current = getQuestionState(key)
    const next = { ...current, ...patch }

    if (next.selected_option || String(next.answer_text || '').trim()) {
      next.status = QUIZ_STATUSES.ANSWERED
    }

    answersMap.value[key] = next
    return next
  }

  const flushSave = async (questionId) => {
    const key = String(questionId)
    const item = answersMap.value[key]
    if (!attemptId.value || !item) return

    const payload = buildSavePayload(key, item)
    const snapshot = toSnapshot(payload)
    if (lastSavedSnapshots.get(key) === snapshot) {
      return
    }

    try {
      await studentPanelService.autosaveQuizAnswer(attemptId.value, payload)
      lastSavedSnapshots.set(key, snapshot)
      saveError.value = ''
    } catch (error) {
      saveError.value = 'Auto-save failed. Your latest changes will retry.'
      throw error
    }
  }

  const scheduleAutosave = (questionId, delay = 400) => {
    const key = String(questionId)
    const previous = saveQueue.get(key)
    if (previous) clearTimeout(previous)

    const timeoutId = setTimeout(() => {
      flushSave(key).catch(() => {})
      saveQueue.delete(key)
    }, delay)

    saveQueue.set(key, timeoutId)
  }

  const flushAllSaves = async () => {
    const pendingIds = Array.from(saveQueue.keys())
    pendingIds.forEach((key) => {
      clearTimeout(saveQueue.get(key))
      saveQueue.delete(key)
    })

    for (const key of pendingIds) {
      await flushSave(key)
    }
  }

  const submitAttempt = async () => {
    if (!attemptId.value || submitting.value) return null

    submitting.value = true
    try {
      await flushAllSaves()
      const response = await studentPanelService.submitQuizAttemptById(attemptId.value)
      attemptState.value = response
      return response
    } finally {
      submitting.value = false
    }
  }

  onUnmounted(() => {
    saveQueue.forEach((timeoutId) => clearTimeout(timeoutId))
    saveQueue.clear()
    lastSavedSnapshots.clear()
  })

  return {
    QUIZ_STATUSES,
    attemptId,
    attemptState,
    answersMap,
    saveError,
    submitting,
    flaggedCount,
    answeredCount,
    setAttemptState,
    getQuestionState,
    patchQuestionState,
    scheduleAutosave,
    flushAllSaves,
    submitAttempt
  }
}
