import { ref } from 'vue'
import aiChatService from '@/services/shared/aiChatService'
import {
  UPLOAD_POLL_INTERVAL_MS,
  UPLOAD_POLL_MAX_ATTEMPTS,
  getProgressForAttempt,
  sleep
} from '@/utils/chatHelpers'

export function useDocumentUpload({ onAssistantNotice }) {
  const isUploading = ref(false)
  const uploadedDocument = ref(null)
  const uploadPollToken = ref(0)
  const activePollPromise = ref(null)
  const activePollFileId = ref(null)
  const activePollToken = ref(null)
  
  const waitForDocumentIndexing = async (fileId, pollToken) => {
    for (let attempt = 0; attempt < UPLOAD_POLL_MAX_ATTEMPTS; attempt += 1) {
      if (pollToken !== uploadPollToken.value || !uploadedDocument.value) {
        return { cancelled: true }
      }

      const statusRes = await aiChatService.getUploadStatus(fileId)
      const statusValue = (statusRes?.status || '').toLowerCase()
      const pollInterval = Number(statusRes?.poll_interval_ms) > 0
        ? Number(statusRes.poll_interval_ms)
        : UPLOAD_POLL_INTERVAL_MS

      if (statusValue === 'indexed') {
        return { ready: true }
      }

      if (statusValue === 'failed') {
        throw new Error('Sentence transformer indexing failed')
      }

      if (uploadedDocument.value?.status === 'uploading') {
        uploadedDocument.value.progress = getProgressForAttempt(attempt)
        uploadedDocument.value.statusText = statusValue === 'processing'
          ? 'Loading Please Wait...'
          : 'Queued for processing...'
      }

      await sleep(pollInterval)
    }

    throw new Error('Indexing timed out')
  }

  const handleUpload = async (event) => {
    const file = event?.target?.files?.[0]
    if (!file) return

    if (isUploading.value && uploadedDocument.value?.status === 'uploading') {
      if (event?.target) event.target.value = ''
      return
    }

    isUploading.value = true
    uploadPollToken.value += 1
    const currentToken = uploadPollToken.value
    
    uploadedDocument.value = {
      id: null,
      name: file.name,
      status: 'uploading',
      statusText: 'Uploading document...',
      progress: 12
    }

    try {
      const res = await aiChatService.uploadDocument(file)

      if (!res?.file_id) {
        throw new Error('Upload response missing file id')
      }

      if (currentToken !== uploadPollToken.value || !uploadedDocument.value) {
        return
      }

      uploadedDocument.value.id = res.file_id
      uploadedDocument.value.statusText = 'Queued for processing...'
      uploadedDocument.value.progress = 18

      let pollPromise = activePollPromise.value
      const canReusePoll = (
        pollPromise
        && activePollFileId.value === res.file_id
        && activePollToken.value === currentToken
      )

      if (!canReusePoll) {
        activePollFileId.value = res.file_id
        activePollToken.value = currentToken
        pollPromise = waitForDocumentIndexing(res.file_id, currentToken)
        activePollPromise.value = pollPromise
      }

      const pollResult = await pollPromise
      if (pollResult?.cancelled || currentToken !== uploadPollToken.value || !uploadedDocument.value) {
        return
      }

      uploadedDocument.value.status = 'ready'
      uploadedDocument.value.statusText = 'Ready'
      uploadedDocument.value.progress = 100
    } catch (err) {
      console.error('Upload failed', err)
      if (currentToken !== uploadPollToken.value || !uploadedDocument.value) {
        return
      }
      const backendError = err?.response?.data?.error || err?.message
      const normalizedError = String(backendError || '').toLowerCase()
      const isSizeIssue = normalizedError.includes('size') || normalizedError.includes('too large')
      uploadedDocument.value.status = 'error'
      uploadedDocument.value.statusText = isSizeIssue
        ? 'File too large. Please upload a smaller file.'
        : (backendError || 'Failed to process')
      uploadedDocument.value.progress = 100
      
      if (onAssistantNotice) {
        onAssistantNotice(
          isSizeIssue
            ? 'File upload failed because the file is too large. Please upload a smaller document and try again.'
            : 'File is not uploaded yet. Please re-upload the document before asking questions from it.'
        )
      }
      setTimeout(() => {
        if (uploadedDocument.value?.status === 'error') {
          uploadedDocument.value = null
        }
      }, 3000)
    } finally {
      if (activePollToken.value === currentToken) {
        activePollPromise.value = null
        activePollFileId.value = null
        activePollToken.value = null
      }
      isUploading.value = false
      event.target.value = '' 
    }
  }

  const removeDocument = () => {
    uploadPollToken.value += 1
    activePollPromise.value = null
    activePollFileId.value = null
    activePollToken.value = null
    isUploading.value = false
    uploadedDocument.value = null
  }

  return {
    isUploading,
    uploadedDocument,
    handleUpload,
    removeDocument,
    waitForDocumentIndexing // exposed mainly if needed externally, but mostly internal
  }
}
